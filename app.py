import streamlit as st
import time
from linkedin_generator.graph import build_graph

st.set_page_config(
    page_title="LinkedIn Content Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0d0f1a 0%, #0a0d1f 50%, #060811 100%);
    min-height: 100vh;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Header ─────────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 200px;
    background: radial-gradient(ellipse, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 40%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin: 0 0 0.75rem;
}
.hero-sub {
    color: #64748b;
    font-size: 1rem;
    font-weight: 400;
    margin: 0;
}

/* ── Agent Cards ─────────────────────────────────────────────── */
.agents-row {
    display: flex;
    gap: 1rem;
    margin: 2rem 0 1.5rem;
    justify-content: center;
}
.agent-card {
    flex: 1;
    max-width: 220px;
    background: rgba(15,18,36,0.8);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
}
.agent-card.active {
    border-color: rgba(99,102,241,0.6);
    box-shadow: 0 0 30px rgba(99,102,241,0.2), inset 0 0 20px rgba(99,102,241,0.05);
    background: rgba(30,33,60,0.9);
}
.agent-card.done {
    border-color: rgba(34,197,94,0.4);
    box-shadow: 0 0 20px rgba(34,197,94,0.1);
}
.agent-icon {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
}
.agent-name {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 0.3rem;
}
.agent-card.active .agent-name { color: #a5b4fc; }
.agent-card.done .agent-name { color: #4ade80; }
.agent-status {
    font-size: 0.7rem;
    color: #475569;
}
.agent-card.active .agent-status { color: #818cf8; }
.agent-card.done .agent-status { color: #22c55e; }

/* ── Generate Button ─────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    width: 100%;
    padding: 1rem 2rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: white;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    letter-spacing: 0.03em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(99,102,241,0.35), 0 1px 0 rgba(255,255,255,0.1) inset;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
    box-shadow: 0 6px 32px rgba(99,102,241,0.5);
    transform: translateY(-1px);
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0);
}

/* ── Result Card ─────────────────────────────────────────────── */
.result-card {
    background: rgba(15,18,36,0.85);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.75rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 40px rgba(99,102,241,0.08);
    animation: fadeUp 0.5s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-topic {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #818cf8;
    margin-bottom: 0.4rem;
}
.result-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.post-text {
    color: #cbd5e1;
    font-size: 0.92rem;
    line-height: 1.8;
    white-space: pre-wrap;
}
.hashtags {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.hashtag {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
}

/* ── Score Panel ─────────────────────────────────────────────── */
.score-panel {
    background: rgba(15,18,36,0.85);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.75rem;
    margin-top: 1.5rem;
    backdrop-filter: blur(12px);
    animation: fadeUp 0.5s ease 0.1s backwards;
}
.score-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 1rem;
}
.score-number {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4ade80, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.score-denom { font-size: 1rem; color: #475569; font-weight: 400; }
.approved-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.3);
    color: #4ade80;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    margin: 0.75rem 0 1.25rem;
}
.strength-item {
    background: rgba(255,255,255,0.04);
    border-left: 3px solid #818cf8;
    color: #94a3b8;
    font-size: 0.82rem;
    padding: 0.5rem 0.75rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
}

/* ── Divider ─────────────────────────────────────────────────── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
    margin: 1.5rem 0;
}

/* ── Progress bar ────────────────────────────────────────────── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    border-radius: 999px;
}

/* ── Text area ───────────────────────────────────────────────── */
textarea {
    background: rgba(10,13,31,0.7) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    color: #cbd5e1 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #818cf8 !important; }

/* Success / Info */
div[data-testid="stAlert"] {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #a5b4fc !important;
    border-radius: 12px !important;
}

/* ── Topic Input ─────────────────────────────────────────────── */
.topic-input-wrap {
    max-width: 700px;
    margin: 0 auto 1.5rem;
}
.topic-input-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.topic-mode-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.topic-mode-badge.auto {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    color: #818cf8;
}
.topic-mode-badge.custom {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.3);
    color: #4ade80;
}
div[data-testid="stTextInput"] input {
    background: rgba(10,13,31,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "app" not in st.session_state:
    st.session_state.app = build_graph()
if "result" not in st.session_state:
    st.session_state.result = None
if "agent_states" not in st.session_state:
    st.session_state.agent_states = {"research": "idle", "rank": "idle", "write": "idle", "review": "idle"}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ Powered by GenAI</div>
    <h1 class="hero-title">LinkedIn Content Generator</h1>
    <p class="hero-sub">Executive thought leadership posts from the perspective of an Architect</p>
</div>
""", unsafe_allow_html=True)

# ── Agent Status Row ──────────────────────────────────────────────────────────
agents = [
    ("🔍", "Research", "Gathers trending topics"),
    ("📊", "Rank", "Scores & selects top topics"),
    ("✍️", "Write", "Drafts the post"),
    ("⭐", "Review", "Reviews & approves"),
]

states = st.session_state.agent_states

def agent_card_html(icon, name, desc, state):
    cls = "active" if state == "active" else ("done" if state == "done" else "")
    status_text = "Running..." if state == "active" else ("Complete ✓" if state == "done" else "Waiting")
    return f"""
    <div class="agent-card {cls}">
        <div class="agent-icon">{icon}</div>
        <div class="agent-name">{name}</div>
        <div class="agent-status">{status_text}</div>
    </div>"""

agents_html = '<div class="agents-row">' + "".join(
    agent_card_html(icon, name, desc, states[key])
    for (icon, name, desc), key in zip(agents, ["research","rank","write","review"])
) + "</div>"
agents_placeholder = st.empty()
agents_placeholder.markdown(agents_html, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Topic Input ───────────────────────────────────────────────────────────────
col_l, col_mid, col_r = st.columns([1, 3, 1])
with col_mid:
    user_topic_input = st.text_input(
        label="Topic (optional)",
        placeholder="e.g. AI governance in enterprise, Technical debt as business risk, Future of work...",
        help="Leave blank to let the system automatically discover and rank the best topic.",
        label_visibility="visible",
    )
    if user_topic_input.strip():
        st.markdown('<span class="topic-mode-badge custom">✦ Custom Topic Mode</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="topic-mode-badge auto">⚙ Auto-Discover Mode</span>', unsafe_allow_html=True)

# ── Generate Button ───────────────────────────────────────────────────────────
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    generate_btn = st.button("⚡  Generate LinkedIn Post", use_container_width=True)

# ── Status placeholder ────────────────────────────────────────────────────────
status_placeholder = st.empty()

# ── Results Area ──────────────────────────────────────────────────────────────
results_placeholder = st.empty()

# ── Generation Logic ──────────────────────────────────────────────────────────
def render_agents(active_key=None, done_keys=None):
    done_keys = done_keys or []
    def get_state(k):
        if k == active_key: return "active"
        if k in done_keys: return "done"
        return "idle"
    html = '<div class="agents-row">' + "".join(
        agent_card_html(icon, name, desc, get_state(key))
        for (icon, name, desc), key in zip(agents, ["research","rank","write","review"])
    ) + "</div>"
    agents_placeholder.markdown(html, unsafe_allow_html=True)

def render_results(draft, review):
    post_body = draft.post
    tags_html = "".join(f'<span class="hashtag">{h}</span>' for h in draft.hashtags)
    score = review.overall_score if review else "N/A"
    approved = review.approved if review else False
    strengths = review.strengths if review else []

    strength_items = "".join(f'<div class="strength-item">{s}</div>' for s in strengths[:5])

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-topic">Generated Post</div>
            <div class="result-title">📌 {draft.topic}</div>
            <div class="post-text">{post_body}</div>
            <div class="hashtags">{tags_html}</div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: space-between; font-size: 0.75rem; color: #64748b;">
                <div><strong>Provider:</strong> <span style="color: #a5b4fc;">{draft.provider}</span></div>
                <div><strong>Model:</strong> <span style="color: #a5b4fc;">{draft.model_name}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Copy-friendly text area
        st.text_area("📋 Copy Post Text", value=draft.post + "\n\n" + " ".join(draft.hashtags),
                     height=180, label_visibility="visible")

    with c2:
        badge = '<span class="approved-badge">✓ Approved</span>' if approved else '<span class="approved-badge" style="border-color:rgba(251,191,36,0.3);background:rgba(251,191,36,0.1);color:#fbbf24;">⚠ Max Revisions</span>'
        st.markdown(f"""
        <div class="score-panel">
            <div class="score-label">Reviewer Score</div>
            <div class="score-number">{score}<span class="score-denom">/10</span></div>
            {badge}
            <div class="score-label" style="margin-top:1rem;">Strengths</div>
            {strength_items}
        </div>
        """, unsafe_allow_html=True)

if generate_btn:
    st.session_state.result = None
    done = []
    user_topic = user_topic_input.strip()

    # Decide which steps to animate based on whether topic was provided
    if user_topic:
        # Skip research & rank — go straight to write & review
        active_steps = [
            ("write",  "✍️ Writer Agent is crafting your post on: " + user_topic + "..."),
            ("review", "⭐ Reviewer Agent is evaluating the post..."),
        ]
        # Mark research & rank as skipped (show as done/grey)
        render_agents(active_key="write", done_keys=[])
    else:
        active_steps = [
            ("research", "🔍 Research Agent is gathering trending topics..."),
            ("rank",     "📊 Ranking Agent is scoring topics..."),
            ("write",    "✍️ Writer Agent is crafting your post..."),
            ("review",   "⭐ Reviewer Agent is evaluating the post..."),
        ]

    initial_state = {
        "user_topic": user_topic or None,
        "research": None,
        "ranking": None,
        "draft": None,
        "review": None,
        "revision_count": 0,
    }

    try:
        with st.spinner(""):
            for step_key, step_msg in active_steps:
                render_agents(active_key=step_key, done_keys=done)
                status_placeholder.info(step_msg)
                time.sleep(0.3)

            final_state = st.session_state.app.invoke(initial_state)

            all_done = ["research", "rank", "write", "review"]
            render_agents(done_keys=all_done)
            status_placeholder.success("✅ Post generated and approved!")

            draft = final_state.get("draft")
            review = final_state.get("review")

            if draft:
                st.session_state.result = (draft, review)
            else:
                st.error("Failed to generate draft. Check your LM Studio connection.")

    except Exception as e:
        status_placeholder.error(f"❌ Error: {e}")
        render_agents()

# ── Show previous result if available ────────────────────────────────────────
if st.session_state.result:
    draft, review = st.session_state.result
    render_results(draft, review)
