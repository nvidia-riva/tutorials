<img src="http://developer.download.nvidia.com/notebooks/dlsw-notebooks/riva_asr_deploy-eks/nvidia_logo.png" style="width: 90px; float: right;">

# How to Deploy Riva at Scale on OCI with OKE

This is an example of deploying Riva Speech Skills on Oracle Cloud Infrastructure (OCI) Oracle Container Engine for Kubernetes (OKE)
with Traefik-based load balancing. It includes the following steps:
1. Creating the OKE cluster
2. Deploying the Riva API service
3. Deploying the Traefik edge router
4. Creating the IngressRoute to handle incoming requests
5. Deploying a sample client
6. Scaling the cluster

## Prerequisites

Before continuing, ensure you have:
- An OCI account with the appropriate user/role privileges to manage [OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm)
- The [OCI command-line tool](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm#Quickstart), configured for your account
- Access to [NGC](https://ngc.nvidia.com/signin) and the associated [command-line](https://ngc.nvidia.com/setup/installers/cli) interface
- Cluster management tools [`helm`](https://helm.sh/docs/intro/install/) and [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
- An [API Signing Key Pair](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#two) to enable an ssh connection to the Kubernetes worker nodes

## Creating the OKE Cluster

Navigate and sign in to the [OCI webpage](https://www.oracle.com/cloud/). Go to the hamburger menu on the top left. Under the Developer Services tab, navigate to Kubernetes Clusters (OKE).

On the left hand side make sure you are in the compartment with the appropriate privileges. Click ‘Create cluster’ to start the cluster creation. There will be two options for creating a Kubernetes Cluster: *Quick create* or *Custom create*. To make this tutorial as simple as possible, we will be using the *Quick create* option.

After selecting the *Quick create* option, you can customize the cluster shape, number of nodes, etc. 

> **Note**
>  You may want to increase the boot volume for each node or the Riva pods will not start up. For this example we increased it to 500 GB. You can specify this during cluster creation by clicking ‘Show advanced options’, checking the ‘Specify a custom boot volume size’, and typing in your desired boot volume size.

> **Note**
>  For testing purposes the worker nodes in this example were created as ‘Public workers’ to `ssh` into the nodes easily. The shape of the worker nodes tested in this example included 2 GPU Nodes of shape `VM.GPU3.1`.

The ideal cluster configuration for this example includes: 
- A GPU-equipped node where the main Riva service will run. 
- A general-purpose compute node for the Traefik load balancer.
- Another general-purpose node for client applications accessing the Riva service. 

Since we are using the *Quick create* option, we can only choose the shape for one node pool initially. A node pool is a group of nodes within a cluster that all have the same configuration. You will be able to [add more node pools](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengscalingclusters.htm) once you create the cluster. After reviewing the resources, click ‘Create cluster.’ It’ll take around 15 min for the cluster creation to complete.

> **Note**
>  Once you click the ‘Create cluster’ button, it may say that the cluster is active, but it won't actually be ready until the node pool status is active..

To access the cluster locally, navigate to the OKE page and click on the cluster name. From there press 'Access Cluster' and then 'Local Access'. From there you can follow the prompts to get local access to the cluster.

You can verify the cluster creation on the OCI Console by navigating to ‘Kubernetes Clusters (OKE)’ under ‘Developer Services’. You will see your cluster name on the webpage. You can go to the 'Instances' section, to see your worker node instances.

Verify that the nodes now appear in Kubernetes. If so, the cluster was successfully created and you can access the cluster locally.

  ```bash
    cat .kube/config
    kubectl get pods -A
    kubectl get nodes
  ```

### Tips

- To `ssh` into a worker node, you will need the private key you downloaded when you created an API Signing Key Pair. You can `ssh` into each worker node by using the IP address and hostname. You can find the IP Address and hostname by going to the Console and clicking on each instance you want to access.

  ```bash
    chmod 600 private_key.key
    ssh -i private_key.key opc@ip_address
  ```


-  If a compute instance is created with a boot volume that is greater than or equal to 50 GB, the instance does not automatically use the entire volume. Use the `oci-growfs` utility to expand the root partition to fully utilize the allocated boot volume size. You'll want to ssh into each worker node and run the following commands:

    ```bash
      sudo /usr/libexec/oci-growfs -y
      sudo systemctl restart kubelet
    ```

    If you are seeing an 'Unable to expand /dev/sda3', go to the OCI console and click hamburger menu on the top left. Under the Storage tab, navigate to 'Block Storage' and click on 'Boot Volumes' on the left hand column. From here you can click on each boot volume associated with a worker node and click 'Edit'. Change the volume size in the window that just opened and click Save Changes. A message will pop up with rescan commands. You will need to ssh into each worker node and input the rescan commands given. From there you can run the `oci-growfs` commands above.

- When accessing the cluster for the first time, any GPU nodes that you create will be tainted by default to make sure that pods are not scheduled onto inappropriate nodes (non-gpu loads should not be scheduled on gpu nodes). With a node taint, no pod will be able to schedule onto that node unless you either remove the taint or add a matching toleration. If you run `kubectl get pods -A ` and see that the CoreDNS pod is not running, this is usually due to a taint on the node.

  To remove the taint:

  ```
  kubectl taint nodes node1 nvidia.com/gpu=value1:NoSchedule-
  ```

  To add a matching toleration:

  ```yaml
    tolerations:
    - key: "nvidia.com/gpu"
      operator: "Equal"
      value: "value1"
      effect: "NoSchedule"
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

2.  In the `riva-api` folder, modify the following file:

    - **`values.yaml`**

        * Set `riva.speechServices.[asr,nlp,tts]` to `true` or `false` as needed to enable or disable those services. For example, if only ASR is needed, then set the NLP and TTS values to `false`.
        * In `modelRepoGenerator.ngcModelConfigs.[asr,nlp,tts]`, comment or uncomment specific models or languages as needed.
        * Change `service.type` from `LoadBalancer` to `ClusterIP`. This directly exposes the service only to other services within the cluster, such as the proxy service to be installed below.
    
3. Enable the cluster to run containers needing NVIDIA GPUs using the nvidia device plugin:

    ```bash
    helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
    helm repo update
    helm install \
        --namespace nvidia-device-plugin \
        --create-namespace nvidia-device-plugin \
        --set failOnInitError=false \
        nvdp/nvidia-device-plugin
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

In the default `values.yaml` of the `riva-api` Helm chart, `service.type` was set to `LoadBalancer`, which would have created an OCI Load Balancer to direct traffic into the Riva service. Instead, the open-source [Traefik](https://doc.traefik.io/traefik/) edge router will serve this purpose.

1.  Download and untar the Traefik Helm chart.

    ```bash
    helm repo add traefik https://helm.traefik.io/traefik
    helm repo update
    helm fetch traefik/traefik
    tar -zxvf traefik-*.tgz
    ```

2.  Modify the `traefik/values.yaml` file.

    Change `service.type` from `LoadBalancer` to `ClusterIP`. This exposes the service on a cluster-internal IP.

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

1.  Create the `client-deployment.yaml` file that defines the deployment. For the image path, check out [NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/riva/containers/riva-speech-client) for the latest tag:
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

As deployed above, the OKE cluster only provisions a single GPU node, although the given configuration permits up to 8 nodes. While a single GPU can handle a [large volume of requests](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/asr/asr-performance.html), the cluster can easily be scaled with more nodes.

1. Scale the GPU nodegroup to the desired number of compute nodes (4 in this case) through the [Console](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengscalingnodepools.htm#contengscalingnodepools)

2. Scale the `riva-api` deployment to use the additional nodes.
    ```bash
    kubectl scale deployments/riva-api --replicas=4
    ```

As with the original `riva-api` deployment, each replica pod downloads and initializes the necessary models prior to starting the Riva service.
