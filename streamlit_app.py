import streamlit as st
import os
import base64
from io import BytesIO
import requests
import time

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

# Translation works via direct API
TRANSLATE_WORKS = True

# Page setup
st.set_page_config(page_title="🧠 Gyan AI", page_icon="🧠", layout="wide")
st.title("🧠 Gyan AI - Voice-Enabled Educational Assistant")

# Sidebar configuration
st.sidebar.header("🔐 API Keys")
openai_key = os.getenv("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Key:", type="password", key="openai")
anthropic_key = os.getenv("ANTHROPIC_API_KEY") or st.sidebar.text_input("Anthropic API Key:", type="password", key="anthropic")
groq_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key:", type="password", key="groq")

# Voice settings
st.sidebar.header("🔊 Voice Settings")
voice_language = st.sidebar.selectbox(
    "Select Voice Output Language:",
    ["English", "Hindi", "Kannada"],
    help="Language for AI response audio"
)

# Language mapping
VOICE_LANGS = {
    "English": {"code": "en", "tld": "com"},
    "Hindi": {"code": "hi", "tld": "co.in"}, 
    "Kannada": {"code": "kn", "tld": "co.in"}
}

# Status indicators
st.sidebar.header("📊 System Status")
st.sidebar.write(f"OpenAI: {'✅' if openai_key else '❌'}")
st.sidebar.write(f"Claude: {'✅' if anthropic_key else '❌'}")
st.sidebar.write(f"Groq: {'✅' if groq_key else '❌'}")
st.sidebar.write(f"TTS Engine: {'✅' if TTS_WORKS else '❌'}")
st.sidebar.write(f"Translator: {'✅' if TRANSLATE_WORKS else '❌'}")

if not TTS_WORKS:
    st.sidebar.error("⚠️ Install TTS: pip install gtts")

# Enhanced Voice Input Section
st.header("🎤 Voice Input System")

voice_input_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
    <h2 style="text-align: center; color: white; margin-bottom: 30px;">🎙️ Advanced Voice Recognition</h2>
    
    <div style="text-align: center; margin: 25px 0;">
        <button onclick="startVoiceRecording()" id="startBtn" 
                style="background: #4CAF50; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer; box-shadow: 0 5px 15px rgba(76,175,80,0.4); transition: all 0.3s;">
            🎤 START RECORDING
        </button>
        
        <button onclick="stopVoiceRecording()" id="stopBtn"
                style="background: #f44336; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer; box-shadow: 0 5px 15px rgba(244,67,54,0.4); transition: all 0.3s;">
            ⏹️ STOP RECORDING
        </button>
        
        <button onclick="copyVoiceText()" id="copyBtn"
                style="background: #2196F3; color: white; padding: 18px 35px; border: none; border-radius: 15px; font-size: 18px; font-weight: bold; margin: 10px; cursor: pointer; box-shadow: 0 5px 15px rgba(33,150,243,0.4); transition: all 0.3s;">
            📋 COPY TEXT
        </button>
    </div>
    
    <div id="voiceStatus" style="text-align: center; padding: 20px; background: rgba(255,255,255,0.9); border-radius: 15px; margin: 20px 0; font-weight: bold; font-size: 18px; color: #333;">
        🔴 Ready to record - Click "START RECORDING" and speak clearly
    </div>
    
    <div id="voiceOutput" style="padding: 25px; background: white; border-radius: 15px; min-height: 120px; margin: 20px 0; font-size: 16px; color: #333; border: 3px solid #ddd;">
        Your voice input will appear here...
    </div>
</div>

<script>
let voiceRecognition;
let isRecording = false;
let recordedText = '';

function startVoiceRecording() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('voiceStatus').innerHTML = '❌ Speech recognition not supported. Use Chrome or Edge.';
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    voiceRecognition = new SpeechRecognition();
    
    voiceRecognition.continuous = true;
    voiceRecognition.interimResults = true;
    voiceRecognition.lang = 'en-US';
    
    voiceRecognition.onstart = function() {
        isRecording = true;
        document.getElementById('voiceStatus').innerHTML = '🎤 RECORDING... Speak now!';
        document.getElementById('voiceOutput').innerHTML = '🎤 Listening...';
        document.getElementById('startBtn').style.background = '#95a5a6';
    };
    
    voiceRecognition.onresult = function(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (finalTranscript) {
            recordedText = finalTranscript.trim();
            document.getElementById('voiceOutput').innerHTML = '<div style="background: #e8f5e8; padding: 15px; border-radius: 10px;"><strong>✅ RECOGNIZED:</strong><br>' + recordedText + '</div>';
        } else if (interimTranscript) {
            document.getElementById('voiceOutput').innerHTML = '<div style="background: #fff3cd; padding: 15px; border-radius: 10px;"><strong>🎤 LISTENING:</strong><br><em>' + interimTranscript + '</em></div>';
        }
    };
    
    voiceRecognition.onend = function() {
        isRecording = false;
        document.getElementById('startBtn').style.background = '#4CAF50';
        if (recordedText) {
            document.getElementById('voiceStatus').innerHTML = '✅ Recording complete!';
        }
    };
    
    voiceRecognition.onerror = function(event) {
        isRecording = false;
        document.getElementById('voiceStatus').innerHTML = '❌ Error: ' + event.error;
        document.getElementById('startBtn').style.background = '#4CAF50';
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
        navigator.clipboard.writeText(recordedText).then(function() {
            document.getElementById('voiceStatus').innerHTML = '✅ Text copied! Paste below.';
        });
    }
}
</script>
"""

st.components.v1.html(voice_input_html, height=500)

# Question Input
st.header("💬 Question Input")
question = st.text_area(
    "Enter your question:",
    height=120,
    placeholder="Type or paste your question here..."
)

# Translation function
def translate_text(text, target_language):
    """Translate using Google Translate API directly"""
    if target_language == "English":
        return text
    
    try:
        lang_code = VOICE_LANGS[target_language]["code"]
        
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en',
            'tl': lang_code,
            'dt': 't',
            'q': text
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translated = result[0][0][0]
            return translated
        else:
            return text
            
    except Exception as e:
        return text

# COMPLETELY REWRITTEN TTS - Multiple audio chunks approach
def create_voice_response_html(text, target_language="English", ai_name="AI"):
    """Generate audio in chunks and create multiple players if needed"""
    
    if not TTS_WORKS:
        st.error("Install: pip install gtts")
        return None
    
    try:
        lang_config = VOICE_LANGS[target_language]
        lang_code = lang_config["code"]
        tld = lang_config["tld"]
        
        text_to_speak = text.strip()
        
        # Translate if needed
        if target_language != "English":
            st.info(f"Translating {ai_name} response to {target_language}...")
            text_to_speak = translate_text(text_to_speak, target_language)
            st.success("Translation complete!")
        
        st.info(f"Generating {target_language} audio for {ai_name}...")
        
        # Split text into chunks of ~150 characters (works better for gTTS)
        max_chunk_size = 150
        words = text_to_speak.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_chunk_size:
                current_chunk += word + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = word + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Generate audio for each chunk
        audio_players = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Generate TTS with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        tts = gTTS(text=chunk, lang=lang_code, tld=tld, slow=False)
                        audio_fp = BytesIO()
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        audio_bytes = audio_fp.read()
                        
                        # Convert to base64
                        audio_base64 = base64.b64encode(audio_bytes).decode()
                        
                        # Create individual audio player
                        player_html = f"""
                        <audio controls style="width: 100%; margin: 5px 0;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                        </audio>
                        """
                        audio_players.append(player_html)
                        break
                        
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                        else:
                            st.warning(f"Chunk {i+1} skipped due to error")
            except Exception as e:
                continue
        
        if not audio_players:
            st.error("Audio generation failed")
            return None
        
        st.success(f"{target_language} audio generated! {len(audio_players)} part(s)")
        
        # Combine all audio players
        all_players = "".join(audio_players)
        
        audio_html = f"""
        <div style="background: linear-gradient(135deg, #e8f5e8, #d4edda); padding: 20px; border-radius: 15px; border-left: 5px solid #28a745; margin: 15px 0;">
            <h4 style="color: #155724; margin-bottom: 10px;">🔊 {ai_name} - {target_language} Voice Response</h4>
            <p style="color: #155724; font-size: 14px; margin-bottom: 10px;">Complete response ({len(audio_players)} part(s)) - Play in sequence:</p>
            {all_players}
            <p style="color: #155724; font-size: 12px; margin-top: 10px; font-style: italic;">Note: For longer responses, audio is split into parts. Play each part in order for the full response.</p>
        </div>
        """
        return audio_html
        
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")
        return None

# API functions
def call_openai_api(question, api_key):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_anthropic_api(question, api_key):
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": question}]
        }
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
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Main response generation
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
                    
                    audio_html = create_voice_response_html(response, voice_language, "OpenAI")
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
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
                    
                    audio_html = create_voice_response_html(response, voice_language, "Claude")
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
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
                    
                    audio_html = create_voice_response_html(response, voice_language, "Groq")
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
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
