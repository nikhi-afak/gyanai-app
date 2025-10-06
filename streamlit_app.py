import streamlit as st
import os
import base64
from io import BytesIO
import requests
import re

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
    ["English", "Hindi", "Kannada"]
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
st.header("🎤 Voice Input")
voice_html = """
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px;">
    <div style="text-align: center;">
        <button onclick="startRec()" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 16px; margin: 5px; cursor: pointer;">🎤 START</button>
        <button onclick="stopRec()" style="background: #f44336; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 16px; margin: 5px; cursor: pointer;">⏹️ STOP</button>
    </div>
    <div id="status" style="text-align: center; padding: 15px; background: white; border-radius: 10px; margin: 15px 0;">Ready</div>
    <div id="output" style="padding: 15px; background: white; border-radius: 10px; min-height: 80px;">Your text here...</div>
</div>
<script>
let rec; let txt = '';
function startRec() {
    if (!('webkitSpeechRecognition' in window)) { document.getElementById('status').innerHTML = 'Not supported'; return; }
    rec = new webkitSpeechRecognition(); rec.continuous = true; rec.interimResults = true;
    rec.onstart = () => { document.getElementById('status').innerHTML = 'Recording...'; };
    rec.onresult = (e) => { let final = ''; for (let i = e.resultIndex; i < e.results.length; i++) { if (e.results[i].isFinal) final += e.results[i][0].transcript + ' '; } if (final) { txt = final.trim(); document.getElementById('output').innerHTML = txt; } };
    rec.onend = () => { document.getElementById('status').innerHTML = 'Done'; };
    rec.start();
}
function stopRec() { if (rec) rec.stop(); }
</script>
"""
st.components.v1.html(voice_html, height=300)

st.header("💬 Question")
question = st.text_area("Enter question:", height=100)

def translate_text(text, lang):
    if lang == "English": return text
    try:
        code = VOICE_LANGS[lang]["code"]
        r = requests.get("https://translate.googleapis.com/translate_a/single", 
                        params={'client': 'gtx', 'sl': 'en', 'tl': code, 'dt': 't', 'q': text}, timeout=10)
        return r.json()[0][0][0] if r.status_code == 200 else text
    except: return text

# THE FIX - Split into very small chunks and play sequentially
def create_voice(text, lang, name):
    if not TTS_WORKS: return
    try:
        cfg = VOICE_LANGS[lang]
        txt = text.strip()
        
        if lang != "English":
            st.info(f"Translating to {lang}...")
            txt = translate_text(txt, lang)
            st.success("Translated")
        
        st.info("Generating audio...")
        
        # Split into 100-character chunks (safe for gTTS)
        chunks = []
        words = txt.split()
        current = ""
        
        for word in words:
            if len(current) + len(word) < 100:
                current += word + " "
            else:
                if current: chunks.append(current.strip())
                current = word + " "
        if current: chunks.append(current.strip())
        
        # Generate all audio parts
        parts = []
        for chunk in chunks:
            tts = gTTS(text=chunk, lang=cfg["code"], tld=cfg["tld"], slow=False)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            parts.append(base64.b64encode(fp.read()).decode())
        
        # Create auto-playing HTML
        html = f"""
        <div style="background: #d4edda; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <h4 style="color: #155724;">{name} - {lang}</h4>
            <p id="stat-{name}" style="color: #155724;">Click play to start</p>
            <audio id="aud-{name}" controls style="width: 100%;"></audio>
        </div>
        <script>
        (function() {{
            const parts = {parts};
            let idx = 0;
            const aud = document.getElementById('aud-{name}');
            const stat = document.getElementById('stat-{name}');
            
            aud.src = 'data:audio/mp3;base64,' + parts[0];
            
            aud.onended = function() {{
                idx++;
                if (idx < parts.length) {{
                    stat.innerHTML = 'Part ' + (idx + 1) + ' of ' + parts.length;
                    aud.src = 'data:audio/mp3;base64,' + parts[idx];
                    aud.play();
                }} else {{
                    stat.innerHTML = 'Complete!';
                }}
            }};
            
            aud.onplay = function() {{
                stat.innerHTML = 'Playing part ' + (idx + 1) + ' of ' + parts.length;
            }};
        }})();
        </script>
        """
        
        st.markdown(html, unsafe_allow_html=True)
        st.success(f"Audio ready ({len(parts)} parts)")
    except Exception as e:
        st.error(f"Error: {e}")

def call_openai(q, key):
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                         json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": q}], "max_tokens": 500}, timeout=30)
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else f"Error {r.status_code}"
    except Exception as e: return f"Error: {e}"

def call_claude(q, key):
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
                         headers={"x-api-key": key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
                         json={"model": "claude-3-haiku-20240307", "max_tokens": 500, "messages": [{"role": "user", "content": q}]}, timeout=30)
        return r.json()["content"][0]["text"] if r.status_code == 200 else f"Error {r.status_code}"
    except Exception as e: return f"Error: {e}"

def call_groq(q, key):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                         json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": q}], "max_tokens": 500}, timeout=30)
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else f"Error {r.status_code}"
    except Exception as e: return f"Error: {e}"

if st.button("Get AI Responses", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Enter a question")
    else:
        st.markdown("## Responses")
        st.markdown(f"**Question:** {question}")
        st.markdown(f"**Language:** {voice_language}")
        st.markdown("---")
        
        if openai_key:
            st.markdown("### OpenAI")
            with st.spinner("Getting response..."):
                resp = call_openai(question, openai_key)
                if not resp.startswith("Error"):
                    st.success("Response received")
                    st.write(resp)
                    create_voice(resp, voice_language, "OpenAI")
                else:
                    st.error(resp)
            st.markdown("---")
        
        if anthropic_key:
            st.markdown("### Claude")
            with st.spinner("Getting response..."):
                resp = call_claude(question, anthropic_key)
                if not resp.startswith("Error"):
                    st.success("Response received")
                    st.write(resp)
                    create_voice(resp, voice_language, "Claude")
                else:
                    st.error(resp)
            st.markdown("---")
        
        if groq_key:
            st.markdown("### Groq")
            with st.spinner("Getting response..."):
                resp = call_groq(question, groq_key)
                if not resp.startswith("Error"):
                    st.success("Response received")
                    st.write(resp)
                    create_voice(resp, voice_language, "Groq")
                else:
                    st.error(resp)

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
    <h3>Gyan AI - Triple AI Integration</h3>
    <p>Voice Input | 3 AI Models | Multilingual Audio</p>
</div>
""", unsafe_allow_html=True)
