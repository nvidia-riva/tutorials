# Guidelines to Record a TTS Dataset at Home

This section describes how to get the best audio quality when recording TTS data at home.

## Recommended Data
Start by recording the [Harvard sentences](http://www.cs.cmu.edu/afs/cs.cmu.edu/project/fgdata/OldFiles/Recorder.app/utterances/Type1/harvsents.txt), which should produce about 20 to 40 minutes of usable data for TTS.

## Hardware Requirements

* Use a microphone like the [Audio-Technica AT2020USB+](https://www.amazon.com/gp/product/B00B5ZX9FM/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) or the [Blue Yeti USB mic](https://www.amazon.com/Blue-Yeti-USB-Microphone-Silver/dp/B002VA464S).

* Get a boom filter or windscreen.

## Software Requirements

This document focuses on [Audacity](https://www.audacityteam.org/): it’s free, and it has a db meter and shortcuts for making recording easy.

[Reaper](https://www.reaper.fm/) is also quite good but not yet covered on this document.

<u>Do not use software that does not have a numbered db meter.</u>

## Recording Prerequisites

1.  Connect your microphone to your computer.
    
2.  Open Audacity.
    
3.  Select your audio interface.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-1.png">
    
    
4.  Set the bit depth to 24-bit preferably or 16-bit.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-2.png">
    
    
5.  Set the sampling rate to 96 kHz preferably or 44 kHz.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-3.png">
    
    
6.  On the microphone, set the microphone pattern to **Cardioid** if you have that option.
    
<img width="450" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-4.png"> <img width="455" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-5.png">
    
  
7.  Set up the boom filter or windscreen.
    
<img width="450" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-6.png">
    
    
8.  Select the most quiet room in your environment, and close your windows and doors.
    
9.  Eliminate external sources of noise, for example, air conditioning, computer fan, and so on.

## Adjusting the Microphone Level and Body Position Before Recording

1.  Set your microphone gain to the direction of a clock's hour hand marking '9 o'clock.'
    
2.  Press the recording button on Audacity.
    
3.  Make sure you’re talking onto the side of the microphone that has the brand logo.
    
<img width="450" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-7.png">
    
      
4.  Position yourself at least a fist away from the microphone and no more than a foot away.
    
<img width="450" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-8.png">
    
    
5.  Speak into the microphone with the voice you will use during the TTS data recording.
    
6.  Adjust the [microphone gain](https://www.homemusicstudio1.com/how-to-set-recording-levels/) to optimize the signal to noise ratio:
    
- If you’re recording with 24-bit, make sure the db meter is hitting between -24 db and -6 db while you’re recording.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-9.png">
    
    
    
- If you’re recording with 16-bit, make sure the db meter is between -12 db and -6 db while you’re recording.
    
7.  Do not change the microphone gain after you’ve adjusted it.
    
## Positioning Yourself Just Right, Too Far or Too Close
- **1 fist away (just right)** – no distortions, minimal room sound, good signal to noise ratio.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-10.png">
    

    
- **1 inch away** – muffled (proximity effect) and distortion from plosives like /b/ and /p/.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-11.png">
    

    
- **2 feet away** – lots of room sound and bad signal-to-noise ratio.
    
<img width="1000" alt="image" src="https://raw.githubusercontent.com/nvidia-riva/tutorials/main/imgs/tts-home-recording-12.png">


## Recording the TTS Data

1.  Prepare your script such that you can easily read it.
    
2.  Press **Shift+R** to record into a new track, read the first sentence, and press space bar to stop recording.
    
3.  Repeat Step 2 for each sentence in your dataset until you have completed the recording of the last one.
    
4.  Export all files by clicking on **File** > **Export** > **Export Multiple...**.
