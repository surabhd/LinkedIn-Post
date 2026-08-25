import os
import random
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_groq import ChatGroq

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _build_provider_list() -> list:
    """Build and return a shuffled list of all configured providers."""
    providers = []

    # 1. Groq
    if os.getenv("GROQ_API_KEY"):
        providers.append({
            "name": "Groq",
            "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            "init_func": lambda: ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=0.7,
            )
        })

    # 2. Cohere
    if os.getenv("COHERE_API_KEY"):
        providers.append({
            "name": "Cohere",
            "model": os.getenv("COHERE_MODEL", "command-r-plus-08-2024"),
            "init_func": lambda: ChatCohere(
                cohere_api_key=os.getenv("COHERE_API_KEY"),
                model=os.getenv("COHERE_MODEL", "command-r-plus-08-2024"),
                temperature=0.7,
            )
        })

    # 3. LLM7
    if os.getenv("LLM7_API_KEY"):
        providers.append({
            "name": "LLM7",
            "model": os.getenv("LLM7_MODEL", "default"),
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("LLM7_API_KEY"),
                base_url=os.getenv("LLM7_BASE_URL", "https://api.llm7.io/v1"),
                model=os.getenv("LLM7_MODEL", "default"),
                temperature=0.7,
            )
        })

    # 4. Nvidia Build
    if os.getenv("NVIDIA_API_KEY"):
        providers.append({
            "name": "Nvidia",
            "model": os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("NVIDIA_API_KEY"),
                base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                model=os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
                temperature=0.7,
                model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}}
            )
        })

    # 5. OVH Kepler
    ovh_url = os.getenv("OVH_KEPLER_URL", "https://qwen-guard-gen-8b.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1")
    ovh_key = os.getenv("OVH_API_KEY")
    if os.getenv("USE_OVH_KEPLER", "false").lower() == "true" and ovh_key:
        providers.append({
            "name": "OVH Kepler",
            "model": "qwen-guard-gen-8b",
            "init_func": lambda: ChatOpenAI(
                api_key=ovh_key,
                base_url=ovh_url,
                model="qwen-guard-gen-8b",
                temperature=0.7,
            )
        })

    # 6. Local LM Studio Fallback
    if os.getenv("USE_LOCAL_LM_STUDIO", "false").lower() == "true" or not providers:
        providers.append({
            "name": "Local LM Studio",
            "model": os.getenv("MODEL_NAME", "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"),
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("API_KEY", "lm-studio"),
                base_url=os.getenv("BASE_URL", "http://localhost:1234/v1"),
                model=os.getenv("MODEL_NAME", "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"),
                temperature=0.7,
            )
        })

    # Shuffle so starting provider is random each run
    random.shuffle(providers)
    return providers


class FallbackStructuredOutput:
    """
    A structured output wrapper that automatically falls back across
    providers if the current one raises an exception.
    Supports LangChain's `prompt | chain` pipe syntax.
    """

    def __init__(self, providers: list, schema, prompt=None):
        self._providers = providers
        self._schema = schema
        self._prompt = prompt
        self.succeeded_provider = None
        self.succeeded_model = None

    def __ror__(self, prompt):
        """Enable: prompt | FallbackStructuredOutput(...)"""
        return FallbackStructuredOutput(self._providers, self._schema, prompt)

    def invoke(self, inputs: dict):
        last_error = None
        for provider in self._providers:
            try:
                llm = provider["init_func"]()
                structured = llm.with_structured_output(self._schema)
                if self._prompt is not None:
                    result = (self._prompt | structured).invoke(inputs)
                else:
                    result = structured.invoke(inputs)
                # Record which provider won
                self.succeeded_provider = provider["name"]
                self.succeeded_model = provider["model"]
                logger.info(f"✅ Provider succeeded: {provider['name']} ({provider['model']})")
                return result
            except Exception as e:
                logger.warning(f"⚠️  Provider '{provider['name']}' failed: {e} — trying next...")
                last_error = e

        raise RuntimeError(
            f"All {len(self._providers)} providers failed. Last error: {last_error}"
        )


class FallbackLLM:
    """
    Drop-in replacement for a single LangChain Chat Model.
    Holds a shuffled provider pool and exposes with_structured_output()
    that retries across the full pool on failure.
    """

    def __init__(self, providers: list):
        self._providers = providers
        # Expose the first provider's name/model as the "intended" provider
        first = providers[0] if providers else {}
        self.provider_name = first.get("name", "Unknown")
        self.model_name = first.get("model", "Unknown")

    def with_structured_output(self, schema) -> FallbackStructuredOutput:
        return FallbackStructuredOutput(self._providers, schema)


def get_llm():
    """
    Returns a FallbackLLM that automatically tries all configured providers
    in random order until one succeeds.

    Returns: (FallbackLLM instance, first_provider_name, first_model_name)
    """
    providers = _build_provider_list()
    if not providers:
        raise RuntimeError("No LLM providers configured. Add at least one API key to your environment.")

    llm = FallbackLLM(providers)
    logger.info(f"Provider pool ({len(providers)} options): {[p['name'] for p in providers]}")
    logger.info(f"Starting with: {llm.provider_name}")

    return llm, llm.provider_name, llm.model_name
