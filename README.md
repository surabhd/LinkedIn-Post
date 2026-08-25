# Multi-Agent LinkedIn Content Generation System

This project is a LangGraph-based multi-agent system that automates the generation of executive-level LinkedIn posts. It runs locally using LM Studio (or any OpenAI-compatible API).

## Architecture

The system consists of 4 agents connected via LangGraph:
1. **Research Agent**: Gathers emerging business/tech topics.
2. **Ranking Agent**: Scores topics based on executive relevance and engagement potential, picking the top ones.
3. **Writer Agent**: Drafts the LinkedIn post from the perspective of a Principal Architect.
4. **Reviewer Agent**: Reviews the draft against strict business-value and readability criteria. Can trigger up to 3 rewrite loops.

## Requirements

- Python 3.11+
- LM Studio running locally with a supported model (e.g., Llama 3)
- Model must support JSON structure output/function calling if strict Pydantic parsing is enforced

## Setup

1. Clone or copy the files into a new directory.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust variables if needed:
   ```
   BASE_URL=http://localhost:1234/v1
   API_KEY=lm-studio
   MODEL_NAME=lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF
   ```
4. Start LM Studio server.

## Execution

Run the system:
```bash
python main.py
```

The system will print the progress of each agent and output the final approved LinkedIn post.
