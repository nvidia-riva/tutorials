# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import requests
import datetime

try:
    import inflect
except ImportError:
    print("[Riva DM] Import Error: Import inflect failed!")
    raise ImportError

from config import riva_config

p = inflect.engine()

'''
typical api_response format
{'request': {'type': 'City', 'query': 'London, United Kingdom', 'language': 'en', 'unit': 'm'},
'location': {'name': 'London', 'country': 'United Kingdom', 'region': 'City of London, Greater London',
'lat': '51.517', 'lon': '-0.106', 'timezone_id': 'Europe/London', 'localtime': '2019-12-10 22:16',
'localtime_epoch': 1576016160, 'utc_offset': '0.0'}, 'current': {'observation_time': '10:16 PM',
'temperature': 10, 'weather_code': 296, 'weather_icons': ['https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0033_cloudy_with_light_rain_night.png'],
'weather_descriptions': ['Light Rain'], 'wind_speed': 24, 'wind_degree': 260, 'wind_dir': 'W', 'pressure': 1006,
'precip': 1.4, 'humidity': 82, 'cloudcover': 0, 'feelslike': 7, 'uv_index': 1, 'visibility': 10, 'is_day': 'no'}}
'''


def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    
    try:
        for word in textnum.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

    except Exception as e:
        print(e)
        # If an Illegal word is detected, ignore the whole weathertime
        return 0

    return result + current


class WeatherService:

    def __init__(self):
        self.access_key = riva_config["WEATHERSTACK_ACCESS_KEY"]
        self.days_of_week = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        self.weekend = 'weekend'

    def time_to_days(self, context):
        if riva_config['VERBOSE']:
            print('[Riva Weather] Time info from the query:', context['payload'])
        ctxtime = False
        if 'weatherforecastdaily' in context['payload']:
            ctxtime = context['payload']['weatherforecastdaily'].lower()
        if 'weathertime' in context['payload']:
            ctxtime = context['payload']['weathertime'].lower()
            if ctxtime == "week":
                if 'weatherforecastdaily' in context['payload']:
                    ctxtime = context['payload']['weatherforecastdaily'].lower() + " " + ctxtime
                else:
                    ctxtime = False
        if 'day_of_week' in context['payload']:
            ctxtime = context['payload']['day_of_week'].lower()
        if ctxtime:
            context['time'] = ctxtime
            if 'now' in ctxtime:
                return 0
            elif 'tomorrow' in ctxtime:
                return 1
            elif 'next week' in ctxtime:
                return 7
            elif 'yesterday' in ctxtime:
                return -1
            elif 'last week' in ctxtime:
                return -7
            elif ctxtime in self.days_of_week:
                diff = self.days_of_week[ctxtime] - datetime.datetime.today().weekday()
                if diff<0:
                    diff+=7
                return diff
            elif self.weekend in ctxtime:
                context['time'] = 'during the weekend'
                return self.days_of_week['sunday'] - datetime.datetime.today().weekday()
            elif 'weathertime' in context['payload']:
                if not isinstance(context['payload']['weathertime'], int):
                    q = text2int(context['payload']['weathertime'])
                else:
                    q = context['payload']['weathertime']
                context['time'] = "in {} {}".format(context['payload']['weathertime'], ctxtime)
                if 'week' in ctxtime:
                    return q*7
                elif 'days' in ctxtime:
                    return q
        return 0

    def query_weather(self, location, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()
            if riva_config['VERBOSE']:
                print("[Riva Weather] Weather API Response: " + str(api_response))

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return

            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = p.number_to_words(api_response['current']['temperature'])
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = p.number_to_words(api_response['current']['humidity'])
            response['wind_mph'] = p.number_to_words(api_response['current']['wind_speed'])
            response['precip'] = p.number_to_words(api_response['current']['precip'])
        except:
            response['success'] = False

    def query_weather_forecast(self, location, day, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return
            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = p.number_to_words(api_response['current']['temperature'])
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = p.number_to_words(api_response['current']['humidity'])
            response['wind_mph'] = p.number_to_words(api_response['current']['wind_speed'])
        except:
            response['success'] = False

    def query_weather_historical(self, location, day, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return

            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = p.number_to_words(api_response['current']['temperature'])
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = p.number_to_words(api_response['current']['humidity'])
            response['wind_mph'] = p.number_to_words(api_response['current']['wind_speed'])

        except:
            response['success'] = False
