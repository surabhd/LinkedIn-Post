from langchain_core.prompts import ChatPromptTemplate
from linkedin_generator.config import get_llm
from linkedin_generator.models import PostDraft
from linkedin_generator.prompts import WRITER_AGENT_PROMPT
from linkedin_generator.humanizer import humanize


def run_writer(topic_title: str, topic_summary: str, feedback: str = None) -> PostDraft:
    llm, provider_name, model_name = get_llm()

    prompt_messages = [
        ("system", WRITER_AGENT_PROMPT),
    ]

    user_prompt = (
        f"Topic Title: {topic_title}\n"
        f"Topic Summary: {topic_summary}\n\n"
        "Please draft a LinkedIn post following the persona and guidelines. "
        "Remember: no buzzwords, no hollow openers, no fake statistics. "
        "Write like a real executive speaking plainly and directly."
    )

    if feedback:
        user_prompt += (
            f"\n\nPREVIOUS REVIEWER FEEDBACK — address every point:\n{feedback}\n"
            "Also re-check: remove all banned buzzwords, hollow openers, and fabricated numbers."
        )

    prompt_messages.append(("user", user_prompt))
    prompt = ChatPromptTemplate.from_messages(prompt_messages)

    # ── Build chain using FallbackStructuredOutput ────────────────────────────
    # prompt | fallback_structured triggers FallbackStructuredOutput.__ror__
    # returning a new FallbackStructuredOutput with the prompt stored inside.
    fallback_structured = llm.with_structured_output(PostDraft)
    chain = prompt | fallback_structured

    draft: PostDraft = chain.invoke({})

    # ── Read which provider actually succeeded ────────────────────────────────
    actual_provider = provider_name
    actual_model = model_name
    if hasattr(chain, "succeeded_provider") and chain.succeeded_provider:
        actual_provider = chain.succeeded_provider
        actual_model = chain.succeeded_model or model_name

    # ── Run humanizer post-processor ──────────────────────────────────────────
    cleaned_post = humanize(draft.post)
    cleaned_hashtags = list(dict.fromkeys(draft.hashtags))  # deduplicate

    return PostDraft(
        topic=draft.topic,
        post=cleaned_post,
        hashtags=cleaned_hashtags,
        provider=actual_provider,
        model_name=actual_model,
    )
