import streamlit as st
from rca_agent import run_rca

st.set_page_config(page_title="RCA Agent", layout="wide", page_icon="🤖")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #f4f6f9;
    color: #1a2332;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.0rem 2rem; max-width: 1400px; }

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
    border-radius: 12px;
    padding: 1.5rem 2.4rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.8rem;
    box-shadow: 0 4px 20px rgba(26,35,50,0.2);
}

.hero-left { display: flex; align-items: center; gap: 1.2rem; }
.hero-icon { font-size: 2.6rem; }

.hero-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f5f0e8;
    margin: 0;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    color: #c9b99a;
    font-size: 0.80rem;
    margin: 0.25rem 0 0 0;
    letter-spacing: 0.02em;
}

/* Pipeline strip */
.pipeline-strip {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 10px;
    padding: 1.1rem 1.1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 6px rgba(26,35,50,0.06);
    display: flex;
    align-items: center;
    justify-content: center;
}

.ps-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
}

.ps-bubble {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    border: 2px solid #d1d9e0;
    background: #f9fafb;
    color: #8a9bb0;
}

.ps-bubble.done {
    border-color: #1a2332;
    background: #1a2332;
    color: #c9b99a;
    box-shadow: 0 2px 10px rgba(26,35,50,0.2);
}

.ps-label {
    font-size: 0.67rem;
    color: #6b7c93;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.ps-label.done { color: #1a2332; }

.ps-connector {
    width: 50px;
    height: 2px;
    background: #d1d9e0;
    margin-bottom: 1.4rem;
}

.ps-connector.done { background: #1a2332; }

/* hide stray empty label above file uploader */
.stFileUploader label { display: none !important; }



.panel-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #6b7c93;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}

# /* Textarea */
# .stTextArea textarea {
#     background: #f9fafb !important;
#     border: 1px solid #dde3ea !important;
#     border-radius: 8px !important;
#     color: #1a2332 !important;
#     font-family: 'Courier New', monospace !important;
#     font-size: 0.82rem !important;
# }

# .stTextArea textarea:focus {
#     border-color: #1a2332 !important;
#     box-shadow: 0 0 0 3px rgba(26,35,50,0.08) !important;
# }

/* File uploader */
.stFileUploader > div {
    background: #f9fafb !important;
    border: 1px dashed #c9b99a !important;
    border-radius: 8px !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #1a2332, #2d3f55) !important;
    color: #f5f0e8 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 3px 12px rgba(26,35,50,0.25) !important;
    letter-spacing: 0.02em !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(26,35,50,0.35) !important;
}

/* Result cards */
.result-card {
    background: #ffffff;
    border: 1px solid #dde3ea;
    border-radius: 10px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 0rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 6px rgba(26,35,50,0.06);
}

.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}

.card-analysis::before  { background: #1a2332; }
.card-hypothesis::before { background: #c9b99a; }
.card-validation::before { background: #4a7c59; }
.card-fix::before        { background: #8b4513; }

.card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.9rem;
}

.card-icon { font-size: 1.1rem; }

.card-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6b7c93;
}

.card-content {
    color: #2c3e50;
    font-size: 0.88rem;
    line-height: 1.75;
    white-space: pre-wrap;
}

/* Badges */
.badge-valid {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #eaf4ec;
    border: 1px solid #a8d5b0;
    color: #2e6b3e;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-size: 0.84rem;
    font-weight: 600;
}

.badge-invalid {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #fdf0ed;
    border: 1px solid #e8b4a8;
    color: #8b2e20;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-size: 0.84rem;
    font-weight: 600;
}

.tool-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: #f0ece4;
    border: 1px solid #c9b99a;
    color: #6b5a3e;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.76rem;
    font-weight: 600;
    margin-top: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f4f6f9; }
::-webkit-scrollbar-thumb { background: #c9b99a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #1a2332; }
</style>
""", unsafe_allow_html=True)

# ── Pipeline HTML helper ──────────────────────────────────────────────────────
def pipeline_html(done=False):
    steps = [("🔍","Analyze"),("💡","Hypothesis"),("🔧","Tool Select"),("✅","Validate"),("🛠","Fix")]
    html = '<div class="pipeline-strip">'
    for i, (icon, label) in enumerate(steps):
        cls = "done" if done else ""
        html += f'<div class="ps-step"><div class="ps-bubble {cls}">{icon}</div><span class="ps-label {cls}">{label}</span></div>'
        if i < len(steps) - 1:
            html += f'<div class="ps-connector {cls}"></div>'
    html += '</div>'
    return html

# ── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-left">
        <div class="hero-icon">🤖</div>
        <div>
            <p class="hero-title">RCA Intelligence Agent</p>
            <p class="hero-subtitle">AI-powered root cause analysis &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; Groq LLM &nbsp;·&nbsp; Dynamic tool routing</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Pipeline Strip (full width, between hero and content) ─────────────────────
done = "result" in st.session_state
st.markdown(pipeline_html(done), unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1.6], gap="large")

with left:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📂 Input</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload log file", type=["txt", "log"], label_visibility="collapsed")
    error_text = ""
    if uploaded_file:
        error_text = uploaded_file.read().decode("utf-8")

    error_text = st.text_area(
        "Paste error log",
        value=error_text,
        height=170,
        placeholder="Paste your error log or stack trace here...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    analyze_clicked = st.button("🔎  Run Analysis", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
with right:
    if analyze_clicked:
        if not error_text.strip():
            st.warning("⚠️ Please provide a log input to analyze.")
        else:
            with st.spinner("Agent is thinking..."):
                result = run_rca(error_text)
            st.session_state.result = result
            st.rerun()

    if "result" in st.session_state:
        r = st.session_state.result

        tool_icons = {"kafka": "📨", "api": "🌐", "file": "📄", "unknown": "❓"}
        tool = r.get("selected_tool", "unknown")
        tool_icon = tool_icons.get(tool, "🔧")

        st.markdown(f"""
        <div class="result-card card-analysis">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <span class="card-title">Log Analysis</span>
            </div>
            <div class="card-content">{r['analysis']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card card-hypothesis">
            <div class="card-header">
                <span class="card-icon">🧠</span>
                <span class="card-title">Root Cause Hypothesis</span>
            </div>
            <div class="card-content">{r['hypothesis']}</div>
            <div class="tool-tag">{tool_icon} Verified via: {tool.upper()} tool</div>
        </div>
        """, unsafe_allow_html=True)

        valid_badge = (
            '<span class="badge-valid">✅ Root Cause Confirmed</span>'
            if r["is_valid"]
            else '<span class="badge-invalid">⚠️ Root Cause Not Confirmed</span>'
        )
        st.markdown(f"""
        <div class="result-card card-validation">
            <div class="card-header">
                <span class="card-icon">🔬</span>
                <span class="card-title">Validation Result</span>
            </div>
            {valid_badge}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card card-fix">
            <div class="card-header">
                <span class="card-icon">🛠</span>
                <span class="card-title">Suggested Fix</span>
            </div>
            <div class="card-content">{r['fix']}</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="height:calc(110vh - 220px);overflow-y:auto;border:1px dashed #c9b99a;
            border-radius:10px;background:#ffffff;display:flex;flex-direction:column;
            align-items:center;justify-content:center;color:#6b7c93;text-align:center;gap:1rem;">
            <div style="font-size:3rem;opacity:0.5;">🤖</div>
            <div style="font-size:1rem;font-weight:600;color:#1a2332;">Awaiting log input</div>
            <div style="font-size:0.82rem;color:#8a9bb0;">Upload a log file or paste an error trace<br>and click <strong style='color:#1a2332'>Run Analysis</strong></div>
        </div>
        """, unsafe_allow_html=True)
