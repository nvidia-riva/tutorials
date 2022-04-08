# Riva Virtual Assistant Example

## Overview

The Virtual Assistant sample demonstrates how to use Riva AI Services, specifically ASR, NLP, and TTS, to build a simple but complete conversational AI application. It demonstrates receiving input via speech from the user, interpreting the query via an intention recognition and slot filling approach, computing a response, and speaking this back to the user in a natural voice.

You can find more information about the Riva Weather Chatbot and how to run it [here](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/samples/weather.html).

## Running the Virtual Assistant

Setting up Riva services is a prerequisite as the various components of the application depends on the availability of those servies. The weather bot assumes the availablity of the following models at the Riva endpoint – ASR, TTS, NLP (weather domain intent & slot model). After you have the Riva services up and running, proceed with running this application.

1. Create and enable a Python [virtual environment](https://virtualenv.pypa.io/en/latest/)
```bash
virtualenv -p python3 apps-env
source apps-env/bin/activate
```

2. Install required dependencies using [pip](https://pip.pypa.io/en/stable/)
```bash
pip3 install -r requirements.txt
```

3. Edit the configuration file [config.py](./config.py), and set:
    * The Riva speech server URL. This is the endpoint where the Riva services can be accessed. 
    * The [weatherstack API access key](https://weatherstack.com/documentation). The VA uses weatherstack for weather fulfillment, that is when the weather intents are recognized, real-time weather information is fetched from weatherstack. Sign up to the free tier of [weatherstack](https://weatherstack.com/), and get your API access key. 

The code snippet will look like the example below.
```python3
riva_config = {
  "RIVA_SPEECH_API_URL": "<IP>:<PORT>", # Replace the IP & port with your hosted Riva endpoint
   ...
  "WEATHERSTACK_ACCESS_KEY": "<API_ACCESS_KEY>",  # Get your access key at - https://weatherstack.com/
   ...
}
```

4. Run the virtual assistant application
```bash
python3 main.py
```

## Sample Use Cases
It is possible to ask the bot the following types of questions:

* What is the weather in Berlin?
* What is the weather?
    * For which location?
* What’s the weather like in San Francisco tomorrow?
    * What about in Los Angeles, California?
* What is the temperature in Milan on Friday?
* Is it currently cold in San Francisco?
* Is it going to rain in Mountain View tomorrow?
* How much rain in Seattle?
* Will it be sunny next week in Santa Clara?
* Is cloudy today?
* Is it going to snow tomorrow in Detroit?
* How much snow is there in Tahoe currently?
* How humid is it right now?
* What is the humidity in Tahoe?

## Limitations
* The provided samples are not complete chatbots, but are intended as simple examples of how to build basic task-oriented chatbots with Riva. Consequently, the intent classifier and slot filling models have been trained with small amounts of data and are not expected to be highly accurate.
* The Riva NLP sample supports intents for weather, temperature, rain, humidity, sunny, cloudy and snowfall checks. It does not support general conversational queries or other domains.
* Both the Riva NLP and Rasa NLU samples support only 1 slot for city. Neither takes into account the day associated with the query.
* These samples support up to four concurrent users. This restriction is not because of Riva, but because of the web framework (Flask and Flask-ScoketIO) that is being used. The socket connection is to stream audio to (TTS) and from (ASR); you are unable to sustain more than four concurrent socket connections.
* The chatbot application is not optimized for low latency in the case of multiple concurrent users.
* Some erratic issues have been observed with the chatbot samples on the Firefox browser. The most common issue is the TTS output being taken in as input by ASR for certain microphone gain values.

## License
[End User License Agreement](https://developer.download.nvidia.com/licenses/Riva_Pre-Release_Evaluation_License_23Jan2020.pdf) is included with the product. Licenses are also available along with the model application zip file. By pulling and using the Riva SDK container, downloading models, or using the sample applications, you accept the terms and conditions of these licenses.
