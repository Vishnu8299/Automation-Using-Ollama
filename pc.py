import speech_recognition as sr
import pyttsx3
import threading
import subprocess
import requests
import webbrowser
import time

# Constants
API_KEY = "83f7a716186b459f8cb9d1c6af4ca8ef"
WAKE_WORD = "ok jarvis"
SPEECH_RATE = 150  # Adjust speech rate
VOICE_ID = None  # Use None to select default voice

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', SPEECH_RATE)

# Set voice if desired (uncomment and specify index for desired voice)
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[VOICE_ID].id)

# A lock to prevent concurrent access to the speech engine
speak_lock = threading.Lock()

def speak(text):
    """Convert text to speech."""
    with speak_lock:
        engine.say(text)
        engine.runAndWait()

def listen_for_wake_word(timeout=5):
    """Listen for the wake word."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for the wake word...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except sr.RequestError:
            print("Error connecting to the recognition service.")
            speak("Connection issue.")
            return None

def listen_for_command():
    """Listen for a command after the wake word is detected."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for command...")
        try:
            audio = recognizer.listen(source, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Error connecting to the recognition service.")
            speak("Could not connect to the recognition service.")
            return None

def fetch_news(query):
    """Fetch latest news headlines from a news API based on a user query."""
    encoded_query = requests.utils.quote(query)
    url = f"https://newsapi.org/v2/everything?q={encoded_query}&apiKey={API_KEY}"
    
    try:
        response = requests.get(url)
        news_data = response.json()

        if response.status_code == 200 and news_data.get('articles'):
            headlines = [article['title'] for article in news_data['articles'][:5]]
            return headlines
        else:
            return ["Sorry, I couldn't find any news on that topic."]
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return ["Sorry, I could not fetch the news."]

def read_news(topic):
    """Read news headlines aloud."""
    headlines = fetch_news(topic)
    speak(f"Here are the latest news headlines on {topic}.")
    
    for headline in headlines:
        speak(headline)
        time.sleep(1)  # Short pause between headlines

def google_search(query):
    """Perform a Google search."""
    speak(f"Searching Google for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak("Here are the search results.")

def open_application(app_name):
    """Open a specified application based on the command."""
    speak(f"Opening {app_name}.")
    try:
        if "notepad" in app_name:
            subprocess.Popen("notepad.exe")
        elif "calculator" in app_name:
            subprocess.Popen("calc.exe")
        else:
            speak(f"Sorry, I cannot open {app_name}.")
    except FileNotFoundError:
        speak(f"Could not find the application {app_name}.")
    except Exception as e:
        speak(f"An error occurred: {e}")

def execute_command(command):
    """Execute commands based on user input."""
    if command is None:
        return
    
    if "news" in command:
        topic = command.replace("search for", "").replace("news", "").strip()
        if topic:
            read_news(topic)
        else:
            speak("Please specify a topic for the news.")
    elif "search for" in command:
        query = command.replace("search for", "").strip()
        google_search(query)
    elif "open" in command:
        app_name = command.replace("open", "").strip()
        open_application(app_name)
    elif "exit" in command:
        speak("Goodbye!")
        return "exit"
    else:
        speak("I'm sorry, I didn't understand that command. Please try again.")

def main():
    """Main function to run the voice assistant."""
    speak("Voice assistant activated. Say 'ok jarvis' to wake me.")
    
    while True:
        wake_word = listen_for_wake_word()
        
        if wake_word and WAKE_WORD in wake_word:
            speak("Yes, how can I help you?")
            command = listen_for_command()  # Listen for actual command after wake word
            
            # Execute command and check if the exit command was given
            if execute_command(command) == "exit":
                break

if __name__ == "__main__":
    main()
