import streamlit as st
from PyPDF2 import PdfReader
from groq import Groq
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os

# Constants
GROQ_API_KEY = "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"
MODEL = "gemma2-9b-it"
USER_CREDENTIALS = {"teacher#7242": "log123", "student#1513": "log123"}  # You can update or extend this dictionary

# Page Configuration
st.set_page_config(page_title="सारथी.ai", page_icon="🌍", layout="wide")

# Styling
def apply_styling():
    st.markdown("""
        <style>
        * { font-size: 16px !important; }
        .main-header { font-size: 16px !important; font-weight: bold; text-align: center; color: #4a4a4a; }
        .sub-header, .powered-by, .section-header, .sidebar-header, .sidebar-subheader {
            font-size: 16px !important; text-align: center; color: #6e6e6e; margin: 10px 0;
        }
        .upload-section { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 15px; }
        .stButton button { width: 100%; font-size: 16px !important; }
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-header {
            text-align: center;
            font-size: 24px !important;
            color: #4a4a4a;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styling()

# Groq client
@st.cache_resource
def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)

groq_client = get_groq_client()

# Session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None

# Login page
def login():
    # Create a centered container for the login form
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown('<h2 class="login-header">🔐Login</h2>', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

# If not authenticated, show login page
if not st.session_state.authenticated:
    # Add a header before the login form
    st.markdown('<h1 class="main-header">🤖 सारथी.ai</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">MULTIMODAL AI-ASSISTANT</p>', unsafe_allow_html=True)
    st.markdown('<p class="powered-by">Powered by <b>mlsquare</b></p>', unsafe_allow_html=True)
    
    login()
    st.stop()

# --- Sidebar Tools ---
with st.sidebar:
    st.markdown('<p class="sidebar-header">सारथी.ai Tools</p>', unsafe_allow_html=True)

    st.markdown('<p class="sidebar-subheader">Select a Tool</p>', unsafe_allow_html=True)
    task_options = [
        '📝 Auto-Grader',
        '🧾 Summarize Document',
        '🌐 Translate Content',
        '🎙️ Transcript Generation',
        '📊 Rubric Generation'
    ]
    selected_task = st.selectbox("Choose a task", task_options, label_visibility="collapsed", key="tool_selector")

    # File uploader
    pdf_file = st.file_uploader("🗂️", type=["pdf"])

    try:
        if pdf_file:
            with open('report.txt', 'r') as file:
                text_content = file.read()
            with open('snapshot.png', 'rb') as img_file:
                img_content = img_file.read()

            st.download_button("📄 Download Report", text_content, "report.txt", "text/plain")
            st.download_button("🔵 Download Snapshot of KB", img_content, "snapshot.png", "image/png")
    except FileNotFoundError as e:
        st.warning(f"File not found: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    with st.expander("🫂 About सारथी.ai", expanded=False):
        st.write(""" 
        सारथी.ai is a multimodal AI assistant designed to help teachers with various tasks like grading, summarization, translations, transcript creation, and more.
        Powered by **mlsquare**
        """)

# --- Main Area ---
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    st.markdown('<h1 class="main-header">🤖 सारथी.ai</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">MULTIMODAL AI-ASSISTANT FOR TEACHERS</p>', unsafe_allow_html=True)
    st.markdown('<p class="powered-by">Powered by <b>mlsquare</b></p>', unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant":
                    try:
                        tts = gTTS(text=msg["content"], lang="hi")
                        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(temp_audio_file.name)
                        st.audio(temp_audio_file.name, format="audio/mp3")
                    except Exception as e:
                        st.error(f"Audio error: {str(e)}")

    chat_input_container = st.container()
    with chat_input_container:
        input_col, voice_col = st.columns([6, 1])
        with input_col:
            user_input = st.chat_input("Type your query here...")
        with voice_col:
            voice_button = st.button("🎙️", key="voice_input")

    # Voice input
    if voice_button:
        with st.spinner("Listening... Speak now"):
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=5)
                    query = recognizer.recognize_google(audio, language="hi-IN")
                    st.session_state.messages.append({"role": "user", "content": query})
                    with st.chat_message("user"):
                        st.markdown(query)

                    with st.chat_message("assistant"):
                        with st.spinner("Generating response..."):
                            completion = groq_client.chat.completions.create(
                                model=MODEL,
                                messages=st.session_state.messages
                            )
                            reply = completion.choices[0].message.content
                            st.markdown(reply)

                            tts = gTTS(text=reply, lang="hi")
                            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                            tts.save(temp_audio_file.name)
                            st.audio(temp_audio_file.name, format="audio/mp3")

                            st.download_button("📥 Download Response", reply, "saarthi_voice_response.txt", "text/plain")
                            st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Speech recognition failed: {e}")

    # Text input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Special case for PPT
        if user_input.lower() == "generate a ppt on chapter real numbers":
            ppt_path = "Real Number.pptx"
            if os.path.exists(ppt_path):
                with open(ppt_path, "rb") as file:
                    st.download_button(
                        label="📄 Download PPT",
                        data=file,
                        file_name="Real Number.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                    st.success("Real Numbers PPT is ready for download!")
            else:
                st.error("PPT file not found. Please upload it to the working directory.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        completion = groq_client.chat.completions.create(
                            model=MODEL,
                            messages=st.session_state.messages
                        )
                        reply = completion.choices[0].message.content
                        st.markdown(reply)

                        tts = gTTS(text=reply, lang="hi")
                        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(temp_audio_file.name)
                        st.audio(temp_audio_file.name, format="audio/mp3")

                        st.download_button("📥 Download Response", reply, "saarthi_response.txt", "text/plain")
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Response generation failed: {e}")