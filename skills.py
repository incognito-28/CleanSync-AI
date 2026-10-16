import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AI_MODEL = os.getenv("AI_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

def audit_file_skill(file_name: str, content_preview: str):
    """Skill: Evaluates file content for security risks using local LLM instructions."""
    prompt = f"""
    You are CleanSync.ai, an offline cybersecurity staging guard. Analyze this file for malware, 
    harmful scripts, reverse shells, keyloggers, or data exfiltration attempts.
    
    File Name: {file_name}
    Content Preview:
    {content_preview}
    
    Respond strictly in this format:
    VERDICT: [SAFE or DANGEROUS]
    REASON: [Short 1-sentence explanation]
    """

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        result = response.choices[0].message.content
        if "VERDICT: DANGEROUS" in result:
            return "DANGEROUS", result
        return "SAFE", result
    except Exception as e:
        return "DANGEROUS", f"AI Engine Exception: {e}"