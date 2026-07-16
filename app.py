import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retrievia - AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0a0a0f;
    --surface: rgba(255, 255, 255, 0.045);
    --surface-2: rgba(255, 255, 255, 0.06);
    --surface-hover: rgba(255, 255, 255, 0.08);
    --border: rgba(255, 255, 255, 0.09);
    --border-strong: rgba(255, 255, 255, 0.16);
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #eaeaf4;
    --text-muted: #9494b8;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(124, 58, 237, 0.20) 0%, transparent 45%),
        radial-gradient(circle at 85% 0%, rgba(6, 182, 212, 0.14) 0%, transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(124, 58, 237, 0.10) 0%, transparent 55%),
        var(--bg) !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Hide the default Streamlit sidebar entirely */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Center the page and give it breathing room */
.block-container {
    max-width: 1180px;
    padding-top: 2.5rem !important;
    padding-bottom: 3rem !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero Title ── */
.hero-wrap {
    text-align: center;
    padding: 1.5rem 0 2rem 0;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 0.6rem;
}

/* ── Glass Card ── */
.glass-card {
    background: var(--surface);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.glass-card:hover {
    border-color: var(--border-strong);
    box-shadow:
        0 12px 40px rgba(124, 58, 237, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-glow), var(--accent-2), transparent);
    opacity: 0.6;
}

/* keep old .card class working the same as glass-card */
.card {
    background: var(--surface);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.card:hover {
    border-color: var(--border-strong);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-glow), var(--accent-2), transparent);
    opacity: 0.6;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

/* ── Control bar (replaces sidebar) ──
   Streamlit's st.markdown() divs don't actually wrap later widgets,
   so we style the REAL container instead: st.container(border=True) */
[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bar-marker) {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)),
        var(--surface) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--border-strong) !important;
    border-radius: 20px !important;
    box-shadow:
        0 10px 40px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(255, 255, 255, 0.02),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.75rem;
}

[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bar-marker) > div {
    padding: 1.75rem 2rem 1.5rem 2rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:has(.control-bar-marker)::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent-glow) 40%, var(--accent-2) 100%);
    opacity: 0.85;
    z-index: 2;
}

.control-bar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.1rem;
}

.control-bar-eyebrow {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.control-bar-eyebrow::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent-glow);
    box-shadow: 0 0 8px var(--accent-glow);
}

.field-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
    display: block;
}

/* ── Accent Badge ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 100px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    backdrop-filter: blur(6px);
}

.badge-purple { background: rgba(124,58,237,0.18); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.35); }
.badge-cyan   { background: rgba(6,182,212,0.14);  color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.35); }
.badge-green  { background: rgba(16,185,129,0.14);  color: var(--success);    border: 1px solid rgba(16,185,129,0.35); }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.045) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.stTextInput > div > div > input {
    padding: 0.65rem 0.9rem !important;
    height: 3rem !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(148, 148, 184, 0.65) !important;
}

.stTextInput > div > div > input:hover,
.stSelectbox > div > div:hover {
    border-color: var(--border-strong) !important;
    background: rgba(255, 255, 255, 0.06) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-glow) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.22) !important;
    background: rgba(255, 255, 255, 0.06) !important;
}

.stSelectbox > div > div {
    min-height: 3rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent-glow), var(--accent) 55%, #5b21b6) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    height: 3rem !important;
    padding: 0 1.5rem !important;
    transition: all 0.25s ease !important;
    text-transform: uppercase !important;
    box-shadow:
        0 6px 20px rgba(124,58,237,0.3),
        inset 0 1px 0 rgba(255,255,255,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 12px 32px rgba(124,58,237,0.45),
        inset 0 1px 0 rgba(255,255,255,0.3) !important;
    filter: brightness(1.06);
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* ── Progress / Status ── */
.status-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 1rem;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.55rem 0.9rem;
    background: var(--surface-2);
    border-radius: 100px;
    border: 1px solid var(--border);
    font-size: 0.72rem;
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done     { background: var(--success); box-shadow: 0 0 6px var(--success); }
.dot-pending  { background: var(--text-muted); opacity: 0.4; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.65rem 1rem;
    border-radius: 14px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 90%;
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble { background: rgba(124,58,237,0.16); border: 1px solid rgba(124,58,237,0.3); align-self: flex-end; }
.bot-bubble  { background: rgba(6,182,212,0.12);  border: 1px solid rgba(6,182,212,0.28);  align-self: flex-start; }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
}

/* ── Empty state hero card ── */
.empty-hero {
    background: var(--surface);
    -webkit-backdrop-filter: blur(22px) saturate(160%);
    backdrop-filter: blur(22px) saturate(160%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 4rem 2rem;
    text-align: center;
    box-shadow:
        0 12px 48px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    position: relative;
    overflow: hidden;
}

.empty-hero::before {
    content: '';
    position: absolute;
    top: -40%; left: 50%;
    transform: translateX(-50%);
    width: 60%; height: 60%;
    background: radial-gradient(circle, rgba(124,58,237,0.25) 0%, transparent 70%);
    pointer-events: none;
}

.empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 20px rgba(124,58,237,0.5));
}

.empty-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.6rem;
}

.empty-copy {
    color: var(--text-muted);
    font-size: 0.85rem;
    max-width: 420px;
    line-height: 1.8;
    margin: 0 auto;
}

.empty-badges {
    margin-top: 2rem;
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
}

/* ── Stale Streamlit elements ── */
.stProgress > div > div > div { background: var(--accent) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">🎬 Retrievia - AI Video Assistant</div>
    <div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>
</div>
""", unsafe_allow_html=True)

# ─── Control Bar (replaces sidebar) ──────────────────────────────────────────────
with st.container(border=True):
    st.markdown('<span class="control-bar-marker"></span>', unsafe_allow_html=True)

    st.markdown("""
    <div class="control-bar-header">
        <span class="control-bar-eyebrow">Session Input</span>
        <span class="badge badge-purple">Step 1 of 1</span>
    </div>
    """, unsafe_allow_html=True)

    in_col1, in_col2, in_col3 = st.columns([4, 1.3, 1], gap="medium")
    with in_col1:
        st.markdown('<span class="field-label">Youtube URL or File Path</span>', unsafe_allow_html=True)
        source = st.text_input(
            "YouTube URL or File Path",
            placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
            label_visibility="collapsed",
        )
    with in_col2:
        st.markdown('<span class="field-label">Language</span>', unsafe_allow_html=True)
        language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")
    with in_col3:
        st.markdown('<span class="field-label">&nbsp;</span>', unsafe_allow_html=True)
        run_btn = st.button("⚡ Analyse", use_container_width=True)

    if st.session_state.pipeline_done or st.session_state.pipeline_steps:
        st.markdown('<div class="status-row">', unsafe_allow_html=True)
        steps_html = []
        for step, icon, label in [
            ("audio",      "🔊", "Audio"),
            ("transcript", "📝", "Transcript"),
            ("title",      "🏷️", "Title"),
            ("summary",    "📋", "Summary"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            css = step_status(st.session_state.pipeline_steps, step)
            steps_html.append(f"""
            <div class="status-bar">
                <div class="status-dot {css}"></div>
                <span>{icon} {label}</span>
            </div>""")
        st.markdown("".join(steps_html), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — status updating above…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state — redesigned glass hero
    st.markdown("""
    <div class="empty-hero">
        <div class="empty-icon">🎬</div>
        <div class="empty-title">Ready to Analyse</div>
        <div class="empty-copy">
            Paste a YouTube URL or local file path above, choose your language, and hit
            <strong>Analyse</strong> to transcribe, summarise, and chat with your meeting.
        </div>
        <div class="empty-badges">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)