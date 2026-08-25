from langchain_core.prompts import ChatPromptTemplate
from linkedin_generator.config import get_llm
from linkedin_generator.models import PostDraft
from linkedin_generator.prompts import WRITER_AGENT_PROMPT

def run_writer(topic_title: str, topic_summary: str, feedback: str = None) -> PostDraft:
    llm = get_llm()
    structured_llm = llm.with_structured_output(PostDraft)
    
    prompt_messages = [
        ("system", WRITER_AGENT_PROMPT),
    ]
    
    user_prompt = f"Topic Title: {topic_title}\nTopic Summary: {topic_summary}\n\nPlease draft a LinkedIn post following the persona and guidelines."
    
    if feedback:
        user_prompt += f"\n\nPREVIOUS REVIEWER FEEDBACK TO INCORPORATE:\n{feedback}"
        
    prompt_messages.append(("user", user_prompt))
    
    prompt = ChatPromptTemplate.from_messages(prompt_messages)
    chain = prompt | structured_llm
    
    response = chain.invoke({})
    return response
