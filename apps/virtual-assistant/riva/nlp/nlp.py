# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import riva_api.riva_nlp_pb2 as rnlp
import riva_api.riva_nlp_pb2_grpc as rnlp_srv

import grpc
from config import riva_config, nlp_config
import requests
import json

# QA api-endpoint
QA_API_ENDPOINT = nlp_config["QA_API_ENDPOINT"]
enable_qa = riva_config["ENABLE_QA"]
verbose = riva_config["VERBOSE"]

channel = grpc.insecure_channel(riva_config["RIVA_SPEECH_API_URL"])
riva_nlp = rnlp_srv.RivaLanguageUnderstandingStub(channel)


def get_qa_answer(context, question, p_threshold):
    # if hasattr(resp, 'intent'):
    #     entities['intent'] = resp.intent.class_name

    # data to be sent to api
    data = {
        "question": question,
        "context": context
    }
    # sending post request and saving response as response object
    r = requests.post(QA_API_ENDPOINT, json=data)

    # extracting response text
    qa_resp = json.loads(r.text)
    # print("The response from QA server is :%s"%qa_response)

    if verbose:
        print("[Riva NLU] The answer is :%s" % qa_resp['result'])
        print("[Riva NLU] The probability is :%s" % qa_resp['p'])

        if qa_resp['result'] == '':
            print("[Riva NLU] QA returned empty string.")

        if qa_resp['p'] < p_threshold:
            print("[Riva NLU] QA response lower than threshold - ", p_threshold)
            # qa_resp['result'] = "I am not too sure about what you meant. " + qa_resp['result']
            # return qa_resp

    return qa_resp


if enable_qa == "true":
    # test question and passage to be sent to api
    riva_test = "I am Riva. I can talk about the weather. My favorite season is spring. I know the weather info " \
                  "from Weatherstack api. I have studied the weather all my life."
    test_question = "What is your name?"
    p_threshold = 0.4
    get_qa_answer(riva_test, test_question, p_threshold)


def get_intent(resp, entities):
    if hasattr(resp, 'intent'):
        entities['intent'] = resp.intent.class_name


def get_slots(resp, entities):
    entities['payload'] = dict()            
    all_entities_class = {}
    all_entities = []
    if hasattr(resp, 'slots'):
        for i in range(len(resp.slots)):
            slot_class = resp.slots[i].label[0].class_name.replace("\r", "")
            token = resp.slots[i].token.replace("?", "").replace(",", "").replace(".", "").replace("[SEP]", "").strip()
            score = resp.slots[i].label[0].score
            if slot_class and token:
                if slot_class == 'weatherplace' or slot_class == 'destinationplace':
                    entity = { "value": token,
                                "confidence": score,
                                "entity": "location" }
                else:
                    entity = { "value": token,
                                "confidence": score,
                                "entity": slot_class }
                all_entities_class[entity["entity"]] = 1
                all_entities.append(entity)
    for cl in all_entities_class:
        partial_entities = list(filter(lambda x: x["entity"] == cl, all_entities))
        partial_entities.sort(reverse=True, key=lambda x: x["confidence"])
        for entity in partial_entities: 
            if cl == "location":
                entities['location'] = entity["value"]
            else:    
                entities['payload'][cl] = entity["value"]
            break


def get_riva_output(text):
    # Submit an AnalyzeIntentRequest. We do not provide a domain with the query, so a domain
    # classifier is run first, and based on the inferred value from the domain classifier,
    # the query is run through the appropriate intent/slot classifier
    # Note: the detected domain is also returned in the response.
    try:
        req = rnlp.AnalyzeIntentRequest()
        req.query = str(text)
        # The <domain_name> is appended to "riva_intent_" to look for a model "riva_intent_<domain_name>"
        # So the model "riva_intent_<domain_name>" needs to be preloaded in riva server.
        # In this case the domain is weather and the model being used is "riva_intent_weather-misc".
        req.options.domain = "weather"
        resp = riva_nlp.AnalyzeIntent(req)
    except Exception as inst:
        # An exception occurred
        print("[Riva NLU] Error during NLU request")
        return {'riva_error': 'riva_error'}
    entities = {}
    get_intent(resp, entities)
    get_slots(resp, entities)
    if 'location' not in entities:
        if verbose:
            print(f"[Riva NLU] Did not find any location in the string: {text}\n"
                    "[Riva NLU] Checking again using NER model")
        try:
            req = rnlp.TokenClassRequest()
            req.model.model_name = "riva_ner"
            req.text.append(text)
            resp_ner = riva_nlp.ClassifyTokens(req)
        except Exception as inst:
            # An exception occurred
            print("[Riva NLU] Error during NLU request (riva_ner)")
            return {'riva_error': 'riva_error'}

        if verbose:
            print(f"[Riva NLU] NER response results: \n {resp_ner.results[0].results}\n")
            print("[Riva NLU] Location Entities:")
        loc_count = 0
        for result in resp_ner.results[0].results:
            if result.label[0].class_name == "LOC":
                if verbose:
                    print(f"[Riva NLU] Location found: {result.token}") # Flow unhandled for multiple location input
                loc_count += 1
                entities['location'] = result.token
        if loc_count == 0:
            if verbose:
                print("[Riva NLU] No location found in string using NER LOC")
                print("[Riva NLU] Checking response domain")
            if resp.domain.class_name == "nomatch.none":
                # as a final resort try QA API
                if enable_qa == "true":
                    if verbose:
                        print("[Riva NLU] Checking using QA API")
                    riva_misty_profile = requests.get(nlp_config["RIVA_MISTY_PROFILE"]).text # Live pull from Cloud
                    qa_resp = get_qa_answer(riva_misty_profile, text, p_threshold)
                    if not qa_resp['result'] == '':
                        if verbose:
                            print("[Riva NLU] received qa result")
                        entities['intent'] = 'qa_answer'
                        entities['answer_span'] = qa_resp['result']
                        entities['query'] = text
                    else:
                        entities['intent'] = 'riva_error'
                else:
                    entities['intent'] = 'riva_error'
    if verbose:
        print("[Riva NLU] This is what entities contain: ", entities)
    return entities


def get_riva_output_qa_only(text):
    # Submit an AnalyzeIntentRequest. We do not provide a domain with the query, so a domain
    # classifier is run first, and based on the inferred value from the domain classifier,
    # the query is run through the appropriate intent/slot classifier
    # Note: the detected domain is also returned in the response.

    entities = {}
    try:
        if enable_qa == "true":
            if verbose:
                print("[Riva NLU] Checking using QA API")
            riva_mark_KB = requests.get(nlp_config["RIVA_MARK_KB"]).text  # Live pull from Cloud
            qa_resp = get_qa_answer(riva_mark_KB, text, p_threshold)
            if not qa_resp['result'] == '':
                if verbose:
                    print("[Riva NLU] received qa result")
                entities['intent'] = 'qa_answer'
                entities['answer_span'] = qa_resp['result']
                entities['query'] = text
            else:
                entities['intent'] = 'riva_error'
        else:
            entities['intent'] = 'riva_error'
    except Exception as inst:
        # An exception occurred
        print("[Riva NLU] Error during NLU request")
        return {'riva_error': 'riva_error'}
    if verbose:
        print("[Riva NLU] This is what entities contain: ", entities)
    return entities


def get_entities(text, nlp_type):
    if nlp_type is None:
        nlp_type = "empty"

    ent_out = {}
    if nlp_type == "empty":
        ent_out.update({'raw_text': str(text)})
    elif nlp_type == "riva":
        riva_out = get_riva_output(text)
        ent_out.update(riva_out)
    elif nlp_type == "riva_mark":
        riva_out = get_riva_output_qa_only(text)
        ent_out.update(riva_out)
    return ent_out
