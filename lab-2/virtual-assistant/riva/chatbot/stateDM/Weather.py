# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from riva.chatbot.stateDM.state import State
from riva.chatbot.stateDM.Util import WeatherService

DEFAULT_MESSAGE = "Unfortunately the weather service is not available at this time. Check your connection to weatherstack.com, set a different API key in your configuration or else try again later."

# rules
replacement_rules = {"what's": "what is", "who's": "who is", "?": ""}
starting_phrases = ["tell me", "can you", "please"]
relation_words = ["from"]
question_words = ["what", "why", "who", "how old", "how long", "how", "do", "does", "where"]
verb_words = ["is", "are", "do", "does"]
belonging_word_convertor = {"my": "your", "your": "my", "yours": "my", "you": "i", "i" : "you",
                            "can you": "i can", "could you": "i could", "have you": "i have"}


# Function that extends the precise answer based on the question
def extend_answer(question, answer):
    print(question + " (" + answer + ") => ", end = " ")

    # Heuristics for long factual answer, where there is no need to copy question into the answer
    if len(answer.split()) >= 5:
        return answer

    # move to lower case
    question = question.lower()

    # extend shortcuts in the question word and remove question sign
    for key in replacement_rules:
        question = question.replace(key, replacement_rules[key])

    # find possible relation word, like "from"
    relation_word = None
    for word in relation_words:
        if question.startswith(word):
            relation_word = word
            question = question[len(word) + 1:]
            break

    # find starting question word
    question_word = None
    for word in question_words:
        if question.startswith(word):
            question_word = word
            question = question[len(word)+1:]
            break

    # Try to find possible relation word like "from" for a second fime in case they are coming after the question
    if relation_word is None:
        for word in relation_words:
            if question.startswith(word):
                relation_word = word
                question = question[len(word) + 1:]
                break

    # in this case you do not add question to the answer
    if question_word is None:
        return answer

    # find starting verb word
    verb_word = None
    for word in verb_words:
        if question.startswith(word):
            if word != "do" and word != "does":
                if word == "are":
                    verb_word = "am"
                else:
                    verb_word = word
            question = question[len(word) + 1:]
            break

    # check if a phrase start with a belonging word that should be converted to the opposite one
    for key in belonging_word_convertor:
        if question.startswith(key):
            question = question.replace(key, belonging_word_convertor[key])
            break

    # create full answer
    full_answer = question

    if relation_word is not None:
        full_answer += " " + relation_word

    if verb_word is not None:
        full_answer += " " + verb_word

    full_answer += " " + answer

    # Capitalize the first letter
    full_answer = full_answer[0].upper() + full_answer[1:]

    return full_answer


class Weather(State):
    def __init__(self, bot, uid):
        super(Weather, self).__init__("Weather", bot, uid)
        self.next_state = None

    def weather(self, ws, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """It is {} in {} at the moment. The temperature is {} degrees, the humidity is {} percent and the wind speed is {} miles per hour.""".format(
                response['condition'], response['city'], response['temperature_c'], response['humidity'], response['wind_mph'])
        return DEFAULT_MESSAGE

    # NOTE: weather forecast and weather historical are paid options in weatherstack
    # forecast and historical methods here return the current data only for now.
    def weather_forecast(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} it'll be {} in {}. The temperature will be {} degrees, the humidity {} percent """.format(
                request_data['context']['time'].capitalize(), response['condition'], response['city'], response['temperature_c'], response['humidity'])
        return DEFAULT_MESSAGE

    def weather_historical(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} it was {} in {}. The temperature was {} degrees, the humidity {} percent """.format(
                request_data['context']['time'].capitalize(), response['condition'], response['city'], response['temperature_c'], response['humidity'])
        return DEFAULT_MESSAGE

    def temperature(self, ws, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """The temperature is {} degrees in {} at the moment.""".format(
                response['temperature_c'], response['city'])
        return DEFAULT_MESSAGE

    def temperature_forecast(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} the temperature will be {} degrees in {}.""".format(
                request_data['context']['time'].capitalize(), response['temperature_c'], response['city'])
        return DEFAULT_MESSAGE

    def temperature_historical(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} the temperature was {} degrees in {}""".format(
                request_data['context']['time'].capitalize(), response['temperature_c'], response['city'])
        return DEFAULT_MESSAGE

    def is_xxxing(self, xxx, condition):
        return xxx in condition.lower()

    def xxxfall(self, ws, xxx, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} it is currently {}ing.""".format(response['city'], xxx)
            else:
                return """In {} it is currently not {}ing.""".format(response['city'], xxx)
        return DEFAULT_MESSAGE

    def xxxfall_forecast(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it will {}.""".format(response['city'], request_data['context']['time'], xxx)
            else:
                return """In {} {} it is not expected to {}.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def xxxfall_historical(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it was {}ing.""".format(response['city'], request_data['context']['time'], xxx)
            else:
                return """In {} {} it was not {}ing.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def xxx(self, ws, xxx, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} it is currently {}.""".format(response['city'], xxx)
            else:
                return """In {} it is currently not {}.""".format(response['city'], xxx)
        return DEFAULT_MESSAGE

    def xxx_forecast(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it will be {}.""".format(response['city'], request_data['context']['time'], xxx)
            else:
                return """In {} {} it is not expected to be {}.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def xxx_historical(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it was {}.""".format(response['city'], request_data['context']['time'], xxx)
            else:
                return """In {} {} it was not {}.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def precip(self, ws, xxx, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} there are currently {} inches of {}.""".format(response['city'], response['precip'], xxx)
            else:
                return """In {} it is currently not {}ing.""".format(response['city'], xxx)
        return DEFAULT_MESSAGE

    def precip_forecast(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it will be {}ing the expected precipitation is {} inches.""".format(response['city'], request_data['context']['time'], xxx, response['precip'])
            else:
                return """In {} {} it is not expected to be {}ing.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def precip_historical(self, ws, xxx, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            if self.is_xxxing(xxx, response['condition']):
                return """In {} {} it was {}ing with {} inches.""".format(response['city'], request_data['context']['time'], xxx, response['precip'])
            else:
                return """In {} {} it was not {}ing.""".format(response['city'], request_data['context']['time'], xxx)
        return DEFAULT_MESSAGE

    def humidity(self, ws, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """The humidity is {} percent in {} at the moment.""".format(
                response['humidity'], response['city'])
        return DEFAULT_MESSAGE

    def humidity_forecast(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} the humidity will be {} percent in {}.""".format(
                request_data['context']['time'].capitalize(), response['humidity'], response['city'])
        return DEFAULT_MESSAGE

    def humidity_historical(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            return """{} the humidity was {} percent in {}""".format(
                request_data['context']['time'].capitalize(), response['humidity'], response['city'])
        return DEFAULT_MESSAGE

    def get_feeling(self, temperature):
        if temperature > 30:
            return 'hot'
        elif temperature > 20:
            return 'warm'
        elif temperature >10:
            return 'chilly'
        elif temperature > 0:
            return 'cold'
        else:
            return 'very cold'

    def feel(self, ws, request_data):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            feel = self.get_feeling(response['temperature_c_int'])
            return """In {} at the moment is {}.""".format(response['city'], feel)
        return DEFAULT_MESSAGE

    def feel_forecast(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            feel = self.get_feeling(response['temperature_c_int'])
            return """{} it will be {} in {}.""".format(
                request_data['context']['time'].capitalize(), feel, response['city'])
        return DEFAULT_MESSAGE

    def feel_historical(self, ws, request_data, day):
        response = {}
        ws.query_weather(request_data['context']['location'], response)
        if response['success']:
            feel = self.get_feeling(response['temperature_c_int'])
            return """{} it was {} in {}""".format(
                request_data['context']['time'].capitalize(), feel, response['city'])
        return DEFAULT_MESSAGE

    # execute state
    def run(self, request_data):
        ws = WeatherService()
        days = ws.time_to_days(request_data['context'])
        if request_data['context']['intent'] == 'weather.weather' or \
                request_data['context']['intent'] == 'context.weather':
            if days > 0:
                message = self.weather_forecast(ws, request_data, days)
            elif days < 0:
                message = self.weather_historical(ws, request_data, days)
            else:
                message = self.weather(ws, request_data)
        elif request_data['context']['intent'] == 'weather.temprature':
            if days > 0:
                message = self.temperature_forecast(ws, request_data, days)
            elif days < 0:
                message = self.temperature_historical(ws, request_data, days)
            else:
                message = self.temperature(ws, request_data)
        elif request_data['context']['intent'] == 'weather.rainfall_yes_no':
            if days > 0:
                message = self.xxxfall_forecast(ws, 'rain', request_data, days)
            elif days < 0:
                message = self.xxxfall_historical(ws, 'rain', request_data, days)
            else:
                message = self.xxxfall(ws, 'rain', request_data)
        elif request_data['context']['intent'] == 'weather.snow_yes_no':
            if days > 0:
                message = self.xxxfall_forecast(ws, 'snow', request_data, days)
            elif days < 0:
                message = self.xxxfall_historical(ws, 'snow', request_data, days)
            else:
                message = self.xxxfall(ws, 'snow', request_data)
        elif request_data['context']['intent'] == 'weather.cloudy':
            if days > 0:
                message = self.xxx_forecast(ws, 'cloudy', request_data, days)
            elif days < 0:
                message = self.xxx_historical(ws, 'cloudy', request_data, days)
            else:
                message = self.xxx(ws, 'cloudy', request_data)
        elif request_data['context']['intent'] == 'weather.sunny':
            if days > 0:
                message = self.xxx_forecast(ws, 'sunny', request_data, days)
            elif days < 0:
                message = self.xxx_historical(ws, 'sunny', request_data, days)
            else:
                message = self.xxx(ws, 'sunny', request_data)
        elif request_data['context']['intent'] == 'weather.snow':
            if days > 0:
                message = self.precip_forecast(ws, 'snow', request_data, days)
            elif days < 0:
                message = self.precip_historical(ws, 'snow', request_data, days)
            else:
                message = self.precip(ws, 'snow', request_data)
        elif request_data['context']['intent'] == 'weather.rainfall':
            if days > 0:
                message = self.precip_forecast(ws, 'rain', request_data, days)
            elif days < 0:
                message = self.precip_historical(ws, 'rain', request_data, days)
            else:
                message = self.precip(ws, 'rain', request_data)
        elif request_data['context']['intent'] == 'weather.temperature_yes_no':
            if days > 0:
                message = self.feel_forecast(ws, request_data, days)
            elif days < 0:
                message = self.feel_historical(ws, request_data, days)
            else:
                message = self.feel(ws, request_data)
        elif request_data['context']['intent'] == 'weather.humidity' or \
                request_data['context']['intent'] == 'weather.humidity_yes_no':
            if days > 0:
                message = self.humidity_forecast(ws, request_data, days)
            elif days < 0:
                message = self.humidity_historical(ws, request_data, days)
            else:
                message = self.humidity(ws, request_data)
        elif request_data['context']['intent'] == 'qa_answer':
            message = request_data['context']['answer_span'] # "This is a test QA response"
            # message = extend_answer(request_data['context']['query'],
            #                         request_data['context']['answer_span'])  # "This is a test QA response"

                #request_data['context']['answer_span']
        else:
            message = "Ask me later."
        request_data['context'].update({'weather_status': message})

        # Update the response text with the weather status
        request_data.update({'response':
                             self.construct_message(request_data, message)})
