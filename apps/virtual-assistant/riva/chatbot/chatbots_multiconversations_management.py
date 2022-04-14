# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from riva.chatbot.chatbot import ChatBot

userbots = {}
user_conversation_cnt = 0


def create_chatbot(user_conversation_index, sio, verbose=False):
    if user_conversation_index not in userbots:
        userbots[user_conversation_index] = ChatBot(user_conversation_index,
                                                                verbose=verbose)
        userbots[user_conversation_index].start_asr(sio)
        if verbose:
            print('[Riva Chatbot] Chatbot created with user conversation index:' +
                                    f'[{user_conversation_index}]')


def get_new_user_conversation_index():
    global user_conversation_cnt
    user_conversation_cnt += 1
    user_conversation_index = user_conversation_cnt
    return str(user_conversation_index)


def get_chatbot(user_conversation_index):
    if user_conversation_index in userbots:
        return userbots[user_conversation_index]
    else:
        return None
