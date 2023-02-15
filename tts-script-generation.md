<img src="http://developer.download.nvidia.com/notebooks/dlsw-notebooks/riva_asr_deploy-eks/nvidia_logo.png" style="width: 90px; float: right;">


# Data collection - Script Generation


In this document, we will cover the outline to create a script for the voice actor to record. The script must cover all the phonemes with good coverage, must be relevant to the domain, and should have the necessary visual cues for the voice actor to get the desired cadence.


## Identifying data sources:


- The content that the voice actor will read needs to be aligned with the use case of the synthesized voice. If the voice is used for questions, have questions in the script. If the voice is going to be used for emotion, then have emotion in the script.


- Another option is to synthetically generate text to be read, using a large language model like Megatron, BERT, or GPT-3. Since the data is coming from an LLM, it requires more manual normalization compared to other datasets.


- The data source must contain enough sentences to meet the training requirement. Rule of thumb calculation for the number of sentences: 20k sentences = 60 hours of studio time = 20 hours of useable audio. Currently, that 20 hours is enough audio for a voice trained from scratch in NeMo.


- Eliminate foreign or difficult-to-pronounce words. Ensure correct punctuation, correct spelling, and consistent normalization. This helps in improving the usable audio time.


- Make the process easier for the voice actor. The smoother things are for the voice actor the more high-quality usable audio is obtained.


## Phoneme coverage and distribution
Each language is made up of sounds that are the ‘building blocks’ of a spoken language. These are called [phonemes](https://en.wikipedia.org/wiki/Phoneme). For example, there are 44 [phonemes in the English language](https://en.wikipedia.org/wiki/English_phonology).


After the script is acquired. It should comply with two requirements listed below:


- **Phoneme coverage**: To train a TTS model, ensure that the script has phoneme coverage of all 44 phonemes of English. If the script does not have coverage of all phonemes, the TTS model will not learn all phonemes and may pronounce some phonemes incorrectly.
- **Phoneme distribution**: Not only does the script need to have coverage of phonemes, but it also needs to have the right phoneme distribution compared to a baseline.








 Datasets like the Harvard Sentences have complete phoneme coverage, and phoneme distribution matching American English, and serve as a good reference point. The script must have good coverage (many samples) of frequently occurring phonemes - fewer samples of phonemes mean that the model is less likely to generate that phoneme well.


The [phoneme distribution analysis notebook](https://github.com/nvidia-riva/tutorials/blob/main/tts-phoneme-distribution.ipynb) shows how to do an analysis of the phoneme coverage and phoneme distribution.


## Technical requirements
- **Length**: Each line of the script should take the voice actor between 10 seconds and 20 seconds to read aloud. Most people speak at 100 to 130 words per minute so this is around 16 to 26 words, as a rough heuristic (for English, other languages will vary).
- **Phonetic distribution**: Phonemes are the building blocks of words. There are 44 phonemes in the English language, and they appear at different frequencies in English speech. The Harvard sentence is a reference distribution. It’s a good idea to run a phoneme comparison on your lines of text to understand how they compare to Harvard sentences.
- **Normalization**: Normalization is the process of converting numbers, abbreviations, datetime, units, etc into their spoken form. Normalization is required to reduce ambiguity between the characters in the script eventually reducing the ambiguity in the input data to the model. For English, there is a normalization script in Nemo, but it won’t catch everything, and a manual review is required.
- **Grammar**: Each line of text that is a question should end with a question mark. This is so the model can learn the pronunciation of sentences that are questions (they often rise in pitch at the end). Other end-of-line punctuation - periods, exclamation marks - is less important, but valuable.


## Heuristics for manually normalizing
- Search for each digit 0, 1, 2, 3, 4, 5, 6, 7, 8, 9. They will be present if there are normalization errors. Manually normalize them into written form - for example, if you see “1950s”, normalize them to “nineteen fifties”.
    - Sports scores often require significant manual normalization. The normalization required can vary by sport, with some sports having specialized terms like “deuce” for tennis. For example, there are a lot of sports scores in the dataset, and you need to know which sport they are to do the correct normalization of cardinals into spoken form.
- Search for the phrase “dot”. This occurs frequently in normalization errors. Correct as appropriate. Sometimes time tokens like “5.00a.m.” will be normalized as “five dot a dot m”. This is not how the time is pronounced, and it needs to be fixed, for example, to “five a m”.
- Search for the phrase “comma”. This can be introduced through (incorrect) programmatic normalization, similar to “dot”.  
- Search for currency symbols such as “$”. If normalization errors have occurred, the symbols might not have been normalized into dollars, cents, pounds etc.
- Search for the degree symbol “°”. This is often not caught in normalization and has to be manually normalized.
- Search for the character “/” (slash). It is often not normalized properly, and you want words like “bar/lounge” pronounced as “bar lounge”, so remove the slash.
- Capitalized proper nouns like New York City instead of new york city, or Paris instead of Paris, make it a lot easier for the voice actor to read the script.
- Ensure questions end with a question mark. A good heuristic for this is searching for pipe, and then a question word (as the pipe | will precede the start of the sentence) - such as how, what, when, where, do you etc.
- Search for calendar months - January”, Februaryy” etc - and ensure that the names of the months are capitalized - this makes the text easier for the voice actors to read.
- Search for three periods (ellipsis) “...” as this is often used to denote pauses in speech. It’s often ambiguous to pronounce.
- Capitalization of acronyms - acronyms such as “GPU” and “CPU” should be left in capitals, but space should be added between them - such as “G P U”.
- Sometimes if the text is processed into a script from Unicode format, Unicode escape sequences need to be searched for and corrected. Unicode escape sequences convert a single character to the format of a 4-digit hexadecimal code point, such as \uXXXX. For example, "A" becomes "\u0041". Search for “\u” to identify if there are any in your lines of text.
- Sometimes if the text is processed from HTML, ISO 8859-1 Characters will be in text and need to be replaced, for example - &#160;. You will need to search for “&#” to find them. Use this [table](https://www.html.am/reference/html-special-characters.cfm) to determine what to replace them with, or use a plugin in your IDE.
- Run a spell checker over the lines of text. This will usually find several spelling errors. Spelling errors make it harder for the voice actor to read the script.


## Conclusion
Once every step mentioned above is completed, the script can be sent to the  voice actor for recording. Remember, TTS training is sensitive to data and any discrepancy in data will lead to an inferior quality final model. Therefore, it is imperative to verify the integrity of data at all steps.
