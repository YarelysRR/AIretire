import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import base64
from prompt_safety import process_prompt

load_dotenv()

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")


def text_to_speech(text):
    try:
        SPEECH_KEY = os.getenv("SPEECH_KEY")
        SPEECH_REGION = os.getenv("SPEECH_REGION")

        if not SPEECH_KEY or not SPEECH_REGION:
            print("Missing Azure Speech credentials in .env file")
            return ""

        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio_data
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            # Modify the returned HTML to include a unique ID and self-removal:
            return f"""
                <audio autoplay onended="this.remove()" style="display: none;">
                    <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                </audio>
            """

    except Exception as e:
        print(f"VOICE ERROR: {str(e)}")
        return ""


# ADDED NEW
def speech_to_text():
    """
    Convert speech to text using Azure Speech Services.
    Returns the transcribed text or None if there's an error.
    """
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )
        speech_config.speech_recognition_language = "en-US"
        
        # Configure recognition settings for better silence detection
        speech_config.set_property(
            speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "3000"  # 3 seconds silence
        )
        speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "5000"  # 5 seconds to start
        )
        speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "3000"  # Stop after 3s silence
        )
        
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        
        # Create recognizer with the given settings
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )

        # Set up result handling
        done = False
        recognized_text = None

        def handle_result(evt):
            nonlocal recognized_text
            if evt.result.text:
                recognized_text = evt.result.text

        def stop_cb(evt):
            nonlocal done
            done = True
        
        # Connect callbacks to the events
        recognizer.recognized.connect(handle_result)
        recognizer.session_stopped.connect(stop_cb)
        recognizer.canceled.connect(stop_cb)
        
        # Start recognition
        result = recognizer.recognize_once()
        
        # Process the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if result.text:
                try:
                    # Process through safety pipeline
                    safe_text = process_prompt(result.text)
                    return safe_text
                except ValueError as e:
                    print(f"Safety check failed: {e}")
                    return None
            return None
        elif result.reason == speechsdk.ResultReason.NoMatch:
            if result.no_match_details.reason == speechsdk.NoMatchReason.InitialSilenceTimeout:
                print("No speech detected within timeout period")
            return None
        elif result.reason == speechsdk.ResultReason.Canceled:
            return None
        
    except Exception as e:
        print(f"Speech Recognition Error: {e}")
        return None
