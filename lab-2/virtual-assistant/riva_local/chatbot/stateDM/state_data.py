# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

# This is used for finding the state to transition to based on intent
intent_transitions = {
    'rivaWeather': {
        'weather.qa_answer': 'checkWeatherLocation',
        'weather.weather': 'checkWeatherLocation',
        'context.weather': 'checkWeatherLocation',
        'weather.temprature': 'checkWeatherLocation',
        'weather.sunny': 'checkWeatherLocation',
        'weather.cloudy': 'checkWeatherLocation',
        'weather.snow': 'checkWeatherLocation',
        'weather.rainfall': 'checkWeatherLocation',
        'weather.snow_yes_no': 'checkWeatherLocation',
        'weather.rainfall_yes_no': 'checkWeatherLocation',
        'weather.temperature_yes_no': 'checkWeatherLocation',
        'weather.humidity': 'checkWeatherLocation',
        'weather.humidity_yes_no': 'checkWeatherLocation',
        'navigation.startnavigationpoi': 'checkWeatherLocation',
        'navigation.geteta': 'checkWeatherLocation',
        'navigation.showdirection': 'checkWeatherLocation',
        'riva_error': 'error',
        'navigation.showmappoi': 'error',
        'nomatch.none': 'error'
    }
}