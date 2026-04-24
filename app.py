# app.py
#sync test
# sync test workinggit
import streamlit as st
from backend import process_query, EduMindMemory
from langchain_groq import ChatGroq
import os
from rag import extract_text, create_vectorstore
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

# ============================================
# 1. PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="EduMind AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. DESIGN SYSTEM
# ============================================
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');
    :root {
        --primary: #4338ca;
        --primary-light: #EEF2FF;
        --surface: #f9f9fb;
        --white: #ffffff;
        --on-surface: #111827;
        --border: #e5e7eb;
        --text-muted: #6B7280;
        --success: #059669;
        --warning: #d97706;
    }
    .stApp { background-color: var(--surface) !important; color: var(--on-surface) !important; font-family: 'Inter', sans-serif !important; }
    h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; }
    [data-testid="stHeader"] { background: transparent !important; border: none !important; }
    [data-testid="stHeader"] > div > div:nth-child(2) { display: none !important; } /* Hide Deploy/Menu buttons */

    /* ANIMATED DOUBLE-ARROW TOGGLE (<< / >>) */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #2d2d4a !important;
        border-radius: 8px !important;
        border: 1px solid #4338ca !important;
        opacity: 1 !important;
        visibility: visible !important;
        transition: all 0.3s ease !important;
        width: 34px !important;
        height: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { display: none !important; } /* Hide default icon */
    [data-testid="stSidebarCollapseButton"]::after {
        content: "«" !important;
        color: #a5b4fc !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: block !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background-color: #4338ca !important;
        box-shadow: 0 0 15px rgba(67, 56, 192, 0.4) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover::after {
        transform: translateX(-3px) !important;
        color: white !important;
    }

    /* EXPAND BUTTON (>>) WHEN CLOSED */
    [data-testid="stHeader"] button[aria-label="Expand sidebar"], 
    button[aria-label="Expand sidebar"] {
        background-color: #1a1a2e !important;
        border: 2px solid #4338ca !important;
        border-radius: 8px !important;
        width: 40px !important;
        height: 40px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        visibility: visible !important;
        opacity: 1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stHeader"] button[aria-label="Expand sidebar"] svg,
    button[aria-label="Expand sidebar"] svg { display: none !important; }
    
    [data-testid="stHeader"] button[aria-label="Expand sidebar"]::after,
    button[aria-label="Expand sidebar"]::after {
        content: "»" !important;
        color: #a5b4fc !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: block !important;
        line-height: 1 !important;
    }
    [data-testid="stHeader"] button[aria-label="Expand sidebar"]:hover,
    button[aria-label="Expand sidebar"]:hover {
        background-color: #4338ca !important;
        box-shadow: 0 0 20px rgba(67, 56, 192, 0.6) !important;
    }
    [data-testid="stHeader"] button[aria-label="Expand sidebar"]:hover::after,
    button[aria-label="Expand sidebar"]:hover::after {
        transform: translateX(4px) !important;
        color: white !important;
    }
    [data-testid="stChatMessage"] { background: transparent !important; border: none !important; }
    #MainMenu, footer { display: none !important; }

    /* DARK SIDEBAR like ChatGPT */
    [data-testid="stSidebar"] { background-color: #1a1a2e !important; border-right: 1px solid #2d2d4a !important; width: 260px !important; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important; color: #9ca3af !important;
        border-radius: 8px !important; border: none !important;
        font-weight: 500 !important; text-align: left !important;
        font-size: 0.82rem !important; text-transform: none !important;
        letter-spacing: 0 !important; padding: 8px 12px !important;
        transition: all 0.15s !important; justify-content: flex-start !important;
        display: flex !important; align-items: center !important; gap: 10px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover { background-color: #2d2d4a !important; color: #e2e8f0 !important; }
    
    /* SLEEK SESSION ROW */
    .session-row {
        border-radius: 8px !important;
        margin-bottom: 2px !important;
        transition: background 0.1s !important;
        background-color: transparent !important;
    }
    .session-row:hover { background-color: rgba(255,255,255,0.03) !important; }
    
    .session-row.active-session {
        background-color: #2d2d4a !important;
        border-left: 3px solid #4338ca !important;
    }
    
    /* Make buttons inside row purely text so they blend in natively */
    .session-row [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important; row-gap: 0 !important;
    }
    .session-row button {
        background-color: transparent !important;
        border: none !important; box-shadow: none !important;
        border-radius: 0 !important; min-height: 28px !important;
        height: auto !important; padding: 6px 10px !important;
    }
    .session-row button:hover { background: transparent !important; }
    
    /* Active styling pushes strictly to font color */
    .session-row.active-session button, .session-row.active-session button p {
        color: white !important; font-weight: 600 !important;
    }
    
    /* Delete button styling (cross) */
    .session-row [data-testid="column"]:nth-child(2) button,
    .session-row [data-testid="column"]:nth-child(2) button * {
        color: #8b92a5 !important;
        font-weight: 800 !important;
        background-color: transparent !important;
        background: transparent !important;
        align-items: center !important; justify-content: center !important;
    }
    .session-row [data-testid="column"]:nth-child(2) button:hover,
    .session-row [data-testid="column"]:nth-child(2) button:hover * {
        color: #ef4444 !important; /* light red on hover */
        background-color: transparent !important;
        background: transparent !important;
    }

    /* SIDEBAR COLLAPSE/EXPAND BUTTON — always visible */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #2d2d4a !important;
        border-radius: 6px !important;
        border: 1px solid #3d3d5a !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { color: #a5b4fc !important; fill: #a5b4fc !important; }

    /* SIDEBAR EXPAND BUTTON when closed */
    button[kind="header"] {
        background-color: #1a1a2e !important;
        border: 1px solid #2d2d4a !important;
        border-radius: 6px !important;
        opacity: 1 !important;
    }

    /* FILE UPLOADER — clearly visible on dark sidebar */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: #12122a !important;
        border: 2px dashed #4338ca !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] * {
        color: #c7d2fe !important;
    }
    /* Upload button */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #4338ca !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-size: 0.78rem !important;
        padding: 6px 14px !important;
        font-weight: 700 !important;
        width: 100% !important;
        display: block !important;
    }
    /* Enforce white text on upload button */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button *,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
        color: white !important;
    }
    /* Upload drag text */
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span {
        color: #a5b4fc !important;
        font-size: 0.75rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: #6b7280 !important;
        font-size: 0.65rem !important;
    }

    /* AGENT CARDS — readable on dark background */
    .agent-card {
        padding: 7px 9px !important;
        border-radius: 6px !important;
        margin: 3px 0 !important;
        font-size: 0.73rem !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    .agent-card span { color: inherit !important; }

    /* MAIN & RIGHT SIDEBAR */
    .block-container { 
        max-width: 1200px !important; padding-top: 24px !important; 
        padding-bottom: 12rem !important; margin: 0 auto !important; 
        padding-right: 280px !important; /* Shift for right sidebar */
    }
    
    .right-sidebar-target { display: none !important; }
    [data-testid="stVerticalBlock"]:has(> .element-container:nth-child(1) .right-sidebar-target) {
        position: fixed !important; top: 0 !important; right: 0 !important;
        width: 260px !important; height: 100vh !important;
        background-color: #1a1a2e !important; border-left: 1px solid #2d2d4a !important;
        padding: 55px 12px 10px 12px !important; z-index: 100 !important;
        overflow-y: auto !important;
    }
    
    /* Make chat input not clip into right sidebar */
    .stChatInput {
        padding-right: 265px !important;
    }

    /* MESSAGES */
    .user-message {
        max-width: 78%; margin-left: auto; background: white;
        padding: 12px 16px; border-radius: 18px; border-top-right-radius: 4px;
        color: var(--on-surface); margin-bottom: 16px; font-size: 0.93rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid var(--border);
    }
    .ai-bubble { display: flex; gap: 10px; margin-bottom: 20px; align-items: flex-start; }
    .ai-icon {
        width: 30px; height: 30px; background: var(--primary); border-radius: 6px;
        display: flex; align-items: center; justify-content: center; color: white;
        flex-shrink: 0; margin-top: 2px; font-size: 13px; font-weight: 800;
        font-family: 'Manrope', sans-serif;
    }
    .ai-content { flex: 1; font-size: 0.93rem; line-height: 1.7; color: var(--on-surface); }

    /* AGENT BOXES */
    .agent-output-box {
        background: white; border: 1px solid var(--border);
        border-left: 3px solid var(--primary); border-radius: 10px;
        padding: 12px 16px; margin: 8px 0;
    }
    .agent-output-label {
        font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; color: var(--primary); margin-bottom: 8px;
    }

    /* AGENT STATUS */
    .agent-card { padding: 7px 9px; border-radius: 6px; margin: 3px 0; font-size: 0.73rem; border: 1px solid rgba(255,255,255,0.06); }

    /* INPUT */
    .stChatInput > div {
        background: white !important; border-radius: 18px !important;
        border: 1.5px solid var(--border) !important;
        box-shadow: 0 4px 25px rgba(0,0,0,0.08) !important; padding: 12px 14px !important;
    }

    /* STEP CARDS */
    .step-card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 16px 12px; text-align: center; flex: 1; min-width: 120px; }
    .step-number { background: var(--primary); color: white; width: 24px; height: 24px; border-radius: 999px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.78rem; margin: 0 auto 8px auto; }

    /* MODEL SELECTBOX OVERLAP HACK */
    .pull-down {
        margin-bottom: -68px !important;
        margin-left: 16px !important;
        position: relative !important;
        z-index: 99999 !important;
        width: 165px !important;
        pointer-events: auto !important;
    }
    
    .pull-down [data-testid="stSelectbox"] > div > div {
        background: #EEF2FF !important; border: 1.5px solid transparent !important;
        border-radius: 999px !important; color: #4338ca !important;
        font-size: 0.8rem !important; font-weight: 700 !important;
        min-height: 42px !important; padding: 0 14px !important; height: 42px !important;
    }
    
    /* Make room in the chat input for the absolute overlay */
    .stChatInput textarea {
        padding-left: 195px !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 3. MODELS + AGENTS
# ============================================
AVAILABLE_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "DeepSeek R1": "deepseek-r1-distill-llama-70b",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768"
}

AGENTS = [
    ("Analyzer Agent", "Understands query depth and topic"),
    ("Question Generator", "Creates exam questions from RAG"),
    ("Evaluator Agent", "Scores answers and gives feedback"),
    ("Structure & Polish Agent", "Formats and details responses"),
    ("Summarizer Agent", "Condenses long text into short summaries"),
]

# ============================================
# 4. SESSION STATE
# ============================================
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]
if "selected_model" not in st.session_state:
    st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]

def get_current_session():
    sid = st.session_state.current_session_id
    if sid and sid in st.session_state.sessions:
        return st.session_state.sessions[sid]
    return {"title": "New Chat", "chat": [], "memory": EduMindMemory()}

def create_new_session():
    sid = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.sessions[sid] = {
        "title": "New Chat",
        "chat": [],
        "memory": EduMindMemory(),
        "vectorstore": None,
        "processed_file": None,
        "num_chunks": 0
    }
    st.session_state.current_session_id = sid
    return sid

def update_session_title(sid, first_message, llm=None):
    if sid in st.session_state.sessions:
        if llm:
            try:
                # Ask AI for a short descriptive title (ChatGPT style)
                prompt = (
                    "System: You are a creative assistant. "
                    "Generate a 2 or 3 word title for a chat conversation that starts with the user message below. "
                    "The title should be professional and relevant. Output ONLY the title text, no quotes or punctuation.\n\n"
                    f"User Message: {first_message}"
                )
                response = llm.invoke(prompt)
                title = response.content.strip().strip('"').strip("'").split('\n')[0]
            except Exception as e:
                title = first_message[:28] + "..."
        else:
            title = first_message[:28] + "..."
        st.session_state.sessions[sid]["title"] = title

if not st.session_state.current_session_id:
    create_new_session()

# ============================================
# 5. AGENT STATUS
# ============================================
def update_agent_status(agent_placeholder, active=None, done=[]):
    html = '<div style="display:flex; flex-direction:column; gap:3px; margin-top:6px;">'
    for name, desc in AGENTS:
        if name in done:
            html += f"""<div style="padding:7px 9px; border-radius:6px; margin:2px 0; background:rgba(5,150,105,0.2); border:1px solid rgba(52,211,153,0.4);">
                <div style="display:flex; align-items:center; gap:5px;">
                    <span style="color:#34d399; font-size:9px;">●</span>
                    <span style="font-weight:600; color:#6ee7b7; font-size:0.72rem;">{name}</span>
                    <span style="margin-left:auto; font-size:0.6rem; color:#34d399; font-weight:700; background:rgba(5,150,105,0.3); padding:1px 5px; border-radius:3px;">DONE</span>
                </div></div>"""
        elif name == active:
            html += f"""<div style="padding:7px 9px; border-radius:6px; margin:2px 0; background:rgba(99,102,241,0.25); border:1px solid rgba(165,180,252,0.5);">
                <div style="display:flex; align-items:center; gap:5px;">
                    <span style="color:#a5b4fc; font-size:9px;">●</span>
                    <span style="font-weight:600; color:#c7d2fe; font-size:0.72rem;">{name}</span>
                    <span style="margin-left:auto; font-size:0.6rem; color:#a5b4fc; font-weight:700; background:rgba(99,102,241,0.3); padding:1px 5px; border-radius:3px;">RUNNING</span>
                </div></div>"""
        else:
            html += f"""<div style="padding:7px 9px; border-radius:6px; margin:2px 0; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);">
                <div style="display:flex; align-items:center; gap:5px;">
                    <span style="color:#4b5563; font-size:9px;">●</span>
                    <span style="font-weight:500; color:#6b7280; font-size:0.72rem;">{name}</span>
                    <span style="margin-left:auto; font-size:0.6rem; color:#4b5563; font-weight:600; background:rgba(255,255,255,0.05); padding:1px 5px; border-radius:3px;">IDLE</span>
                </div></div>"""
    html += '</div>'
    agent_placeholder.markdown(html, unsafe_allow_html=True)

# ============================================
# 6. SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 4px 10px 4px;">
        <div style="font-size:1.05rem; font-weight:800; color:#a5b4fc;">EduMind AI</div>
        <div style="font-size:0.6rem; color:#4b5563; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-top:2px;">RAG + Agents + Memory</div>
    </div>""", unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True, key="new_chat"):
        create_new_session()
        st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # (Chat history moved to right sidebar)

    # Upload
    current_session = get_current_session()

    # RAG status
    st.markdown("""<div style="font-size:0.6rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#374151; padding:6px 4px 3px 4px;">RAG Pipeline</div>""", unsafe_allow_html=True)
    if current_session.get("vectorstore"):
        st.markdown(f"""<div style="background:rgba(5,150,105,0.1); border:1px solid rgba(52,211,153,0.25); border-radius:7px; padding:7px 9px; font-size:0.72rem;"><span style="color:#34d399; font-weight:700;">● Active</span><br><span style="color:#6b7280;">{current_session.get('processed_file')}</span><br><span style="color:#6b7280;">{current_session.get('num_chunks')} chunks</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:rgba(217,119,6,0.08); border:1px solid rgba(217,119,6,0.25); border-radius:7px; padding:7px 9px; font-size:0.72rem;"><span style="color:#fbbf24; font-weight:700;">● No document</span><br><span style="color:#6b7280;">Upload notes to activate</span></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px; border-top:1px solid #2d2d4a; margin-top:6px;'></div>", unsafe_allow_html=True)

    # Agent pipeline
    st.markdown("""<div style="font-size:0.6rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#374151; padding:6px 4px 3px 4px;">Agent Pipeline</div>""", unsafe_allow_html=True)
    agent_placeholder = st.empty()
    update_agent_status(agent_placeholder)

    # Memory
    current_session = get_current_session()
    memory = current_session.get("memory", EduMindMemory())
    memory_status = memory.get_status()
    st.markdown("<div style='height:6px; border-top:1px solid #2d2d4a; margin-top:6px;'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.6rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#374151; padding:6px 4px 3px 4px;">Memory</div>""", unsafe_allow_html=True)
    if memory_status["topic"]:
        topic_short = str(memory_status["topic"])[:28] + "..." if len(str(memory_status["topic"])) > 28 else memory_status["topic"]
        st.markdown(f"""<div style="background:rgba(67,56,202,0.1); border:1px solid rgba(99,102,241,0.25); border-radius:7px; padding:7px 9px; font-size:0.72rem;"><span style="color:#818cf8; font-weight:700;">● Active</span><br><span style="color:#6b7280;">{topic_short}</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="border:1px solid #2d2d4a; border-radius:7px; padding:7px 9px; font-size:0.72rem;"><span style="color:#374151; font-weight:600;">● Empty</span></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="font-size:0.65rem; color:#374151; padding:12px 4px 4px 4px;">Built by Vasvi Bali | v2.0</div>""", unsafe_allow_html=True)

# ============================================
# 8. HEADER
# ============================================
st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem; padding-top:4px;">
    <span style="background:#EEF2FF; color:#4338ca; border-radius:999px; padding:3px 10px; font-size:0.62rem; font-weight:800; text-transform:uppercase; letter-spacing:1px;">RAG + MicroAgents + Memory</span>
    <h1 style="font-size:3.2rem; font-weight:900; margin:8px 0 5px 0; color:#111827; letter-spacing:-1px;">EduMind AI</h1>
    <p style="color:#6B7280; font-size:0.87rem; margin:0;">Upload study notes and get exam ready with AI agents</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 8. RIGHT SIDEBAR (HISTORY)
# ============================================
right_sidebar = st.container()
with right_sidebar:
    st.markdown('<span class="right-sidebar-target"></span>', unsafe_allow_html=True)
    st.markdown("""<div style="font-size:1.05rem; font-weight:800; color:#a5b4fc; padding-bottom:12px; margin-bottom:8px; border-bottom:1px solid #2d2d4a;">Chat History</div>""", unsafe_allow_html=True)
    if st.session_state.sessions:
        for sid in reversed(list(st.session_state.sessions.keys())):
            session = st.session_state.sessions[sid]
            title = session.get("title", "New Chat")
            is_active = sid == st.session_state.current_session_id
            label = f"{title}"
            row_class = "session-row active-session" if is_active else "session-row"
            st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.88, 0.12])
            with col1:
                if st.button(label, key=f"sess_{sid}", use_container_width=True):
                    st.session_state.current_session_id = sid
                    st.rerun()
            with col2:
                if st.button("✕", key=f"del_{sid}", help="Delete Chat"):
                    del st.session_state.sessions[sid]
                    if st.session_state.current_session_id == sid:
                        st.session_state.current_session_id = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 9. CURRENT SESSION DATA
# ============================================
current_session = get_current_session()
current_chat = current_session.get("chat", [])
current_memory = current_session.get("memory", EduMindMemory())

# ============================================
# 10. LANDING PAGE
# ============================================
if not current_chat:
    st.markdown("""
    <div style="background:white; border:1px solid #e5e7eb; border-radius:14px; padding:24px; margin-bottom:1.5rem;">
        <h3 style="text-align:center; color:#374151; margin-bottom:18px; font-size:1rem;">How to use EduMind AI</h3>
        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">
            <div class="step-card"><div class="step-number">1</div><div style="font-weight:700; margin-bottom:3px; font-size:0.82rem;">Upload Notes</div><div style="color:#6B7280; font-size:0.75rem;">PDF or Word from sidebar</div></div>
            <div class="step-card"><div class="step-number">2</div><div style="font-weight:700; margin-bottom:3px; font-size:0.82rem;">Select Model</div><div style="color:#6B7280; font-size:0.75rem;">Choose AI model below</div></div>
            <div class="step-card"><div class="step-number">3</div><div style="font-weight:700; margin-bottom:3px; font-size:0.82rem;">Ask Questions</div><div style="color:#6B7280; font-size:0.75rem;">Ask or request exam prep</div></div>
            <div class="step-card"><div class="step-number">4</div><div style="font-weight:700; margin-bottom:3px; font-size:0.82rem;">Get Evaluated</div><div style="color:#6B7280; font-size:0.75rem;">Submit answers for scoring</div></div>
        </div>
        <div style="margin-top:16px; background:#EEF2FF; border-radius:8px; padding:10px 14px; font-size:0.8rem; color:#4338ca;">
            <b>Try:</b> "Generate 5 exam questions" &nbsp;•&nbsp; "Explain the main concepts" &nbsp;•&nbsp; "Grade my answer: [your answer]"
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 11. CHAT HISTORY
# ============================================
for msg in current_chat:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble"><div class="ai-icon">E</div><div class="ai-content">{msg["content"]}</div></div>', unsafe_allow_html=True)

# ============================================
# 12. MODEL SELECTOR ABOVE INPUT
# ============================================
st.markdown('<div class="pull-down">', unsafe_allow_html=True)
selected_model = st.selectbox(
    "model",
    options=list(AVAILABLE_MODELS.keys()),
    index=list(AVAILABLE_MODELS.keys()).index(st.session_state.selected_model),
    label_visibility="collapsed",
    key="model_selector"
)
st.session_state.selected_model = selected_model
model_id = AVAILABLE_MODELS[selected_model]
st.markdown('</div>', unsafe_allow_html=True)

prompt = st.chat_input("Message EduMind AI...", accept_file=True, file_type=["pdf", "docx"])

# ============================================
# 13. PROCESS QUERY & FILE
# ============================================
if prompt:
    sid = st.session_state.current_session_id
    session = st.session_state.sessions[sid]

    # Handle file upload if any
    if prompt.files:
        uploaded_file = prompt.files[0]
        if session.get("processed_file") != uploaded_file.name:
            with st.spinner("Processing through RAG pipeline..."):
                text = extract_text(uploaded_file)
                vectorstore, num_chunks = create_vectorstore(text)
                session["processed_file"] = uploaded_file.name
                session["vectorstore"] = vectorstore
                session["num_chunks"] = num_chunks
            st.success(f"RAG Ready — {num_chunks} chunks indexed")
            
    query = prompt.text
    if query:
        if session["title"] == "New Chat":
            # Pass model_id to update_session_title for AI naming
            llm_temp = ChatGroq(
                model=model_id,
                temperature=0.3,
                api_key=os.environ.get("GROQ_API_KEY")
            )
            update_session_title(sid, query, llm=llm_temp)

        session["chat"].append({"role": "user", "content": query})
        st.markdown(f'<div class="user-message">{query}</div>', unsafe_allow_html=True)

        with st.spinner("EduMind is thinking..."):
            update_agent_status(agent_placeholder, active="Analyzer Agent")
            time.sleep(0.3)

            llm = ChatGroq(
                model=model_id,
                temperature=0.3,
                api_key=os.environ.get("GROQ_API_KEY")
            )

            result = process_query(
                query,
                session.get("vectorstore"),
                session["memory"],
                llm
            )

            agents_used = result.get("agents_used", [])
            update_agent_status(agent_placeholder, done=agents_used)

        intent = result.get("intent", "")
        final_html = ""

        # Intent tag
        if intent and intent not in ["GENERAL_CHAT", "NONE"]:
            intent_colors = {"QUIZ": "#EEF2FF", "EVALUATE": "#ECFDF5", "EXPLAIN": "#FEF3C7", "GENERAL": "#F9FAFB"}
            ic = intent_colors.get(intent, "#F9FAFB")
            agents_str = " → ".join(agents_used) if agents_used else "None"
            final_html += f"""<div style="background:{ic}; border-radius:5px; padding:3px 9px; margin-bottom:7px; font-size:0.65rem; color:#6B7280; font-weight:600;">Orchestrator: <b>{intent}</b> | {agents_str}</div>"""

        if result.get("questions"):
            final_html += f"""<div class="agent-output-box" style="border-left-color:#4338ca;"><div class="agent-output-label">Question Generator Agent</div><div style="white-space:pre-line; font-size:0.9rem;">{result['questions']}</div></div>"""

        if result.get("answer"):
            if agents_used and "Structure" in " ".join(agents_used):
                label = "Structure & Polish Agent"
                label_color = "#059669"
            elif agents_used and "Summarizer" in " ".join(agents_used):
                label = "Summarizer Agent"
                label_color = "#059669"
            else:
                label = "EduMind AI"
                label_color = "#4338ca"
                
            final_html += f"""<div class="agent-output-box" style="border-left-color:{label_color};"><div class="agent-output-label" style="color:{label_color};">{label}</div><div style="white-space:pre-line; font-size:0.9rem;">{result['answer']}</div></div>"""

        if result.get("evaluation"):
            final_html += f"""<div class="agent-output-box" style="border-left-color:#d97706;"><div class="agent-output-label" style="color:#d97706;">Evaluator Agent</div><div style="white-space:pre-line; font-size:0.9rem;">{result['evaluation']}</div></div>"""

        st.markdown(f'<div class="ai-bubble"><div class="ai-icon">E</div><div class="ai-content">{final_html}</div></div>', unsafe_allow_html=True)
        session["chat"].append({"role": "assistant", "content": final_html})
