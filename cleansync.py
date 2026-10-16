import os
from pathlib import Path
from watchfiles import watch, Change
from dotenv import load_dotenv

# Import our custom tools and skills
import tools
import skills

load_dotenv()

TARGET_FOLDER_NAME = os.getenv("SCAN_TARGET_DIR", "Downloads")
TARGET_DIR = Path.home() / TARGET_FOLDER_NAME

print(f"[*] CleanSync.ai running with modular tools.py & skills.py!")
print(f"[*] Watching live folder: {TARGET_DIR}\n")

def process_file(file_path: Path):
    if not file_path.is_file() or file_path.suffix in ['.crdownload', '.tmp', '.part']:
        return

    print(f"\n[+] Intercepted: {file_path.name}")
    
    # 1. Action using tool: Move to staging buffer
    try:
        buffered_file = tools.move_to_buffer(file_path)
    except Exception:
        return

    # 2. Action using tool: Read file content
    content = tools.read_file_preview(buffered_file)

    # 3. Decision using skill: Audit with local AI
    print("[*] Running local AI inspection...")
    verdict, explanation = skills.audit_file_skill(buffered_file.name, content)

    # 4. Actions using tools based on skill verdict
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
    try:
        for changes in watch(TARGET_DIR):
            for change_type, path_str in changes:
                if change_type == Change.added:
                    process_file(Path(path_str))
    except KeyboardInterrupt:
        print("\n[!] Shutting down CleanSync.ai.")