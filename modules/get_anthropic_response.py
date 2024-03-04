import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=key)

def claude_chat_response(message, history, model, system):
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        partial_message = ""
        with client.messages.stream(
            max_tokens=1024,
            system=system,
            messages=history_response,
            model="claude-3-opus-20240229",
        ) as stream:
            for text in stream.text_stream:
                partial_message = partial_message + str(text)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")
