import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv # To securely load API key
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# 🔑 Get your Google Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")


if not GEMINI_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    print("Please create a .env file in the same directory as this script,")
    print("and add GOOGLE_API_KEY='AIzaSyAmeYm2c20f46DMuKWsv1uKrmKlkgye2Ug' to it.")
    exit()

# Configure Google Gemini API
genai.configure(api_key='AIzaSyAmeYm2c20f46DMuKWsv1uKrmKlkgye2Ug')

# Initialize the Gemini model
# 'gemini-pro' is a good general-purpose text model.
# You can explore other models like 'gemini-1.5-pro' or 'gemini-1.5-flash' if you have access and specific needs.
# Note: For conversational continuity, using model.start_chat() is often better.
model = genai.GenerativeModel(model_name="gemini-1.5-flash")


# Initialize engine and recognizer
engine = pyttsx3.init()
r = sr.Recognizer()

# Optional: Set voice properties for pyttsx3
# You might need to adjust these based on available voices on your system
voices = engine.getProperty('voices')
# Try to find a suitable voice, e.g., male voice on Windows or a default on Linux/macOS
try:
    # On Windows, voices[0] is often David (male), voices[1] is Zira (female)
    # You might need to check your system's installed voices
    engine.setProperty('voice', voices[0].id) 
except IndexError:
    print("Warning: Could not set a specific voice. Using default.")
engine.setProperty('rate', 170) # Adjust speech rate (words per minute)


def speak(text):
    """Converts text to speech and plays it."""
    print(f"🤖 AI: {text}") # Changed print statement for clarity
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for audio input from the microphone and converts it to text."""
    with sr.Microphone() as source:
        print("AI is Listening...")
        r.pause_threshold = 1 # Seconds of non-speaking before a phrase is considered complete
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8) # Added timeout
        except sr.WaitTimeoutError:
            print("No speech detected within timeout.")
            return ""

        try:
            query = r.recognize_google(audio)
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Didn't understand.")
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            speak("Sorry, there was an issue with my speech recognition service.")
            return ""

def ask_gemini(prompt):
    """Sends the user's prompt to the Gemini LLM and returns its text response."""
    try:
        # For a simple turn-based conversation, model.generate_content is sufficient.
        # For more complex, multi-turn conversations where the model needs to remember context,
        # you would use `chat = model.start_chat(history=[...])` and `chat.send_message(prompt)`.
        response = model.generate_content(prompt)
        # Gemini's response object might have parts, so we access the text attribute
        return response.text
    except Exception as e:
        print(f"Error talking to Gemini: {e}")
        return "I'm sorry, I couldn't connect to my brain right now."

# 🧠 Main Loop
if __name__ == "__main__":
    speak("Hello! How can I help you today?") # Initial greeting

    while True:
        command = listen()
        if command: # Only proceed if a command was recognized
            if "stop" in command.lower() or "exit" in command.lower() or "goodbye" in command.lower():
                speak("Goodbye!")
                break
            else:
                reply = ask_gemini(command)
                print("🤖 Gemini:", reply) # Changed print statement for clarity
                speak(reply)