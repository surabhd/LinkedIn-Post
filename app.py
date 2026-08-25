import streamlit as st
from linkedin_generator.graph import build_graph

st.set_page_config(page_title="LinkedIn Content Generator", page_icon="📈", layout="wide")

st.title("📈 Multi-Agent LinkedIn Content Generator")
st.markdown("Generate executive-level LinkedIn thought leadership posts from the perspective of a Principal Architect.")

# Initialize session state for workflow app
if "app" not in st.session_state:
    st.session_state.app = build_graph()

if "final_post" not in st.session_state:
    st.session_state.final_post = None
    
if "topic" not in st.session_state:
    st.session_state.topic = None

if "review" not in st.session_state:
    st.session_state.review = None

def run_generator():
    st.session_state.final_post = None
    
    initial_state = {
        "research": None,
        "ranking": None,
        "draft": None,
        "review": None,
        "revision_count": 0
    }
    
    with st.spinner("Agents are researching, ranking, drafting, and reviewing... Please wait."):
        try:
            final_state = st.session_state.app.invoke(initial_state)
            draft = final_state.get("draft")
            review = final_state.get("review")
            
            if draft:
                st.session_state.final_post = draft.post + "\n\n" + " ".join(draft.hashtags)
                st.session_state.topic = draft.topic
                st.session_state.review = review
            else:
                st.error("Failed to generate draft.")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

col1, col2 = st.columns([1, 2])

with col1:
    st.info("Make sure LM Studio is running on localhost:1234 with your model loaded.")
    if st.button("Generate New LinkedIn Post", type="primary", use_container_width=True):
        run_generator()

with col2:
    if st.session_state.final_post:
        st.subheader(f"Topic: {st.session_state.topic}")
        st.text_area("Final Post", value=st.session_state.final_post, height=400)
        
        if st.session_state.review:
            st.markdown("### Executive Reviewer Feedback")
            st.metric(label="Review Score", value=f"{st.session_state.review.overall_score}/10")
            if st.session_state.review.approved:
                st.success("Status: Approved")
            else:
                st.warning("Status: Max Revisions Reached")
                
            if st.session_state.review.strengths:
                st.markdown("**Strengths:**")
                for s in st.session_state.review.strengths:
                    st.markdown(f"- {s}")
