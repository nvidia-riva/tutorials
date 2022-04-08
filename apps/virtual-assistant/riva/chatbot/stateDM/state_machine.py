# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import copy
from riva.chatbot.stateDM.states import userInput, userLocationInput
from config import riva_config

verbose = riva_config["VERBOSE"]

###############################################################################
# stateDM (Simple Dialog Manager): A Finite State Machine
###############################################################################
class StateMachine:
    def __init__(self, user_conversation_index, init):
        self.uid = user_conversation_index
        self.bot = "rivaWeather"
        if verbose:
            print("[stateDM] Initializing the state machine for uid: ", self.uid)
        self.currentState = init(self.bot, self.uid)

    def execute_state(self, bot, context, text):
        # Fresh request frame
        request_data = {'context': context,
                        'text': text,
                        'uid': self.uid,
                        'payload': {}}

        # TODO: Add support for !undo (saving previous context) and !reset

        # Keep executing the state machine until a user input is required
        # i.e. stop when state is either InputUser or InputContext
        while True:
            # Run the current state
            if verbose:
                print("[stateDM] Executing state:",
                                    self.currentState.name)
            self.currentState.run(request_data)
            nextState = self.currentState.next()

            # If the next state exists
            if nextState is not None:
                # Create an object from the next state
                self.currentState = nextState(self.bot, self.uid)
                # If the next state requires user input, just return
                # WARNING: Can go into infinite loop if states don't have
                # next_state configured properly
                if nextState == userInput or nextState == userLocationInput:
                    return request_data

            # If no next state exists, wait for user input now
            else:
                if verbose:
                    print("[stateDM] No next state, waiting for user input")
                self.currentState = userInput(self.bot, self.uid)
                return request_data
