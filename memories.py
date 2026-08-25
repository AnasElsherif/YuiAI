from pathlib import Path
import json
from datetime import date

folder = Path("memories")
chats_folder = folder / "chats"


def list_memories():
    memory_files = []
    for file in folder.iterdir():
        if file.is_file():
            memory_files.append(str(file))
    for file in chats_folder.iterdir():
        if file.is_file():
            memory_files.append(str(file))
    return memory_files


def load_memory(path_name):
    path = Path(path_name)
    if path.is_file():
        if path.suffix == ".json":
            data = json.dumps(
            json.loads(path.read_text()),
            indent=2
            )
            return data
        elif path.suffix == ".txt":
            return path.read_text()
        else:
            return "umm so how did u get a valid path that isnt the right suffex, so umm this is an error"
    else:
        return "not a valid path"

def load_today_chat():
    today = date.today().strftime("%d_%m_%Y")
    chat_file = chats_folder / f"{today}.json"
    if not chat_file.exists():
        return []
    return json.loads(chat_file.read_text())

def save_chat(history):
    chats_folder.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%d_%m_%Y")
    save_file = chats_folder / f"{today}.json"
    clean_history = []
    for message in history:
        if isinstance(message, dict):
            clean_history.append(message)
    save_file.write_text(
        json.dumps(clean_history, indent=2)
    )
    print(f"Saved chat to {save_file}")