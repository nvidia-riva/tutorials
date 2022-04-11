# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from abc import ABC, abstractmethod
import sys

class State(ABC):
    """ State is an abstract class """

    def __init__(self, name, bot, uid):
        self.name = name    # Name of the state
        self.bot = bot  # Name of the chatbot eg. "rivaWeather"
        self.uid = uid
        self.next_state = None

    @abstractmethod
    def run(self, request_data):
        assert 0, "Run not implemented!"

    def next(self):
        # This should only be run after populating next_state
        return self.next_state

    def construct_message(self, request_data, text):
        """ Constructs the response frame,
        appending to a prev response if that exists """
        message = {'type': 'text',
                   'payload': {'text': text},
                   'delay': 0}

        prev_response = request_data.get('response', False)

        # If there was an old response, append the new response to the list
        if prev_response:
            prev_response.append(message)
        # Else create a list containing the response
        else:
            prev_response = [message]

        return prev_response