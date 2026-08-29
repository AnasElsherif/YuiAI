# YuiAI

YuiAI is a personal AI assistant project by AnasElsherif. It combines Google's Gemini API with Unreal Speech to create a conversational AI with persistent memory, customizable personality, tool calling, and voice output.

The project is designed to be simple and easy to modify, allowing users to customize Yui's personality, memories, tools, and behavior.

Currently tested on Linux with Python 3.14.

## Features

- LLM-based conversation using Google Gemini
- Persistent conversation history
- Long-term memory system
- Customizable personality and behavior
- Core memory that Yui can update herself
- Function calling for tools
- Web search
- File system access through tools
- Screenshot capture
- Text-to-speech using Unreal Speech
- Configurable system prompt
- Open source and fully customizable

## Requirements

- Python 3.14
- Google Gemini API key
- Unreal Speech API key
- ffmpeg
- mpv
- grim (for screenshots)

## Setup

### 1. Clone the repository

    git clone git@github.com:AnasElsherif/YuiAI.git
    cd YuiAI

### 2. Create a virtual environment

    python -m venv .venv
    source .venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure API keys

Copy the example environment file:

    cp .env.example .env

Open .env and add your own API keys:

    GEMINI_API_KEY=your_gemini_api_key
    UNREAL_SPEECH_API_KEY=your_unreal_speech_api_key

Do not commit your .env file or share your API keys.

## Configuration

### system.txt

Contains Yui's main system prompt.

This controls things such as her communication style, behavior, rules, and how she should interact with the memory system.

### core_memory.txt

Contains Yui's long-term core memory.

This is intended for information that Yui considers important enough to remember across conversations, such as the user's name, preferences, ongoing projects, or other stable facts.

Yui can also update this file herself using the save_core_memory tool.

### memories/

Contains archived conversations.

Conversation history is stored separately from Yui's core memory so that old conversations can be loaded when relevant.

## Usage

Activate the virtual environment:

    source .venv/bin/activate

Then start Yui:

    python chating.py

The basic conversation flow is:

1. You send Yui a message.
2. Gemini processes the conversation.
3. Yui can use available tools when necessary.
4. Gemini generates a response.
5. Unreal Speech generates Yui's voice.
6. The generated audio is played locally.

Type:

    exit

to close Yui and save the current conversation.

## Memory System

Yui has two different types of memory.

### Conversation Memory

Conversations are automatically saved and can be loaded later when Yui needs information from a previous conversation.

Yui decides when an archived conversation is relevant instead of loading every conversation automatically.

### Core Memory

Core memory is intended for information that should remain important across conversations.

This includes things like the user's name, age, preferences, ongoing projects, or any fact worth remembering long-term.

Core memory is stored in:

    core_memory.txt

## Tools

Yui currently has access to several tools:

- list_memories — Lists available archived conversations.
- load_memory — Loads a specific archived conversation.
- save_core_memory — Saves an important fact to core memory.
- search_web — Searches the web using DuckDuckGo.
- get_datetime — Gets the current local date and time.
- list_files — Lists files in a specified directory.
- take_screenshot — Takes a screenshot of the current screen.

More tools can be added as the project develops.

## API Usage

YuiAI currently uses external APIs for its AI and voice generation.

### Google Gemini

Gemini is used for:

- Conversation
- Reasoning
- Tool calling
- Processing screenshots

You need to provide your own Gemini API key.

### Unreal Speech

Unreal Speech is used for:

- Text-to-speech
- Generating Yui's voice

You need to provide your own Unreal Speech API key.

API keys are stored locally in .env and are not included in the repository.

## Future Improvements

The project is still under development. Planned improvements include:

- [ ] Speech-to-text
- [ ] Real-time voice conversations
- [ ] Improved vision capabilities
- [ ] More tools

## Credits

- Language model powered by Google Gemini
- Text-to-speech powered by Unreal Speech

## License

YuiAI is licensed under the MIT License.

See the LICENSE file for the full license.