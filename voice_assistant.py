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
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY, region=SPEECH_REGION
        )
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        
        # Use recognize_once instead of recognize_once_async for better control
        result = recognizer.recognize_once()
        
        if result.text:
            # Process the recognized text through safety pipeline
            try:
                safe_text = process_prompt(result.text)
                return safe_text
            except ValueError as e:
                # Convert safety warning to speech
                warning = f"Safety Alert: {str(e)}"
                text_to_speech(warning)
                return warning
        return ""
            
    except Exception as e:
        print(f"Speech Recognition Error: {e}")
        return ""
