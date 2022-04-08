# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from client.webapplication.server.server import *
from config import client_config
     
def start_web_application():
    port = client_config["PORT"]
    host = "0.0.0.0"
    ssl_context = ('client/webapplication/cert.pem', 'client/webapplication/key.pem')
    print("Server starting at : https://" + str(host) + ":" + str(port) + "/rivaWeather")
    print("***Note: Currently the streaming is working with Chrome and FireFox, Safari does not support navigator.mediaDevices.getUserMedia***")
    sio.run(app, host=host, port=port, debug=False, use_reloader=False, ssl_context=ssl_context)
