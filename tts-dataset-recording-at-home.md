# Guidelines to Record a TTS Dataset at Home

This section describes best practices for getting the best audio quality when recording TTS data at home.

## What data?
Start by recording the [harvard sentences](http://www.cs.cmu.edu/afs/cs.cmu.edu/project/fgdata/OldFiles/Recorder.app/utterances/Type1/harvsents.txt), which should produce about 20 to 40 minutes of usable data for TTS.

## What gear?

* Use a decent cheap microphone like the [Audio-Technica AT2020USB+](https://www.amazon.com/gp/product/B00B5ZX9FM/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) or the [blue yeti usb mic](https://www.amazon.com/Blue-Yeti-USB-Microphone-Silver/dp/B002VA464S).

* Get a boom filter or windscreen.

## What audio recording software?

This document focuses on [Audacity](https://www.audacityteam.org/): it’s free, and it has a db meter and shortcuts for making recording easy.

[Reaper](https://www.reaper.fm/) is also quite good but not yet covered on this document.

<u>Do not use software that does not have a numbered db meter.</u>

## How to set up for recording?

1.  Connect your microphone to your computer.
    
2.  Open Audacity.
    
3.  Select your audio interface.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/7874fef9-4e34-400b-9e0c-2bd8a734111e">
    
    
4.  Set the bit depth to 24-bit preferably or 16-bit.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/d3eb72fa-2842-49bb-93d1-a0d09f29c4a7">
    
    
5.  Set the sampling rate to 96 kHz preferably or 44 kHz.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/c0067a97-3425-472e-8580-4e2648d3b894">
    
    
6.  On the microphone, set the microphone pattern to **Cardioid** if you have that option.
    
<img width="450" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/6e5e7a0e-ab58-41fc-8c11-be6921642f52"> <img width="455" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/bb834106-ac03-4eb5-91dd-eb4d1918234a">
    
  
7.  Set up the boom filter or windscreen.
    
<img width="450" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/c08c2fbd-0f3d-46e9-aa92-f51519d183d6">
    
    
8.  Select the most quiet room in your environment, and close your windows and doors.
    
9.  Eliminate external sources of noise, e. g. air conditioning, computer fan, kids, etc...

## How to adjust microphone levels and body position before recording?

1.  Set your microphone gain to ‘9 hours.’
    
2.  Press the recording button on Audacity.
    
3.  Make sure you’re talking onto the side of the microphone that has the brand logo.
    
<img width="450" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/700927ca-1a40-4a30-938a-b6330dba3a85">
    
      
4.  Position yourself at least a fist away from the microphone and no more than a foot away.
    
<img width="450" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/ee03a9ea-2207-48a5-85ae-0f7a939c066e">
    
    
5.  Speak into the microphone with the voice you will use during the TTS data recording.
    
6.  Adjust the [microphone gain](https://www.homemusicstudio1.com/how-to-set-recording-levels/) to optimize the signal to noise ratio:
    
- If you’re recording with 24-bit, make sure the db meter is hitting between -24 db and -6 db while you’re recording.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/21a99b40-523a-423b-8cd0-15ffd7dc7f8d">
    
    
    
- If you’re recording with 16-bit, make sure the db meter is between -12 db and -6 db while you’re recording.
    
7.  Do not change the microphone gain after you’ve adjusted it.
    
## What happens if you position yourself just right, too far or too close?
- **1 fist away (just right)** – no distortions, minimal room sound, good signal to noise ratio.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/1bb0dec4-2b35-4d35-8db2-e4a572ed6992">
    

    
- **1 inch away** – muffled (proximity effect) and distortion from plosives like /b/ and /p/.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/cb082600-7323-4e39-9e3b-4b68a62f29a5">
    

    
- **2 feet away** – lots of room sound and bad signal-to-noise ratio.
    
<img width="1000" alt="image" src="https://github.com/mgrafu/tutorials/assets/47233618/3851e09e-b62b-4e71-8a3c-dda3ec65892b">


## How to record the TTS data?

1.  Prepare your script such that you can easily read it.
    
2.  Press Shift+R to record into a new track, read the first sentence, and press space bar to stop recording.
    
3.  Repeat Step 2 for each sentence in your dataset until you have completed the recording of the last one.
    
4.  Export all files by clicking on File –> Export –> Export Multiple...
