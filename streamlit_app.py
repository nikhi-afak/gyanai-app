import streamlit as st
import os
from io import BytesIO
import requests

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

st.set_page_config(page_title="🧠 Gyan AI", page_icon="🧠", layout="wide")
st.title("🧠 Gyan AI - Voice-Enabled Educational Assistant")

# API Keys
st.sidebar.header("🔐 API Keys")
openai_key = os.getenv("OPENAI_API_KEY") or st.sidebar.text_input("OpenAI API Key:", type="password", key="openai")
anthropic_key = os.getenv("ANTHROPIC_API_KEY") or st.sidebar.text_input("Anthropic API Key:", type="password", key="anthropic")
groq_key = os.getenv("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key:", type="password", key="groq")

# Voice settings
st.sidebar.header("🔊 Voice Settings")
voice_language = st.sidebar.selectbox("Select Voice Output Language:", ["English", "Hindi", "Kannada"])

VOICE_LANGS = {
    "English": {"code": "en", "tld": "com"},
    "Hindi": {"code": "hi", "tld": "co.in"}, 
    "Kannada": {"code": "kn", "tld": "co.in"}
}

# Status
st.sidebar.header("📊 System Status")
st.sidebar.write(f"OpenAI: {'✅' if openai_key else '❌'}")
st.sidebar.write(f"Claude: {'✅' if anthropic_key else '❌'}")
st.sidebar.write(f"Groq: {'✅' if groq_key else '❌'}")
st.sidebar.write(f"TTS: {'✅' if TTS_WORKS else '❌'}")

# Question Input
st.header("💬 Question Input")
question = st.text_area("Enter your question:", height=120, placeholder="Type your question here...")

# TTS Function
def create_voice_response(text, target_language, ai_name):
    if not TTS_WORKS:
        return None
    try:
        lang_config = VOICE_LANGS[target_language]
        st.info(f"Generating {target_language} audio for {ai_name}...")
        tts = gTTS(text=text.strip(), lang=lang_config["code"], tld=lang_config["tld"], slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.success(f"{target_language} audio ready!")
        return audio_fp
    except Exception as e:
        st.error(f"Audio failed: {str(e)}")
        return None

# API Functions
def call_openai_api(q, key):
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": q}], "max_tokens": 500}, timeout=30)
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else f"❌ Error: {r.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def call_anthropic_api(q, key):
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-3-haiku-20240307", "max_tokens": 500, "messages": [{"role": "user", "content": q}]}, timeout=30)
        return r.json()["content"][0]["text"] if r.status_code == 200 else f"❌ Error: {r.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def call_groq_api(q, key):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": q}], "max_tokens": 500}, timeout=30)
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else f"❌ Error: {r.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Main
if st.button("🤖 Get AI Responses with Voice", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("⚠️ Please enter a question!")
    else:
        st.markdown("## 🤖 AI Responses")
        st.markdown(f"**Question:** {question}")
        st.markdown(f"**Voice Language:** {voice_language}")
        st.markdown("---")
        
        if openai_key:
            st.markdown("### 🔵 OpenAI GPT-3.5")
            with st.spinner("Getting OpenAI response..."):
                resp = call_openai_api(question, openai_key)
                if not resp.startswith("❌"):
                    st.success("✅ OpenAI Response received!")
                    st.write(resp)
                    audio = create_voice_response(resp, voice_language, "OpenAI")
                    if audio:
                        st.audio(audio, format='audio/mp3')
                else:
                    st.error(resp)
            st.markdown("---")
        
        if anthropic_key:
            st.markdown("### 🟣 Anthropic Claude")
            with st.spinner("Getting Claude response..."):
                resp = call_anthropic_api(question, anthropic_key)
                if not resp.startswith("❌"):
                    st.success("✅ Claude Response received!")
                    st.write(resp)
                    audio = create_voice_response(resp, voice_language, "Claude")
                    if audio:
                        st.audio(audio, format='audio/mp3')
                else:
                    st.error(resp)
            st.markdown("---")
        
        if groq_key:
            st.markdown("### 🟢 Groq Llama")
            with st.spinner("Getting Groq response..."):
                resp = call_groq_api(question, groq_key)
                if not resp.startswith("❌"):
                    st.success("✅ Groq Response received!")
                    st.write(resp)
                    audio = create_voice_response(resp, voice_language, "Groq")
                    if audio:
                        st.audio(audio, format='audio/mp3')
                else:
                    st.error(resp)

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'><h3>🧠 Gyan AI - Triple AI Integration</h3><p><strong>3 AI Models | Multilingual Audio</strong></p></div>", unsafe_allow_html=True)
