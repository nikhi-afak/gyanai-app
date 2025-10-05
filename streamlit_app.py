import streamlit as st
import os
import base64
from io import BytesIO
import requests

# Simple imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

try:
    from gtts import gTTS
    TTS_WORKS = True
except ImportError:
    TTS_WORKS = False

# Page setup
st.set_page_config(page_title="🧠 Gyan AI", page_icon="🧠", layout="wide")
st.title("🧠 Gyan AI - Voice-Enabled Educational Assistant")

# ... (rest of your code stays the same until the TTS function)

# WORKING TTS Function
def create_voice_response(text, target_language="English", ai_name="AI"):
    """Working TTS with proper Streamlit audio player"""
    
    if not TTS_WORKS:
        st.error("Install: pip install gtts")
        return None
    
    try:
        VOICE_LANGS = {
            "English": {"code": "en", "tld": "com"},
            "Hindi": {"code": "hi", "tld": "co.in"}, 
            "Kannada": {"code": "kn", "tld": "co.in"}
        }
        
        lang_config = VOICE_LANGS[target_language]
        
        st.info(f"Generating {target_language} audio for {ai_name}...")
        
        # Generate TTS
        tts = gTTS(text=text.strip(), lang=lang_config["code"], tld=lang_config["tld"], slow=False)
        
        # Save to BytesIO
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        st.success(f"{target_language} audio ready!")
        
        return audio_fp
        
    except Exception as e:
        st.error(f"Audio failed: {str(e)}")
        return None

# Then in your response sections, use:
audio_fp = create_voice_response(response, voice_language, "OpenAI")
if audio_fp:
    st.audio(audio_fp, format='audio/mp3')
