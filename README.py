# raspberry_pi_5_based_chatgpt_voice_endpoint
import os
import logging
from typing import Optional

import speech_recognition as sr
from gtts import gTTS
from langchain_openai import ChatOpenAI
import pygame

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VoiceAssistant:
    def __init__(self, api_key: str, 
                 api_base: str = "https://proxy.tune.app/", 
                 model: str = "openai/gpt-4o-mini"):
        """
        Initialize the Voice Assistant with ChatGPT and Speech capabilities
        """
        try:
            # Initialize pygame mixer for audio
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)  # Set volume to maximum
            self.chat_model = ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base=api_base,
                model_name=model
            )
            self.recognizer = sr.Recognizer()
            
            # Adjust for ambient noise
            with sr.Microphone() as source:
                logger.info("Calibrating microphone for noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise

    def listen(self, timeout: int = 5, phrase_time_limit: int = 3) -> Optional[str]: 
        """
        Listen and convert speech to text
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.info("Recognizing speech...")
            query = self.recognizer.recognize_google(audio, language='en-US')
            logger.info(f"Recognized: {query}")
            return query
        
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return None

    def get_chatgpt_response(self, prompt: str) -> str:
        """
        Get response from ChatGPT
        """
        try:
            response = self.chat_model.invoke(prompt)
            return str(response)
        except Exception as e:
            logger.error(f"ChatGPT response error: {e}")
            return "Sorry, I couldn't process your request at the moment."

    def speak(self, text: str, language: str = 'en') -> None:
        """
        Convert text to speech and play audio with multiple fallback methods
        """
        try:
            # Create a temporary audio file
            temp_file = "temp_response.mp3"
            
            # Use gTTS to generate speech
            tts = gTTS(text=text, lang=language)
            tts.save(temp_file)
            
            # Use pygame to play audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(5)
            
            # Remove temporary file
            os.remove(temp_file)
        
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            # Fallback: Print the response if audio fails
            print(f"Response (Audio Failed): {text}")

    def run(self):
        """
        Main loop for voice assistant
        """
        logger.info("Voice Assistant Started. Press Ctrl+C to exit.")
        try:
            while True:
                query = self.listen()
                if query:
                    response = self.get_chatgpt_response(query)
                    print(f"AI: {response}")
                    self.speak(response)
        except KeyboardInterrupt:
            logger.info("Voice Assistant Stopped.")

def main():
    try:
        # Use your API key
        API_KEY = "your_api_key_here"
        
        assistant = VoiceAssistant(api_key=API_KEY)
        assistant.run()
   
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
