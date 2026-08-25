import os
import random
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_groq import ChatGroq

load_dotenv()

# Set up logging for provider selection
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_llm():
    """
    Returns a configured LangChain Chat Model instance randomly selected 
    from available LLM providers.
    """
    providers = []

    # 1. Groq
    if os.getenv("GROQ_API_KEY"):
        providers.append({
            "name": "Groq",
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
            "init_func": lambda: ChatCohere(
                cohere_api_key=os.getenv("COHERE_API_KEY"),
                model=os.getenv("COHERE_MODEL", "command-r-plus"),
                temperature=0.7,
            )
        })

    # 3. LLM7
    if os.getenv("LLM7_API_KEY"):
        providers.append({
            "name": "LLM7",
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("LLM7_API_KEY"),
                base_url=os.getenv("LLM7_BASE_URL", "https://api.llm7.io/v1"),
                model=os.getenv("LLM7_MODEL", "llama-3-8b"),
                temperature=0.7,
            )
        })

    # 4. Nvidia Build
    if os.getenv("NVIDIA_API_KEY"):
        providers.append({
            "name": "Nvidia",
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("NVIDIA_API_KEY"),
                base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                model=os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
                temperature=0.7,
                model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": True}}}
            )
        })

    # 5. OVH Kepler (Qwen Guard Gen 8B)
    ovh_url = os.getenv("OVH_KEPLER_URL", "https://qwen-guard-gen-8b.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1")
    ovh_key = os.getenv("OVH_API_KEY")
    if os.getenv("USE_OVH_KEPLER", "false").lower() == "true" and ovh_key:
        providers.append({
            "name": "OVH Kepler",
            "init_func": lambda: ChatOpenAI(
                api_key=ovh_key,
                base_url=ovh_url,
                model="qwen-guard-gen-8b", 
                temperature=0.7,
            )
        })
        
    # 6. Local LM Studio Fallback (Default if nothing else is configured)
    if os.getenv("USE_LOCAL_LM_STUDIO", "false").lower() == "true" or not providers:
        providers.append({
            "name": "Local LM Studio",
            "init_func": lambda: ChatOpenAI(
                api_key=os.getenv("API_KEY", "lm-studio"),
                base_url=os.getenv("BASE_URL", "http://localhost:1234/v1"),
                model=os.getenv("MODEL_NAME", "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"),
                temperature=0.7,
            )
        })

    # Randomly select a provider
    selected = random.choice(providers)
    
    # Initialize the LLM
    llm_instance = selected["init_func"]()
    
    # Extract model name safely
    model_name = "Unknown"
    if hasattr(llm_instance, "model_name"):
        model_name = llm_instance.model_name
    elif hasattr(llm_instance, "model"):
        model_name = llm_instance.model
        
    logger.info(f"Randomly selected LLM Provider: {selected['name']} ({model_name})")
    
    return llm_instance, selected["name"], model_name
