# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

client_config = {
    "CLIENT_APPLICATION": "WEBAPPLICATION", # Default and only config value for this version
    "PORT": 8009, # The port your flask app will be hosted at
    "DEBUG": True, # When this flag is set, the UI displays detailed Riva data
    "VERBOSE": True  # print logs/details for diagnostics
}

riva_config = {
    "RIVA_SPEECH_API_URL": "localhost:50051", # Replace the IP & port with your hosted Riva endpoint
    "ENABLE_QA": "QA unavailable in this VA version. Coming soon",
    "WEATHERSTACK_ACCESS_KEY": "",  # Get your access key at - https://weatherstack.com/
    "VERBOSE": True  # print logs/details for diagnostics
}

asr_config = {
    "VERBOSE": True,
    "SAMPLING_RATE": 16000,
    "LANGUAGE_CODE": "en-US",  # a BCP-47 language tag
    "ENABLE_AUTOMATIC_PUNCTUATION": True,
}

nlp_config = {
    "RIVA_MISTY_PROFILE": "http://docs.google.com/document/d/17HJL7vrax6FiF1zW_Vzqk9FTfmATeq5i3UemtagM8RY/export?format=txt", # URL for the Riva meta info file.
    "RIVA_MARK_KB": "http://docs.google.com/document/d/1LeRphIBOo5UyyUcr45ewvg16sCVNqP_H3SdFTB74hck/export?format=txt", # URL for Mark's GPU History doc file.    
    "QA_API_ENDPOINT": "QA unavailable in this VA version. Coming soon", # Replace the IP port with your Question Answering API
}

tts_config = {
    "VERBOSE": False,
    "SAMPLE_RATE": 22050,
    "LANGUAGE_CODE": "en-US",  # a BCP-47 language tag
    "VOICE_NAME": "English-US-Female-1", # Options are English-US-Female-1 and English-US-Male-1
}
