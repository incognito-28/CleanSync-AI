import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

USER_HOME = Path.home()
AIRLOCK_BASE = USER_HOME / "CleanSync_Airlock"
STAGING_DIR = AIRLOCK_BASE / "staging_buffer"
SECURE_DIR = USER_HOME / "Desktop" / "CleanSync_Secure"
QUARANTINE_DIR = AIRLOCK_BASE / "quarantine"

# Ensure required directories exist
for dir_path in [STAGING_DIR, SECURE_DIR, QUARANTINE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def read_file_preview(file_path: Path, max_chars=10000) -> str:
    """Tool: Reads raw text preview of a file for inspection."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    except Exception as e:
        return f"[Error reading file text: {e}]"

def move_to_buffer(source_path: Path) -> Path:
    """Tool: Moves an incoming download into the isolated staging buffer."""
    dest = STAGING_DIR / source_path.name
    shutil.move(str(source_path), str(dest))
    return dest

def move_to_secure(file_path: Path):
    """Tool: Transfers a verified safe file to secure storage."""
    dest = SECURE_DIR / file_path.name
    shutil.move(str(file_path), str(dest))
    return dest

def move_to_quarantine(file_path: Path):
    """Tool: Transfers a dangerous file to quarantine."""
    dest = QUARANTINE_DIR / file_path.name
    shutil.move(str(file_path), str(dest))
    return dest

def popup_user_alert(file_name: str, reasoning: str) -> bool:
    """Tool: Triggers an on-screen warning window asking user to Allow or Decline."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    msg = f"CleanSync.ai detected a potential threat in:\n\n📄 {file_name}\n\nAI Analysis:\n{reasoning}\n\nDo you want to ALLOW this file anyway?"
    response = messagebox.askyesno("⚠️ CleanSync.ai Security Alert", msg, icon='warning')
    root.destroy()
    return response