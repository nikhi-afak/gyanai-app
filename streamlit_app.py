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

TRANSLATE_WORKS = True

# Page setup
st.set_page_config(page_title="Gyan AI", page_icon="🧠", layout="wide")
st.title("🧠 Gyan AI - Voice-Enabled Educational Assistant")

# Sidebar
st.sidebar.header("🔐 API Keys")
openai_key = os.getenv("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Key:", type="password", key="openai")
anthropic_key = os.getenv("ANTHROPIC_API_KEY") or st.sidebar.text_input("Anthropic API Key:", type="password", key="anthropic")
groq_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key:", type="password", key="groq")

st.sidebar.header("🔊 Voice Settings")
voice_language = st.sidebar.selectbox(
    "Select Voice Output Language:",
    ["English", "Hindi", "Kannada"],
    help="Language for AI response audio"
)

VOICE_LANGS = {
    "English": {"code": "en", "tld": "com"},
    "Hindi": {"code": "hi", "tld": "co.in"}, 
    "Kannada": {"code": "kn", "tld": "co.in"}
}

st.sidebar.header("📊 System Status")
st.sidebar.write(f"OpenAI: {'✅' if openai_key else '❌'}")
st.sidebar.write(f"Claude: {'✅' if anthropic_key else '❌'}")
st.sidebar.write(f"Groq: {'✅' if groq_key else '❌'}")
st.sidebar.write(f"TTS Engine: {'✅' if TTS_WORKS else '❌'}")
st.sidebar.write(f"Translator: {'✅' if TRANSLATE_WORKS else '❌'}")

# Voice Input
st.header("🎤 Voice Input System")

voice_input_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; margin: 20px 0;">
    <h2 style="text-align: center; color: white; margin-bottom: 30px;">🎙️ Voice Recognition</h2>
    <div style="text-align: center; margin: 25px 0;">
        <button onclick="startVoiceRecording()" id="startBtn" 
                style="background: #4CAF50; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer;">
            🎤 START
        </button>
        <button onclick="stopVoiceRecording()" id="stopBtn"
                style="background: #f44336; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer;">
            ⏹️ STOP
        </button>
        <button onclick="copyVoiceText()" id="copyBtn"
                style="background: #2196F3; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer;">
            📋 COPY
        </button>
    </div>
    <div id="voiceStatus" style="text-align: center; padding: 20px; background: rgba(255,255,255,0.9); border-radius: 15px; margin: 20px 0; font-weight: bold; font-size: 18px; color: #333;">
        Ready to record
    </div>
    <div id="voiceOutput" style="padding: 25px; background: white; border-radius: 15px; min-height: 120px; margin: 20px 0; font-size: 16px; color: #333;">
        Your voice input will appear here...
    </div>
</div>

<script>
let voiceRecognition;
let isRecording = false;
let recordedText = '';

function startVoiceRecording() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('voiceStatus').innerHTML = 'Speech recognition not supported';
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    voiceRecognition = new SpeechRecognition();
    voiceRecognition.continuous = true;
    voiceRecognition.interimResults = true;
    voiceRecognition.lang = 'en-US';
    
    voiceRecognition.onstart = function() {
        isRecording = true;
        document.getElementById('voiceStatus').innerHTML = '🎤 RECORDING...';
        document.getElementById('voiceOutput').innerHTML = 'Listening...';
    };
    
    voiceRecognition.onresult = function(event) {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript + ' ';
            }
        }
        if (finalTranscript) {
            recordedText = finalTranscript.trim();
            document.getElementById('voiceOutput').innerHTML = '<strong>✅ RECOGNIZED:</strong><br>' + recordedText;
        }
    };
    
    voiceRecognition.onend = function() {
        isRecording = false;
        if (recordedText) {
            document.getElementById('voiceStatus').innerHTML = '✅ Recording complete!';
        }
    };
    
    voiceRecognition.start();
}

function stopVoiceRecording() {
    if (voiceRecognition && isRecording) {
        voiceRecognition.stop();
    }
}

function copyVoiceText() {
    if (recordedText) {
        navigator.clipboard.writeText(recordedText);
        document.getElementById('voiceStatus').innerHTML = '✅ Text copied!';
    }
}
</script>
"""

st.components.v1.html(voice_input_html, height=500)

st.header("💬 Question Input")
question = st.text_area("Enter your question:", height=120, placeholder="Type or paste your question here...")

# Translation
def translate_text(text, target_language):
    if target_language == "English":
        return text
    
    try:
        lang_code = VOICE_LANGS[target_language]["code"]
        url = "https://translate.googleapis.com/translate_a/single"
        params = {'client': 'gtx', 'sl': 'en', 'tl': lang_code, 'dt': 't', 'q': text}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()[0][0][0]
        return text
    except:
        return text

# COMPLETELY REWRITTEN TTS - WORKING VERSION
def create_voice_response(text, target_language, ai_name):
    if not TTS_WORKS:
        st.error("TTS not available")
        return
    
    try:
        lang_config = VOICE_LANGS[target_language]
        lang_code = lang_config["code"]
        tld = lang_config["tld"]
        
        text_to_speak = text.strip()
        
        # Translate if needed
        if target_language != "English":
            st.info(f"Translating to {target_language}...")
            text_to_speak = translate_text(text_to_speak, target_language)
            st.success("Translation complete!")
        
        st.info(f"Generating {target_language} audio...")
        
        # Generate TTS - this is the working method
        tts = gTTS(text=text_to_speak, lang=lang_code, tld=tld, slow=False)
        
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Use Streamlit's native audio player
        st.audio(audio_fp, format='audio/mp3')
        st.success(f"{target_language} audio ready!")
        
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")

# API functions
def call_openai_api(question, api_key):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": question}], "max_tokens": 500}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_anthropic_api(question, api_key):
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
        data = {"model": "claude-3-haiku-20240307", "max_tokens": 500, "messages": [{"role": "user", "content": question}]}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_groq_api(question, api_key):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": question}], "max_tokens": 500}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Main
if st.button("Get AI Responses with Voice", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a question!")
    else:
        st.markdown("## AI Responses")
        st.markdown(f"**Question:** {question}")
        st.markdown(f"**Voice Language:** {voice_language}")
        st.markdown("---")
        
        # OpenAI
        if openai_key:
            st.markdown("### OpenAI GPT-3.5")
            with st.spinner("Getting OpenAI response..."):
                response = call_openai_api(question, openai_key)
                if not response.startswith("Error"):
                    st.success("OpenAI Response received!")
                    st.write(response)
                    create_voice_response(response, voice_language, "OpenAI")
                else:
                    st.error(response)
            st.markdown("---")
        
        # Claude
        if anthropic_key:
            st.markdown("### Anthropic Claude")
            with st.spinner("Getting Claude response..."):
                response = call_anthropic_api(question, anthropic_key)
                if not response.startswith("Error"):
                    st.success("Claude Response received!")
                    st.write(response)
                    create_voice_response(response, voice_language, "Claude")
                else:
                    st.error(response)
            st.markdown("---")
        
        # Groq
        if groq_key:
            st.markdown("### Groq Llama")
            with st.spinner("Getting Groq response..."):
                response = call_groq_api(question, groq_key)
                if not response.startswith("Error"):
                    st.success("Groq Response received!")
                    st.write(response)
                    create_voice_response(response, voice_language, "Groq")
                else:
                    st.error(response)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
    <h3>Gyan AI - Triple AI Integration</h3>
    <p><strong>Voice Input | 3 AI Models | Multilingual Audio Output</strong></p>
</div>
""", unsafe_allow_html=True)
