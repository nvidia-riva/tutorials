<img src="http://developer.download.nvidia.com/notebooks/dlsw-notebooks/riva_asr_deploy-eks/nvidia_logo.png" style="width: 90px; float: right;">

# How to Deploy Riva at Scale on Azure Cloud with AKS

This is an example of deploying and scaling Riva Speech Skills on Azure Cloud's Azure Kuberenetes Service (AKS)
with Traefik-based load balancing. It includes the following steps:
1. Creating the AKS cluster
2. Deploying the Riva API service
3. Deploying the Traefik edge router
4. Creating the IngressRoute to handle incoming requests
5. Deploying a sample client
6. Scaling the cluster

## Prerequisites

Before continuing, ensure you have:
- An Google account with the appropriate user/role privileges to manage [AKS](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- The azure command-line tool, [Configured](https://learn.microsoft.com/en-us/cli/azure/azure-cli-configuration) for your account
- Access to [NGC](https://ngc.nvidia.com/signin) and the associated [command-line](https://docs.ngc.nvidia.com/cli/) interface
- Cluster management tools [`az`](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli), [`helm`](https://helm.sh/) and [`kubectl`](https://kubernetes.io/docs/reference/kubectl/)


## Creating the AKS Cluster

The cluster contains three separate nodegroups:
- `rivaserver`:  A GPU-equipped node where the main Riva service runs. `Standard_NC8as_T4_v3` instances, each using an Tesla T4 GPU, provide good value and sufficient capacity for many applications.

- `loadbalancer`: A general-purpose compute node for the Traefik load balancer, using an `Standard_D4s_v3` instance.

- `rivaclient`: A general-purpose node with an `Standard_D8s_v3` instance for client applications accessing the Riva service

1. Create Azure Resource Group as all the resources created for AKS cluster will be part of this resource group:

    ```bash
    AKS_RESOURCE_GROUP=riva-resource
 
    # Set a unique name for your cluster.
    AKS_CLUSTER_NAME=riva-aks
    
    az group create --name ${AKS_RESOURCE_GROUP} --location eastus
    ```


 2. Create the AKS cluster, It will take some time as it will spin nodes and setup master in backend.

    ```bash
    az aks create  --resource-group  ${AKS_RESOURCE_GROUP}  --name ${AKS_CLUSTER_NAME}  --node-count 1 --generate-ssh-keys
    ```

3. Once the cluster creation is complete, Let's pull the cluster config to local machine so that kubectl can connect to the cluster:

    ```bash
    az aks get-credentials --resource-group ${AKS_RESOURCE_GROUP}  --name ${AKS_CLUSTER_NAME} --admin
    ```

4. Verify if we are able to connect cluster using kubectl, you should see nodes & pods should be running.

    ```bash
    kubectl get nodes
    kubectl get po -A
    ```

5. Create the 3 nodepools for GPU workers, Loadbalancers & Clients:

      - **GPU LINUX WORKERS:**

        ```bash
        az aks nodepool add --name rivaserver --resource-group ${AKS_RESOURCE_GROUP} --cluster-name ${AKS_CLUSTER_NAME} --node-vm-size Standard_NC8as_T4_v3 --node-count 1 --labels role=workers
        ```
      - **CPU LINUX LOADBALANCERS:**

        ```bash
        az aks nodepool add --name loadbalancer --resource-group ${AKS_RESOURCE_GROUP} --cluster-name ${AKS_CLUSTER_NAME} --node-vm-size Standard_D4s_v3 --node-count 1 --labels role=loadbalancers
        ```
      - **CPU LINUX CLIENTS:**
        ```bash
        az aks nodepool add --name rivaclient --resource-group ${AKS_RESOURCE_GROUP} --cluster-name ${AKS_CLUSTER_NAME} --node-vm-size Standard_D8s_v3 --node-count 1 --labels role=clients
        ```

6. Verify that the newly added nodes now appear in Kubernetes cluster.
    ```bash   
    kubectl get nodes --show-labels
    kubectl get nodes --selector role=workers
    kubectl get nodes --selector role=clients
    kubectl get nodes --selector role=loadbalancers
    ```



## Deploying the Riva API

The Riva Speech Skills Helm chart is designed to automate deployment to a Kubernetes cluster. After downloading the Helm chart, minor adjustments will adapt the chart to the way Riva will be used in the remainder of this tutorial.

1.  Download and untar the Riva API Helm chart. Replace `VERSION_TAG` with the specific version needed.

    ```bash
    export NGC_CLI_API_KEY=<your NGC API key>
    export VERSION_TAG="{VersionNum}"
    helm fetch https://helm.ngc.nvidia.com/nvidia/riva/charts/riva-api-${VERSION_TAG}.tgz --username='$oauthtoken' --password=$NGC_CLI_API_KEY
    tar -xvzf riva-api-${VERSION_TAG}.tgz
    ```

2.  In the `riva-api` folder, modify the following files:

    1. **`values.yaml`**

        * Set `riva.speechServices.[asr,nlp,tts]` to `true` or `false` as needed to enable or disable those services. For example, if only ASR is needed, then set the NLP and TTS values to `false`.
        * In `modelRepoGenerator.ngcModelConfigs.[asr,nlp,tts]`, comment or uncomment specific models or languages as needed.
        * Change `service.type` from `LoadBalancer` to `ClusterIP`. This directly exposes the service only to other services within the cluster, such as the proxy service to be installed below.
        * Set `persistentVolumeClaim.usePVC` to `true` , `persistentVolumeClaim.storageClassName` to `azurefile` , `persistentVolumeClaim.storageAccessMode` to `ReadWriteOnce`, This will store the riva models in Created Persistent Volume.

    
    2. **`templates/deployment.yaml`**

        * Add a node selector constraint to ensure that Riva is only deployed on the correct GPU resources. In `spec.template.spec`, add:
          
          ```yaml
          nodeSelector:
            kubernetes.azure.com/agentpool: rivaserver
          ```

4. Install nvidia gpu device plugin, Azure will not install it by default, Verify the installation with the following command:
    ```bash
    helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
    helm repo update
    helm install \
        --generate-name \
        --set failOnInitError=false \
        nvdp/nvidia-device-plugin
    ```

5. Verify the gpu plugin installation:
    ```bash
    kubectl get pod -A | grep nvidia
                       
                       or
 
    kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
    ```

4. Ensure you are in a working directory with `riva-api` as a subdirectory, then install the Riva Helm chart. You can explicitly override variables from the `values.yaml` file, such as the `riva.speechServices.[asr,nlp,tts]` settings.

    ```bash
    helm install riva-api riva-api/ \
        --set ngcCredentials.password=`echo -n $NGC_CLI_API_KEY | base64 -w0` \
        --set modelRepoGenerator.modelDeployKey=`echo -n tlt_encode | base64 -w0` \
        --set riva.speechServices.asr=true \
        --set riva.speechServices.nlp=true \
        --set riva.speechServices.tts=true
    ```

5. The Helm chart runs two containers in order: a `riva-model-init` container that downloads and deploys the models, followed by a `riva-speech-api` container to start the speech service API. Depending on the number of models, the initial model deployment could take an hour or more. To monitor the deployment, use `kubectl` to describe the `riva-api` pod and to watch the container logs.
    ```bash
    export pod=`kubectl get pods | cut -d " " -f 1 | grep riva-api`
    kubectl describe pod $pod

    kubectl logs -f $pod -c riva-model-init
    kubectl logs -f $pod -c riva-speech-api
    ```

## Deploying the Traefik edge router

Now that the Riva service is running, the cluster needs a mechanism to route requests into Riva.

In the default `values.yaml` of the `riva-api` Helm chart, `service.type` was set to `LoadBalancer`, which would have automatically created an AWS Classic Load Balancer to direct traffic into the Riva service. Instead, the open-source [Traefik](https://doc.traefik.io/traefik/) edge router will serve this purpose.

1.  Download and untar the Traefik Helm chart.

    ```bash
    helm repo add traefik https://helm.traefik.io/traefik
    helm repo update
    helm fetch traefik/traefik
    tar -zxvf traefik-*.tgz
    ```

2.  Modify the `traefik/values.yaml` file.

    1. Change `service.type` from `LoadBalancer` to `ClusterIP`. This exposes the service on a cluster-internal IP.

    2. Set `nodeSelector` to `{  Kubernetes.azure.com/agentpool: loadbalancer}`. Similar to what you did for the Riva API service,
    this tells the Traefik service to run on the `loadbalancer` nodepool.

3.  Deploy the modified `traefik` Helm chart.
    ```bash
    helm install traefik traefik/
    ```

## Creating the IngressRoute

  An [IngressRoute](https://doc.traefik.io/traefik/routing/providers/kubernetes-crd/) enables the Traefik load balancer to
  recognize incoming requests and distribute them across multiple `riva-api` services.
  
  When you deployed the `traefik` Helm chart above, Kubernetes automatically created a local DNS entry for that service: `traefik.default.svc.cluster.local`. The IngressRoute definition below matches these DNS entries and directs requests to the `riva-api` service. You can modify the entries to support a different DNS arrangement, depending on your requirements.

  1. Create the following `riva-ingress.yaml` file:

      ```yaml
      apiVersion: traefik.containo.us/v1alpha1
      kind: IngressRoute
      metadata:
        name: riva-ingressroute
      spec:
        entryPoints:
          - web
        routes:
          - match: "Host(`traefik.default.svc.cluster.local`)"
            kind: Rule
            services:
              - name: riva-api
                port: 50051
                scheme: h2c
      ```

  2. Deploy the IngressRoute.
      ```bash
      kubectl apply -f riva-ingress.yaml
      ```

The Riva service is now able to serve gRPC requests from within the cluster at the address `traefik.default.svc.cluster.local`. If you are planning to deploy your own client application in the cluster to communicate with Riva, you can send requests to that address. In the next section, you will deploy a Riva sample client and use it to test the deployment.

## Deploying a Sample Client

Riva provides a container with a set of pre-built sample clients to test the Riva services. The [clients](https://github.com/nvidia-riva/cpp-clients) are also available on GitHub for those interested in adapting them.

1.  Create the `client-deployment.yaml` file that defines the deployment and contains the following:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: riva-client
      labels:
        app: "rivaasrclient"
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: "rivaasrclient"
      template:
        metadata:
          labels:
            app: "rivaasrclient"
        spec:
          nodeSelector:
              kubernetes.azure.com/agentpool: rivaclient
          imagePullSecrets:
          - name: imagepullsecret
          containers:
          - name: riva-client
            image: "nvcr.io/{NgcOrgTeam}/riva-speech-client:{VersionNum}"
            command: ["/bin/bash"]
            args: ["-c", "while true; do sleep 5; done"]
    ```
2.  Deploy the client service.
    ```bash
    kubectl apply -f client-deployment.yaml
    ```

3.  Connect to the client pod.
    ```bash
    export cpod=`kubectl get pods | cut -d " " -f 1 | grep riva-client`
    kubectl exec --stdin --tty $cpod /bin/bash
    ```

4.  From inside the shell of the client pod, run the sample ASR client on an example `.wav` file. Specify the `traefik.default.svc.cluster.local` endpoint, with port 80, as the service address.
    ```bash
    riva_streaming_asr_client \
       --audio_file=/work/wav/sample.wav \
       --automatic_punctuation=true \
       --riva_uri=traefik.default.svc.cluster.local:80
    ```

## Scaling the cluster

As deployed above, the AKS cluster only provisions a single GPU node, although we can scale the nodes. While a single GPU can handle a [large volume of requests](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-performance.html), the cluster can easily be scaled with more nodes.

1. Scale the GPU nodepool to the desired number of compute nodes (2 in this case).
    ```bash
    az aks nodepool scale --name rivaserver --resource-group ${AKS_RESOURCE_GROUP} --cluster-name ${AKS_CLUSTER_NAME} --node-count 2

    ```

2. Scale the `riva-api` deployment to use the additional nodes.
    ```bash
    kubectl scale deployments/riva-api --replicas=2
    ```

As with the original `riva-api` deployment, each replica pod downloads and initializes the necessary models prior to starting the Riva service.
