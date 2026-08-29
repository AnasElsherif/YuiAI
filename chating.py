from google import genai
import time
import subprocess
from datetime import datetime
import sounddevice as sd
from ddgs import DDGS
import requests
from google.genai import types
import os
from dotenv import load_dotenv
from pathlib import Path
import memories


# ============================================================
# SETUP
# ============================================================

load_dotenv()

system_file = Path("system.txt")
coreMemoryfile = Path("core_memory.txt")

system = system_file.read_text()
Core_memory = coreMemoryfile.read_text()


# ============================================================
# AUDIO INITIALIZATION
# ============================================================

AUDIO_DEVICE = 3
AUDIO_SAMPLE_RATE = 22050

audio_stream = sd.OutputStream(
    samplerate=AUDIO_SAMPLE_RATE,
    channels=1,
    device=AUDIO_DEVICE
)

audio_stream.start()


# ============================================================
# API SETUP
# ============================================================

UNREAL_API_KEY = os.environ["UNREAL_SPEECH_API_KEY"]

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# ============================================================
# GEMINI SYSTEM PROMPT
# ============================================================

sys_prompt = f"""
{system}

{Core_memory}

MEMORY SYSTEM:

You have access to a persistent memory system.

You do NOT automatically remember every old conversation.

If you need information from the past, you can inspect the available
memories using the list_memories tool.

After seeing the list, you can choose a specific memory to load using
load_memory.

You should decide yourself when an old memory is relevant.

Do not load every memory just because it is available.

Do not claim to remember something if it is not present in your
current context or in a memory you have loaded.

CURRENT CONVERSATION:
The current conversation is already available to you.

LOADED MEMORY RULE:

When you load a memory, it becomes background context only.
It does NOT become the current conversation.

Never continue, roleplay, or answer anything from inside a loaded memory.
After reading it, return to the current conversation and respond only
to the users' current message.

CORE MEMORY:

You can save important information to core_memory.txt using
the save_core_memory tool.

Use it when:
- the user explicitly asks you to remember something.
- You learn a stable preference or fact that will help
  future conversations. This includes things like the user's
  name, age, interests, preferences, or habits.
- An important long-term project, goal, or decision is established.

Do NOT save:
- Normal conversation
- Temporary information
- Every message
- Things you are merely guessing
- Sensitive information unless explicitly requested

Keep memories concise.

OTHER TOOLS:

WEB SEARCH:
Use search_web when the user asks about current events, facts you are
unsure about, or anything that benefits from an up-to-date answer.
Do not announce that you are searching. Just do it and respond naturally.

DATE AND TIME:
Use get_datetime when the user asks about the current time or date,
or when knowing the date is relevant to your response.

SCREENSHOT:
Use take_screenshot only when the user asks you to look at their screen,
or when it is clearly necessary to answer their question.

FILE BROWSER:
Use list_files when the user asks about files in a folder, or when
you need to inspect the filesystem to answer a question.
Always use the exact path provided by the user.
"""


messages = [
    {
        "role": "user",
        "parts": [{"text": sys_prompt}]
    }
]

messages.extend(
    memories.load_today_chat()
)


# ============================================================
# TOOLS
# ============================================================

search_web_tool = types.FunctionDeclaration(
    name="search_web",
    description="""
Search the web using DuckDuckGo.

Use this when the user asks about current information,
recent events, websites, facts you are unsure about, or
anything that requires an internet search.
""",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "query": types.Schema(
                type="STRING",
                description="The web search query."
            )
        },
        required=["query"]
    )
)

save_core_memory_tool = types.FunctionDeclaration(
    name="save_core_memory",
    description="""
Save an important piece of information to core_memory.txt.

Use this when something from the current conversation is important
enough to remember long-term.

Only save information that is genuinely useful for future conversations.
Do not save temporary details, random conversation, or sensitive information.

The memory should be written as a concise statement.
""",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "memory": types.Schema(
                type="STRING",
                description="The concise piece of information that should be remembered."
            )
        },
        required=["memory"]
    )
)

list_memories_tool = types.FunctionDeclaration(
    name="list_memories",
    description="""
List all memories currently available to Yui.

Use this when you think you need information from an older
conversation or memory but do not know which memory file contains it.

The result only gives you the available memory filenames.
It does NOT load their contents.
"""
)


list_files_tool = types.FunctionDeclaration(
    name="list_files",
    description="""
Lists all files in a folder Yui chooses by providing the exact path.
""",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "name": types.Schema(
                type="STRING",
                description="The exact path of the folder to list the files in."
            )
        },
        required=["name"]
    )
)


take_screenshot_tool = types.FunctionDeclaration(
    name="take_screenshot",
    description="Take a screenshot of the users' current screen."
)


load_memory_tool = types.FunctionDeclaration(
    name="load_memory",
    description="""
Load one specific memory file for context.

IMPORTANT:
The loaded file is ARCHIVED MEMORY, NOT the current conversation.

After loading a memory:

- Use it only to understand relevant past information.
- NEVER continue the conversation found inside the memory.
- NEVER respond to the last message in the memory.
- NEVER pretend the events in the memory are happening now.
- NEVER copy or continue dialogue from the memory.
- Return to the CURRENT conversation and respond to the user's CURRENT message.
- Treat everything in the memory as historical context.

You must provide the exact memory filename returned by list_memories().
Do not load memories unnecessarily.
""",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "name": types.Schema(
                type="STRING",
                description="The exact memory filename to load."
            )
        },
        required=["name"]
    )
)
get_datetime_tool = types.FunctionDeclaration(
    name="get_datetime",
    description="Get the user's current local date and time."
)

# ============================================================
# FILE TOOL
# ============================================================


def search_web(query):

    print("used tool: search_web:", query)

    results = DDGS().text(
        query,
        max_results=5
    )

    return {
        "results": [
            {
                "title": r["title"],
                "url": r["href"],
                "snippet": r["body"]
            }
            for r in results
        ]
    }

def save_core_memory(memory):
    with open("core_memory.txt", "a", encoding="utf-8") as f:
        f.write("\n" + memory.strip() + "\n")

    return {
        "status": "saved",
        "memory": memory
    }

def list_files(path_str):

    files = []

    folder = Path(path_str)

    if not folder.is_dir():
        return {
            "error": "not a valid path"
        }

    for file in folder.iterdir():

        if file.is_file() or file.is_dir():
            files.append(str(file))

    return files

def get_datetime():
    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "timezone": "Asia/Kuwait"
    }

# ============================================================
# TOOL HANDLER
# ============================================================

def do_tool_pls(tool_name, tool_arg):

    if tool_name == "list_memories":

        print("used tool: list_memories")

        return {
            "memories": memories.list_memories()
        }


    if tool_name == "load_memory":

        print(
            "used tool: load_memory on path: "
            + tool_arg["name"]
        )

        return {
            "memory content":
            memories.load_memory(
                tool_arg["name"]
            )
        }


    if tool_name == "list_files":

        print(
            "used tool: list_files on path: "
            + tool_arg["name"]
        )

        return {
            "files in path":
            list_files(tool_arg["name"])
        }


    if tool_name == "take_screenshot":

        print("took screenshot")

        subprocess.run(
            ["grim", "/tmp/screen.png"],
            check=True
        )

        return Path(
            "/tmp/screen.png"
        ).read_bytes()

    if tool_name == "save_core_memory":
        print("used tool: save_core_memory")
        return save_core_memory(tool_arg["memory"])
    if tool_name == "search_web":
        return search_web(
            tool_arg["query"]
        )
    if tool_name == "get_datetime":
        print("used tool: get_datetime")
        return get_datetime()
# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(text):

    print("Generating speech...")

    response = requests.post(
        "https://api.v8.unrealspeech.com/stream",

        headers={
            "Authorization": f"Bearer {UNREAL_API_KEY}",
        },

        json={
            "Text": text,
            "VoiceId": "af_bella",
            "Bitrate": "192k",
            "Speed": 0,
            "Pitch": 1.1,
            "Codec": "libmp3lame",
        },

        stream=True,
    )


    if response.status_code != 200:

        print("TTS error:")
        print(response.status_code)
        print(response.text)

        return


    print("Playing...")


    mpv = subprocess.Popen(
        [
            "mpv",
            "--no-video",
            "--really-quiet",
            "--cache=yes",
            "--demuxer-readahead-secs=0",
            "--",
            "fd://0",
        ],

        stdin=subprocess.PIPE,
    )


    try:

        for chunk in response.iter_content(
            chunk_size=4096
        ):

            if chunk:

                mpv.stdin.write(chunk)
                mpv.stdin.flush()


    finally:

        mpv.stdin.close()
        mpv.wait()


    print("Finished.")


# ============================================================
# GEMINI TOOLS
# ============================================================

tools = types.Tool(
    function_declarations=[
        load_memory_tool,
        list_memories_tool,
        list_files_tool,
        take_screenshot_tool,
        save_core_memory_tool,
        search_web_tool,
        get_datetime_tool,
    ]
)


# ============================================================
# MAIN CHAT LOOP
# ============================================================

while True:

    msg = input("\033[91m"+"user: "+"\033[0m")


    if msg.lower() == "exit":

        memories.save_chat(
            messages[1:]
        )

        break


    messages.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": msg
                }
            ]
        }
    )



    while True:

        try:

            response = client.models.generate_content(

                model="gemini-3.1-flash-lite",

                contents=messages,

                config=types.GenerateContentConfig(
                    tools=[tools]
                )
            )


        except Exception as e:

            print(
                f"Gemini error, retrying in 5s... ({e})"
            )

            time.sleep(5)

            continue


        if not response.function_calls:
            break


        messages.append(
            response.candidates[0].content
        )


        for func in response.function_calls:

            tool_result = do_tool_pls(
                func.name,
                func.args
            )


            # =================================================
            # SCREENSHOT TOOL
            # =================================================

            if func.name == "take_screenshot":

                messages.append(
                    types.Content(
                        role="tool",

                        parts=[
                            types.Part.from_function_response(
                                name=func.name,
                                response={}
                            )
                        ]
                    )
                )


                messages.append(
                    types.Content(
                        role="user",

                        parts=[
                            types.Part.from_bytes(
                                data=tool_result,
                                mime_type="image/png"
                            )
                        ]
                    )
                )


            # =================================================
            # NORMAL TOOLS
            # =================================================

            else:

                messages.append(
                    types.Content(
                        role="tool",

                        parts=[
                            types.Part.from_function_response(
                                name=func.name,
                                response=tool_result
                            )
                        ]
                    )
                )


    # ========================================================
    # RESPONSE
    # ========================================================

    if response.text is not None:

        messages.append(
            {
                "role": "model",

                "parts": [
                    {
                        "text": response.text
                    }
                ]
            }
        )


        print(
            "\033[96m"+"yui: " +"\033[0m"+ response.text
        )


        speak(
            response.text
        )