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
3. Copy `.env.example` to `.env` and fill in API keys for the providers you want to use. The app will randomly select a configured provider.

## Cloud Deployment (Streamlit Community Cloud)

To host this application on the cloud for free:
1. Push this repository to a **private** GitHub repository.
2. Do **not** commit your `.env` file to version control.
3. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud) with your GitHub account.
4. Click **New app** and select your repository, branch, and `app.py` as the main file.
5. **Secure Keys**: Before clicking Deploy, click on **Advanced settings** (or the **Secrets** section later) and paste your environment variables in TOML format:
   ```toml
   GROQ_API_KEY = "your-key"
   NVIDIA_API_KEY = "your-key"
   LLM7_API_KEY = "your-key"
   # ... add others as needed
   ```
6. Click Deploy!

## Execution

### Command Line Interface
Run the system in the terminal:
```bash
python main.py
```

### Web User Interface
Run the Streamlit web app:
```bash
streamlit run app.py
```
This will open a local web page in your browser where you can generate posts interactively.
