# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from riva.chatbot.stateDM.state import State
from riva.nlp.nlp import get_entities
from riva.chatbot.stateDM.state_data import intent_transitions
from riva.chatbot.stateDM.Weather import Weather
import sys
from config import riva_config

verbose = riva_config["VERBOSE"]


class initialState(State):
    def __init__(self, bot, uid):
        super(initialState, self).__init__("initialState", bot, uid)

    def run(self, request_data):
        text = "Hi, welcome to Riva weather service. How may I help you?"

        # Update response with welcome text
        request_data.update({'response':
                            self.construct_message(request_data, text)})

        self.next_state = userInput


class userInput(State):
    def __init__(self, bot, uid):
        super(userInput, self).__init__("userInput", bot, uid)
        self.next_state = None

    def get_state(self, class_str, default):
        return getattr(sys.modules[__name__], class_str, default)

    def run(self, request_data):
        # Get response from Riva NLU
        response = get_entities(request_data['text'], "riva")
        response_intent = response.get('intent', False)

        # Fetch the transitions dict for the bot
        intents_project = intent_transitions[self.bot]

        # If a valid intent was detected
        if response_intent:
            # If a valid state exists for the response intent AND
            # the response intent is different from the one already in context
            if intents_project.get(response_intent, False) and \
                    response_intent != request_data['context'].get('intent', False):
                self.next_state = self.get_state(intents_project.get(response_intent, False), None)

                # update request_data with response and next_state
                request_data['context'].update(response)
                return

        # If intent exists in the context, use that
        if 'intent' in request_data['context']:
            # Populate context with response (eg. new entity location value), except the intent
            request_data['context'].update({x: response[x] for x in response if x not in 'intent'})
            self.next_state = self.get_state(intents_project.get(request_data['context']['intent'], False), None)
            return


class userLocationInput(State):
    def __init__(self, bot, uid):
        super(userLocationInput, self).__init__("userLocationInput", bot, uid)

    def run(self, request_data):
        response = get_entities(request_data['text'], "riva")

        # Updates all keys except intent
        request_data['context'].update(
            {x: response[x] for x in response if x not in 'intent'})

        # Check if the required entities (location here) are present
        # If present, proceed to Weather State
        if 'location' in response:
            # Move to Weather State
            self.next_state = Weather
        else:
            # Else, proceed to ErrorState
            self.next_state = error


class checkWeatherLocation(State):
    def __init__(self, bot, uid):
        super(checkWeatherLocation, self).__init__(
                            "checkWeatherLocation", bot, uid)

    def run(self, request_data):
        # Check if all entities (location) required for informing weather exists
        location = request_data['context'].get("location", False)

        if location:
            # If location exists, then call Weather class to check the weather location
            self.next_state = Weather
        else:
            # If not, then asks location and moves to userLocationInput to fetch it
            text = "For which location?"

            # Update response asking the user location, intent stays the same
            request_data.update({'response':
                                 self.construct_message(request_data, text)})

            self.next_state = userLocationInput


class error(State):
    def __init__(self, bot, uid):
        super(error, self).__init__("error", bot, uid)

    def run(self, request_data):
        text = "Sorry, I couldn't get you!"

        # Update response with error text
        request_data.update({'response':
                             self.construct_message(request_data, text)})

        self.next_state = userInput


# TODO: This state is not in use currently,
# add this if end of conversation is required
class end(State):
    def __init__(self, bot, uid):
        super(end, self).__init__("end", bot, uid)

    def run(self, request_data):
        text = "Bye!"

        # Update response with end state text
        request_data.update({'response':
                             self.construct_message(request_data, text)})

        self.next_state = userInput
