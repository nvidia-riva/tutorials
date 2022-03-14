import argparse
import os

import grpc
import riva_api.riva_nlp_pb2 as rnlp
import riva_api.riva_nlp_pb2_grpc as rnlp_srv


def get_args():
    parser = argparse.ArgumentParser(description="Riva Question Answering client sample")
    parser.add_argument("--riva-uri", type=str, help="URI to access Riva server")

    return parser.parse_args()


parser = get_args()

riva_uri = parser.riva_uri
if riva_uri is None:
    if "RIVA_URI" in os.environ:
        riva_uri = os.getenv("RIVA_URI")
    else:
        riva_uri = "localhost:50051"

grpc_server = riva_uri
channel = grpc.insecure_channel(grpc_server)
riva_nlp = rnlp_srv.RivaLanguageUnderstandingStub(channel)

req = rnlp.NaturalQueryRequest()

test_context = "In 2010 the Amazon rainforest experienced another severe drought, in some ways more extreme than the 2005 drought. The affected region was approximate 1,160,000 square miles (3,000,000 km2) of rainforest, compared to 734,000 square miles (1,900,000 km2) in 2005. The 2010 drought had three epicenters where vegetation died off, whereas in 2005 the drought was focused on the southwestern part. The findings were published in the journal Science. In a typical year the Amazon absorbs 1.5 gigatons of carbon dioxide; during 2005 instead 5 gigatons were released and in 2010 8 gigatons were released."
req.query = "How many tons of carbon are absorbed the Amazon in a typical year?"

req.context = test_context
resp = riva_nlp.NaturalQuery(req)
print(resp)
