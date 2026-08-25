from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from linkedin_generator.models import ResearchOutput, RankingOutput, PostDraft, ReviewFeedback
from linkedin_generator.agents.researcher import run_researcher
from linkedin_generator.agents.ranker import run_ranker
from linkedin_generator.agents.writer import run_writer
from linkedin_generator.agents.reviewer import run_reviewer

class AgentState(TypedDict):
    research: Optional[ResearchOutput]
    ranking: Optional[RankingOutput]
    draft: Optional[PostDraft]
    review: Optional[ReviewFeedback]
    revision_count: int

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
    # Always take the top ranked topic
    top_topic = state["ranking"].ranked_topics[0]
    
    # Get original summary from research to provide context
    topic_summary = ""
    for t in state["research"].topics:
        if t.title == top_topic.title:
            topic_summary = t.summary
            break
            
    # Check if there is review feedback
    feedback = None
    if state.get("review") and not state["review"].approved:
        feedback = "\n".join(state["review"].rewrite_instructions)
        
    output = run_writer(top_topic.title, topic_summary, feedback)
    
    # Increment revision count if we are looping
    new_revision_count = state.get("revision_count", 0)
    if feedback:
        new_revision_count += 1
        
    return {"draft": output, "revision_count": new_revision_count}

def reviewer_node(state: AgentState):
    print("---RUNNING REVIEWER---")
    output = run_reviewer(state["draft"])
    return {"review": output}

def review_condition(state: AgentState):
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

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("ranker", ranker_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    
    workflow.set_entry_point("researcher")
    
    workflow.add_edge("researcher", "ranker")
    workflow.add_edge("ranker", "writer")
    workflow.add_edge("writer", "reviewer")
    
    workflow.add_conditional_edges(
        "reviewer",
        review_condition,
        {
            "approved": END,
            "rejected": "writer"
        }
    )
    
    return workflow.compile()
