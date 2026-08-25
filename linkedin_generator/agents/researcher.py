from langchain_core.prompts import ChatPromptTemplate
from linkedin_generator.config import get_llm
from linkedin_generator.models import ResearchOutput
from linkedin_generator.prompts import RESEARCH_AGENT_PROMPT

def run_researcher() -> ResearchOutput:
    llm = get_llm()
    # Using structured output. Some local models might need specific prompting for JSON
    structured_llm = llm.with_structured_output(ResearchOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_AGENT_PROMPT),
        ("user", "Please generate 10 emerging topics for technology leaders.")
    ])
    
    chain = prompt | structured_llm
    
    response = chain.invoke({})
    return response
