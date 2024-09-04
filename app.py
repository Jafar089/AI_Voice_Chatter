import streamlit as st
import openai
import speech_recognition as sr
import pyttsx3
import threading
import json

# Set OpenAI API key
openai.api_key = "your_openai_api"

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize conversation history in session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Function to capture audio
def listen_to_query():
    with sr.Microphone() as source:
        st.write("Listening for your query...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."

# Function to get a response from ChatGPT using gpt-3.5-turbo
def get_gpt_response(query):
    # Add the user query to the conversation history
    st.session_state.conversation_history.append({"role": "user", "content": query})
    
    # Get response from GPT without limiting characters
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.conversation_history,
        max_tokens=2000,  # Max tokens can be set higher, GPT will auto limit based on context length
        temperature=0.5
    )
    
    answer = response['choices'][0]['message']['content'].strip()

    # Add the GPT response to the conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": answer})
    
    return answer

# Function to speak the response in a separate thread
def speak_response(response):
    def speak():
        engine = pyttsx3.init()
        engine.say(response)
        engine.runAndWait()

    # Run the speech synthesis in a new thread to avoid conflicts
    threading.Thread(target=speak).start()

# Streamlit UI
st.title("ChatBot with Voice Input and Output")

# Display past conversation history
st.write("### Conversation History")
if st.session_state.conversation_history:
    for message in st.session_state.conversation_history:
        role = "You" if message["role"] == "user" else "ChatGPT"
        st.write(f"**{role}:** {message['content']}")

# Button to interact with the chatbot
if st.button("Talk to Chatbot"):
    query = listen_to_query()
    if query:
        st.write(f"You said: {query}")
        response = get_gpt_response(query)
        st.write(f"ChatGPT says: {response}")
        speak_response(response)

# Add a button to clear conversation
if st.button("Clear Conversation"):
    st.session_state.conversation_history.clear()
    st.write("Conversation cleared!")

# Function to convert chat history to JSON for download
def convert_history_to_text():
    conversation_text = ""
    for message in st.session_state.conversation_history:
        role = "You" if message["role"] == "user" else "ChatGPT"
        conversation_text += f"{role}: {message['content']}\n\n"
    return conversation_text

# Button to download chat history
if st.button("Download Chat History"):
    chat_history_text = convert_history_to_text()
    st.download_button(label="Download Chat History", data=chat_history_text, file_name="chat_history.txt", mime="text/plain")
