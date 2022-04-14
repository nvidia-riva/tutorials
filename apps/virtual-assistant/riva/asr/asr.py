# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import sys
import re
import grpc
import riva_api.riva_audio_pb2 as ra
import riva_api.riva_asr_pb2 as rasr
import riva_api.riva_asr_pb2_grpc as rasr_srv
from six.moves import queue
from config import riva_config, asr_config

# Default ASR parameters - Used in case config values not specified in the config.py file
VERBOSE = False
SAMPLING_RATE = 16000
LANGUAGE_CODE = "en-US"
ENABLE_AUTOMATIC_PUNCTUATION = True
STREAM_INTERIM_RESULTS = True

class ASRPipe(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self):
        self.verbose = asr_config["VERBOSE"] if "VERBOSE" in asr_config else VERBOSE
        self.sampling_rate = asr_config["SAMPLING_RATE"] if "SAMPLING_RATE" in asr_config else SAMPLING_RATE
        self.language_code = asr_config["LANGUAGE_CODE"] if "LANGUAGE_CODE" in asr_config else LANGUAGE_CODE
        self.enable_automatic_punctuation = asr_config["ENABLE_AUTOMATIC_PUNCTUATION"] if "ENABLE_AUTOMATIC_PUNCTUATION" in asr_config else ENABLE_AUTOMATIC_PUNCTUATION
        self.stream_interim_results = asr_config["STREAM_INTERIM_RESULTS"] if "STREAM_INTERIM_RESULTS" in asr_config else STREAM_INTERIM_RESULTS
        self.chunk = int(self.sampling_rate / 10) # 100ms
        self._buff = queue.Queue()
        self._transcript = queue.Queue()
        self.closed = False

    def start(self):
        if self.verbose:
            print('[Riva ASR] Creating Stream ASR channel: {}'.format(riva_config["RIVA_SPEECH_API_URL"]))
        self.channel = grpc.insecure_channel(riva_config["RIVA_SPEECH_API_URL"])
        self.asr_client = rasr_srv.RivaSpeechRecognitionStub(self.channel)

    def close(self):
        self.closed = True
        self._buff.queue.clear()
        self._buff.put(None) # means the end
        del(self.channel)

    def empty_asr_buffer(self):
        """Clears the audio buffer."""
        if not self._buff.empty():
            self._buff.queue.clear()

    def fill_buffer(self, in_data):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)

    def get_transcript(self):
        """Generator returning chunks of audio transcript"""
        while True:  # not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            trans = self._transcript.get()
            if trans is None:
                return
            yield trans

        """Generates byte-sequences of audio chunks from the audio buffer"""
    def build_request_generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    def listen_print_loop(self, responses):
        """Iterates through server responses and populates the audio
        transcription buffer (and prints the responses to stdout).

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()
                interm_trans = transcript + overwrite_chars + '\r'
                interm_str = f'event:{"intermediate-transcript"}\ndata: {interm_trans}\n\n'
                self._transcript.put(interm_str)
            else:
                if self.verbose:
                    print('[Riva ASR] Transcript:', transcript + overwrite_chars)
                final_transcript = transcript + overwrite_chars
                final_str = f'event:{"finished-speaking"}\ndata: {final_transcript}\n\n'
                self._transcript.put(final_str)
            num_chars_printed = 0
        if self.verbose:
            print('[Riva ASR] Exit')

    def main_asr(self):
        """Creates a gRPC channel (thread-safe) with RIVA API server for
        ASR Calls, and retrieves recognition/transcription responses."""
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        self.start()
        config = rasr.RecognitionConfig(
            encoding=ra.AudioEncoding.LINEAR_PCM,
            sample_rate_hertz=self.sampling_rate,
            language_code=self.language_code,
            max_alternatives=1,
            enable_automatic_punctuation=self.enable_automatic_punctuation,
            verbatim_transcripts=True
        )
        streaming_config = rasr.StreamingRecognitionConfig(
            config=config,
            interim_results=self.stream_interim_results)

        if self.verbose:
            print("[Riva ASR] Starting Background ASR process")
        self.request_generator = self.build_request_generator()
        requests = (rasr.StreamingRecognizeRequest(audio_content=content)
                    for content in self.request_generator)

        def build_generator(cfg, gen):
            yield rasr.StreamingRecognizeRequest(streaming_config=cfg)
            for x in gen:
                yield x
            yield cfg

        if self.verbose:
            print("[Riva ASR] StreamingRecognize Start")
        responses = self.asr_client.StreamingRecognize(build_generator(streaming_config, requests))
        # Now, put the transcription responses to use.
        self.listen_print_loop(responses)
