from langchain_core.prompts import ChatPromptTemplate
from linkedin_generator.config import get_llm
from linkedin_generator.models import PostDraft, ReviewFeedback
from linkedin_generator.prompts import REVIEWER_AGENT_PROMPT

def run_reviewer(draft: PostDraft) -> ReviewFeedback:
    llm = get_llm()
    structured_llm = llm.with_structured_output(ReviewFeedback)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEWER_AGENT_PROMPT),
        ("user", "Please review the following LinkedIn post draft:\n\nTopic: {topic}\n\nPost Content:\n{post}\n\nHashtags: {hashtags}")
    ])
    
    chain = prompt | structured_llm
    
    response = chain.invoke({
        "topic": draft.topic,
        "post": draft.post,
        "hashtags": ", ".join(draft.hashtags)
    })
    
    return response
