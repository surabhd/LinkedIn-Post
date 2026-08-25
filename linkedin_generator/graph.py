from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from linkedin_generator.models import ResearchOutput, RankingOutput, PostDraft, ReviewFeedback
from linkedin_generator.agents.researcher import run_researcher
from linkedin_generator.agents.ranker import run_ranker
from linkedin_generator.agents.writer import run_writer
from linkedin_generator.agents.reviewer import run_reviewer


class AgentState(TypedDict):
    # Optional user-supplied topic hint (title and/or description)
    user_topic: Optional[str]
    # Internal agent outputs
    research: Optional[ResearchOutput]
    ranking: Optional[RankingOutput]
    draft: Optional[PostDraft]
    review: Optional[ReviewFeedback]
    revision_count: int


# ── Nodes ────────────────────────────────────────────────────────────────────

def researcher_node(state: AgentState):
    print("---RUNNING RESEARCHER---")
    output = run_researcher()
    return {"research": output}


def ranker_node(state: AgentState):
    print("---RUNNING RANKER---")
    output = run_ranker(state["research"])
    return {"ranking": output}


def writer_node(state: AgentState):
    print("---RUNNING WRITER---")

    user_topic = state.get("user_topic") or ""

    if user_topic.strip():
        # ── User-provided topic: skip research/ranking ────────────────────────
        topic_title = user_topic.strip()
        topic_summary = (
            f"The user wants a post on: {topic_title}. "
            "Write about the business implications, leadership considerations, "
            "and strategic impact of this topic for technology executives."
        )
    else:
        # ── Auto-selected topic from ranker ───────────────────────────────────
        ranking = state.get("ranking")
        research = state.get("research")

        top_topic = ranking.ranked_topics[0]
        topic_title = top_topic.title
        topic_summary = ""
        if research:
            for t in research.topics:
                if t.title == top_topic.title:
                    topic_summary = t.summary
                    break

    # Check if there is review feedback from a previous loop
    feedback = None
    if state.get("review") and not state["review"].approved:
        feedback = "\n".join(state["review"].rewrite_instructions)

    output = run_writer(topic_title, topic_summary, feedback)

    new_revision_count = state.get("revision_count", 0)
    if feedback:
        new_revision_count += 1

    return {"draft": output, "revision_count": new_revision_count}


def reviewer_node(state: AgentState):
    print("---RUNNING REVIEWER---")
    output = run_reviewer(state["draft"])
    return {"review": output}


# ── Conditional routing ───────────────────────────────────────────────────────

def entry_router(state: AgentState) -> str:
    """
    At graph entry decide whether to run the full research pipeline
    or jump straight to the writer using the user-supplied topic.
    """
    user_topic = state.get("user_topic") or ""
    if user_topic.strip():
        print(f"---USER TOPIC PROVIDED: '{user_topic}' — skipping Research & Ranking---")
        return "writer"
    else:
        print("---NO TOPIC PROVIDED — running full Research & Ranking pipeline---")
        return "researcher"


def review_condition(state: AgentState) -> str:
    print("---CHECKING REVIEW DECISION---")
    review = state.get("review")
    revision_count = state.get("revision_count", 0)
    print(f"Approved: {review.approved}, Revisions: {revision_count}")

    if review.approved:
        return "approved"
    elif revision_count >= 3:
        print("Max revisions reached. Proceeding with current draft.")
        return "approved"
    else:
        return "rejected"


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("ranker", ranker_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)

    # Conditional entry point: user topic → writer, else → researcher
    workflow.set_conditional_entry_point(
        entry_router,
        {
            "researcher": "researcher",
            "writer": "writer",
        }
    )

    # Full pipeline edges
    workflow.add_edge("researcher", "ranker")
    workflow.add_edge("ranker", "writer")
    workflow.add_edge("writer", "reviewer")

    # Revision loop or end
    workflow.add_conditional_edges(
        "reviewer",
        review_condition,
        {
            "approved": END,
            "rejected": "writer",
        }
    )

    return workflow.compile()
