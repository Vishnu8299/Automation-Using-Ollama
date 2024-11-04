from langchain_ollama import OllamaLLM
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from threading import Thread
import os

# Initialize the model
model = OllamaLLM(model="llama3.2")

# Initialize the text-to-speech engine
tts_engine = pyttsx3.init()

# Set up tkinter window for displaying responses
root = tk.Tk()
root.title("JARVIS Response")
root.geometry("300x200")
root.resizable(False, False)
response_label = tk.Label(root, text="", wraplength=280, justify="left")
response_label.pack(pady=20, padx=10)
root.withdraw()  # Start hidden

# Conversation log file
conversation_file = "conversation_log.txt"
history_limit = 5  # Number of previous exchanges to use as context

# Load previous conversation history
def load_conversation_history():
    history = []
    if os.path.exists(conversation_file):
        with open(conversation_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines[-2*history_limit:]:  # Keep last `history_limit` user-assistant pairs
                history.append(line.strip())
    return "\n".join(history)

# Write conversation to file
def write_conversation(user_input, response):
    with open(conversation_file, "a", encoding="utf-8") as file:
        file.write(f"User: {user_input}\nAssistant: {response}\n")

# Display response in tkinter window
def display_response(text):
    response_label.config(text=text)
    root.deiconify()  # Show window
    root.after(5000, root.withdraw)  # Hide after 5 seconds

# Convert voice input to text
def get_text_from_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak_text("Listening for your voice input...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            speak_text("Sorry, I didn't catch that. Could you repeat?")
        except sr.RequestError:
            speak_text("Network error. Please check your connection.")
        except sr.WaitTimeoutError:
            speak_text("No input detected. Try speaking again.")
    return ""  # Return empty string if no valid input

# Speak out the assistant's response
def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Main conversation handling function
def handle_conversation():
    speak_text("Welcome, boss. How can I assist you?")
    
    # Show previous conversation history if any
    previous_conversation = load_conversation_history()
    if previous_conversation:
        display_response("Previous Conversations:\n" + previous_conversation)

    while True:
        user_input = get_text_from_voice()  # Get voice input

        if user_input.lower() == "bye":
            speak_text("Goodbye! Exiting the chat.")
            root.quit()  # Close the tkinter window
            break

        if not user_input.strip():
            continue  # Ignore empty input

        # Prepare context for model response
        conversation_history = load_conversation_history()
        prompt = f"{conversation_history}\nUser: {user_input}\nAssistant:"

        try:
            response = model.invoke(prompt)  # Get model response
        except Exception as e:
            response = "I'm having trouble processing that. Please try again."
            print("Model Error:", e)

        # Log conversation and speak response
        write_conversation(user_input, response)
        speak_text(response)

        # Display response if requested by user
        if "show response" in user_input.lower():
            display_response(response)

# Start conversation in a separate thread for tkinter responsiveness
def start_conversation():
    conversation_thread = Thread(target=handle_conversation, daemon=True)
    conversation_thread.start()

# Run script
if __name__ == "__main__":
    start_conversation()
    root.mainloop()
