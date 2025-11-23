import streamlit as st
import os
import time
import numpy as np
from gtts import gTTS
import speech_recognition as sr
from fuzzywuzzy import process
import google.generativeai as genai
from dotenv import load_dotenv
# from audiorecorder import audiorecorder
import base64

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Page Config
st.set_page_config(
    page_title="School Voice Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Child-Friendly Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #E0F7FA;
    }
    .main-header {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #006064;
        text-align: center;
        padding: 20px;
        background-color: #B2EBF2;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 3px solid #00BCD4;
    }
    .chat-bubble-user {
        background-color: #FFCCBC;
        color: #BF360C;
        padding: 10px 15px;
        border-radius: 20px 20px 0 20px;
        margin: 10px 0;
        text-align: right;
        font-family: 'Arial', sans-serif;
        font-size: 18px;
        max-width: 70%;
        float: right;
        clear: both;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .chat-bubble-bot {
        background-color: #C8E6C9;
        color: #1B5E20;
        padding: 10px 15px;
        border-radius: 20px 20px 20px 0;
        margin: 10px 0;
        text-align: left;
        font-family: 'Arial', sans-serif;
        font-size: 18px;
        max-width: 70%;
        float: left;
        clear: both;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #FF7043;
        color: white;
        border-radius: 50px;
        font-size: 20px;
        padding: 10px 25px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #F4511E;
        transform: scale(1.05);
    }
    .sidebar-content {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #00BCD4;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def load_faq(file_path="school-faq.txt"):
    faq = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().split("\n\n")
            for item in content:
                if "Q:" in item and "A:" in item:
                    lines = item.split("\n")
                    q = lines[0].replace("Q: ", "").strip()
                    a = lines[1].replace("A: ", "").strip()
                    faq[q] = a
    except FileNotFoundError:
        st.error("FAQ file not found. Please create 'school-faq.txt'.")
    return faq

def get_best_match(query, faq_dict):
    questions = list(faq_dict.keys())
    best_match, score = process.extractOne(query, questions)
    if score > 70:  # Threshold for fuzzy matching
        return faq_dict[best_match]
    return None

import asyncio
import edge_tts

# ... (imports)

# --- Helper Functions ---

# ... (load_faq, get_best_match)

def get_llm_response(query):
    if not GEMINI_API_KEY:
        return "Sorry, I cannot connect to the brain right now (API Key missing). Please ask a basic school question."
    try:
        available_models = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash-exp",
            "gemini-flash-latest",
            "gemini-pro"
        ]
        model = None
        for model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                # Test generation to ensure model works
                model.generate_content("test")
                break
            except:
                continue
        
        if not model:
            return "Sorry, I could not connect to any AI model. Please check your API key."

        # Updated Prompt for specific greeting
        prompt = f"You are a helpful school assistant for a school in Pakistan. You MUST start every answer with 'Assalam-o-Alaikum'. Answer this question in simple Roman Urdu or English as appropriate for a parent or child. Keep it short and friendly. Question: {query}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

import re



def speech_to_text(audio_bytes):
    r = sr.Recognizer()
    try:
        # Save bytes to a temp file for SR to read
        with open("temp_input.wav", "wb") as f:
            f.write(audio_bytes)
        
        with sr.AudioFile("temp_input.wav") as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="ur-PK") # Trying Urdu first
            return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        # Try English if Urdu fails or generic error
        try:
             with sr.AudioFile("temp_input.wav") as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                return text
        except:
            return None

# --- Main App Logic ---

def main():
    # Header
    st.markdown('<div class="main-header"><h1>🏫 MGSDO School Assistant v2.0 🎓</h1><h3>Assalam-o-Alaikum! Ask me anything! 👋</h3></div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/school-building.png", width=100)
        
        st.header("🔊 Voice Settings")
        voice_style = st.selectbox("Choose Voice", ["Woman", "Man"])
        
        st.header("📌 Quick Info")
        
        if st.button("🕒 School Timing"):
            st.info("Mon-Thu: 8:00 AM - 2:00 PM\nFri: 8:00 AM - 12:00 PM")
        
        if st.button("💰 Admission Fee"):
            st.info("Admission Fee: Rs. 5000 (Non-refundable)")
            
        if st.button("🗓️ Holidays"):
            st.info("Sunday & Gazetted Holidays are off.")
            
        if st.button("📍 Location"):
            st.info("Main Gulberg Road, Block C, near City Park.")
            
        if st.button("📞 Contact Us"):
            st.info("Phone: 0300-1234567\nEmail: info@mgsdo.edu.pk")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # FAQ Loader
    faq_data = load_faq()

    # --- Input Area ---
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown("### 🎤 Speak")
        st.caption("1. Click 'Start Recording' \n2. Speak your question \n3. Click 'Stop' to send")
        audio_bytes = st.audio_input("Record Voice")

    with col2:
        st.markdown("### ⌨️ Or Type")
        user_input = st.chat_input("Type your question here...")

    # Handle Voice Input
    if audio_bytes:
        # st.audio_input returns a UploadedFile-like object, we can read bytes
        # But st.audio_input return value is already playable in st.audio
        # We need bytes for speech_recognition
        
        # st.audio(audio_bytes) # Optional: play back what was recorded
        
        with st.spinner("Listening..."):
            # audio_bytes is a BytesIO/UploadedFile, read it
            audio_data = audio_bytes.read()
            recognized_text = speech_to_text(audio_data)
            if recognized_text:
                user_input = recognized_text
            else:
                st.warning("Could not understand audio. Please try again.")

    # Process Input
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Logic to find answer
        answer = get_best_match(user_input, faq_data)
        
        if not answer:
            with st.spinner("Thinking..."):
                answer = get_llm_response(user_input)

        # Add bot response to history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Generate Audio for the response
        audio_file = text_to_speech(answer, voice_style)
        st.session_state.latest_audio = audio_file

    # Display Chat History
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    # Play Audio for the latest response
    if "latest_audio" in st.session_state and st.session_state.latest_audio:
        st.audio(st.session_state.latest_audio, format='audio/mp3', autoplay=True)

# ... (rest of file)

import re

async def generate_edge_tts(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def text_to_speech(text, voice_style):
    try:
        # Clean text for speech
        clean_text = text
        
        # 1. Fix Greeting Pronunciation
        # "Assalam u Alaikum" sounds better in en-IN voice for Roman Urdu
        clean_text = clean_text.replace("Assalam-o-Alaikum", "Assalam u Alaikum")
        clean_text = clean_text.replace("Assalam o Alaikum", "Assalam u Alaikum")
        
        # 2. Fix Time (7:45 -> 7 baj kar 45 mint)
        # Regex to find time pattern like 7:45
        clean_text = re.sub(r'(\d{1,2}):(\d{2})', r'\1 baj kar \2 mint', clean_text)
        
        # 3. Remove AM/PM
        clean_text = clean_text.replace("AM", "").replace("PM", "").replace("am", "").replace("pm", "")
        
        # 4. Remove Special Chars
        clean_text = re.sub(r'[*_#`~]', '', clean_text) 
        clean_text = re.sub(r'[^\w\s.,?!]', '', clean_text)
        
        filename = "temp_audio.mp3"
        
        # Select Voice (Switching to Indian English for better Roman Urdu pronunciation)
        voice = "en-IN-NeerjaNeural" # Default Female
        if voice_style == "Man":
            voice = "en-IN-PrabhatNeural"
        
        # Run async edge-tts
        asyncio.run(generate_edge_tts(clean_text, voice, filename))
        
        return filename
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

if __name__ == "__main__":
    main()
