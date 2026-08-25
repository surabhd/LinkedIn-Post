from pydantic import BaseModel, Field
from typing import List

class Topic(BaseModel):
    title: str = Field(description="The title of the topic")
    summary: str = Field(description="A brief summary of the topic")
    sources: List[str] = Field(description="List of sources for this topic")
    why_relevant: str = Field(description="Why this is relevant for technology leaders and the business")

class ResearchOutput(BaseModel):
    topics: List[Topic] = Field(description="List of researched topics")

class RankedTopic(BaseModel):
    rank: int = Field(description="The rank of the topic (1 is best)")
    title: str = Field(description="The title of the topic")
    score: float = Field(description="The score out of 10")
    reasoning: str = Field(description="Reasoning for this score based on trend momentum, executive relevance, engagement potential, longevity, and originality")

class RankingOutput(BaseModel):
    ranked_topics: List[RankedTopic] = Field(description="The top 3 ranked topics")

class PostDraft(BaseModel):
    topic: str = Field(description="The selected topic")
    post: str = Field(description="The full LinkedIn post text")
    hashtags: List[str] = Field(description="5-10 relevant hashtags")

class ReviewFeedback(BaseModel):
    approved: bool = Field(description="Whether the post is approved")
    overall_score: float = Field(description="Score out of 10")
    strengths: List[str] = Field(description="Strengths of the post")
    issues: List[str] = Field(description="Issues or areas for improvement")
    rewrite_instructions: List[str] = Field(description="Specific instructions for the writer agent to fix the post if rejected")
