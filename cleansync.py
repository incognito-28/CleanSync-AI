import os
from pathlib import Path
from openai import OpenAI
from watchfiles import watch, Change
from dotenv import load_dotenv
import tools

load_dotenv()

AI_MODEL = os.getenv("AI_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
TARGET_FOLDER_NAME = os.getenv("SCAN_TARGET_DIR", "Downloads")
TARGET_DIR = Path.home() / TARGET_FOLDER_NAME

# Initialize local Ollama client
client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

def load_skill_instructions():
    """Reads instructions dynamically from Skill.md"""
    skill_path = Path("Skill.md")
    if skill_path.exists():
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are CleanSync.ai. Analyze this file for malware and security risks."

def audit_file_with_skill(file_name: str, content_preview: str):
    """Audits file content via local LLM using guidelines loaded from Skill.md."""
    skill_instructions = load_skill_instructions()
    
    prompt = f"""
    {skill_instructions}
    
    File Name: {file_name}
    Content Preview:
    {content_preview}
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

def process_file(file_path: Path):
    if not file_path.is_file() or file_path.suffix in ['.crdownload', '.tmp', '.part']:
        return

    print(f"\n[+] Intercepted download: {file_path.name}")
    
    try:
        buffered_file = tools.move_to_buffer(file_path)
    except Exception:
        return

    content = tools.read_file_preview(buffered_file)

    print("[*] Running local AI inspection using Skill.md instructions...")
    verdict, explanation = audit_file_with_skill(buffered_file.name, content)

    if verdict == "SAFE":
        dest = tools.move_to_secure(buffered_file)
        print(f"[✔] SAFE: Moved to secure storage -> {dest}")
    else:
        print(f"[❌] THREAT DETECTED!")
        allow = tools.popup_user_alert(buffered_file.name, explanation)
        if allow:
            dest = tools.move_to_secure(buffered_file)
            print(f"[!] User forced ALLOW -> {dest}")
        else:
            dest = tools.move_to_quarantine(buffered_file)
            print(f"[✔] DECLINED -> Quarantined at {dest}")

if __name__ == "__main__":
    print(f"[*] CleanSync.ai active with modular files and Skill.md!")
    print(f"[*] Monitoring live folder: {TARGET_DIR}\n")
    try:
        for changes in watch(TARGET_DIR):
            for change_type, path_str in changes:
                if change_type == Change.added:
                    process_file(Path(path_str))
    except KeyboardInterrupt:
        print("\n[!] Shutting down CleanSync.ai.")