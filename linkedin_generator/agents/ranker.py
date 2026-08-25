from langchain_core.prompts import ChatPromptTemplate
from linkedin_generator.config import get_llm
from linkedin_generator.models import ResearchOutput, RankingOutput
from linkedin_generator.prompts import RANKING_AGENT_PROMPT

def run_ranker(research_output: ResearchOutput) -> RankingOutput:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RankingOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RANKING_AGENT_PROMPT),
        ("user", "Here are the topics to score and rank:\n\n{topics}")
    ])
    
    chain = prompt | structured_llm
    
    # Format topics for the prompt
    topics_text = ""
    for idx, t in enumerate(research_output.topics):
        topics_text += f"Topic {idx+1}:\nTitle: {t.title}\nSummary: {t.summary}\nWhy Relevant: {t.why_relevant}\n\n"
        
    response = chain.invoke({"topics": topics_text})
    return response
