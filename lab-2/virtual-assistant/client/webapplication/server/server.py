# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from __future__ import division

import uuid
import time
from flask import Flask, jsonify, send_from_directory, Response, request, logging
from flask_cors import CORS
from flask import stream_with_context
from flask_socketio import SocketIO, emit
from os.path import dirname, abspath, join, isdir
from os import listdir
from config import client_config
from engineio.payload import Payload

from riva_local.chatbot.chatbots_multiconversations_management import create_chatbot, get_new_user_conversation_index, get_chatbot

''' Flask Initialization 
'''
app = Flask(__name__)
cors = CORS(app)
log = logging.logging.getLogger('werkzeug')
log.setLevel(logging.logging.ERROR)
Payload.max_decode_packets = 500  # https://github.com/miguelgrinberg/python-engineio/issues/142
sio = SocketIO(app, logger=False)
verbose = client_config['VERBOSE']

# Methods to show client
@app.route('/rivaWeather/')
def get_bot1():
    return send_from_directory("../ui/", "index.html")

@app.route('/rivaWeather/<file>', defaults={'path': ''})
@app.route('/rivaWeather/<path:path>/<file>')
def get_bot2(path, file):
    return send_from_directory("../ui/" + path, file)


@app.route('/get_new_user_conversation_index')
def get_newuser_conversation_index():
    return get_new_user_conversation_index()

# Audio source for TTS
@app.route('/audio/<int:user_conversation_index>/<int:post_id>')
def audio(user_conversation_index, post_id):
    if verbose:
        print(f'[{user_conversation_index}] audio speak: {post_id}')
    currentChatbot = get_chatbot(user_conversation_index)
    return Response(currentChatbot.get_tts_speech())

# Handles ASR audio transcript output
@app.route('/stream/<int:user_conversation_index>')
def stream(user_conversation_index):
    @stream_with_context
    def audio_stream():
        currentChatbot = get_chatbot(user_conversation_index)
        if currentChatbot:
            asr_transcript = currentChatbot.get_asr_transcript()
            for t in asr_transcript:
                yield t
        params = {'response': "Audio Works"}
        return params
    return Response(audio_stream(), mimetype="text/event-stream")


# Used for sending messages to the bot
@app.route( "/", methods=['POST'])
def get_input():
    try:
        text = request.json['text']
        context = request.json['context']
        bot = request.json['bot'].lower()
        payload = request.json['payload']
        user_conversation_index = request.json['user_conversation_index']
    except KeyError:
        return jsonify(ok=False, message="Missing parameters.")
    if user_conversation_index:
        create_chatbot(user_conversation_index, sio, verbose=client_config['VERBOSE'])
        currentChatBot = get_chatbot(user_conversation_index)
        try:
            response = currentChatBot.stateDM.execute_state(
                bot, context, text)

            if client_config['DEBUG']:
                print(f"[{user_conversation_index}] Response from RivaDM: {response}")
            
            for resp in response['response']:
                speak = resp['payload']['text']
                if len(speak):
                    currentChatBot.tts_fill_buffer(speak)
            return jsonify(ok=True, messages=response['response'], context=response['context'],
                           session=user_conversation_index, debug=client_config["DEBUG"])
        except Exception as e:  # Error in execution

            print(e)
            return jsonify(ok=False, message="Error during execution.")
    else:
        print("user_conversation_index not found")
        return jsonify(ok=False, message="user_conversation_index not found")


# Writes audio data to ASR buffer
@sio.on('audio_in', namespace='/')
def receive_remote_audio(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.asr_fill_buffer(data["audio"])


@sio.on('start_tts', namespace='/')
def start_tts(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.start_tts()


@sio.on('stop_tts', namespace='/')
def stop_tts(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.stop_tts()


@sio.on('pause_asr', namespace='/')
def pauseASR(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        if verbose:
            print(f"[{data['user_conversation_index']}] Pausing ASR requests.")
        currentChatbot.pause_asr()
        

@sio.on('unpause_asr', namespace='/')
def unpauseASR(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        if verbose:
            print(f"[{data['user_conversation_index']}] Attempt at Unpausing ASR requests on {data['on']}.")
        unpause_asr_successful_flag = currentChatbot.unpause_asr(data["on"])
        if unpause_asr_successful_flag == True:
            emit('onCompleteOf_unpause_asr', {'user_conversation_index': data["user_conversation_index"]}, broadcast=False)


@sio.on('pause_wait_unpause_asr', namespace='/')
def pause_wait_unpause_asr(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.pause_wait_unpause_asr()
        emit('onCompleteOf_unpause_asr',  {'user_conversation_index': data["user_conversation_index"]}, broadcast=False)


@sio.on("connect", namespace="/")
def connect():
    if verbose:
        print('[Riva Chatbot] Client connected')


@sio.on("disconnect", namespace="/")
def disconnect():
    if verbose:
        print('[Riva Chatbot] Client disconnected')
