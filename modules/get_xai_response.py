import os

from dotenv import load_dotenv
from datetime import date

from openai import OpenAI

load_dotenv()

key = os.getenv("XAI_API_KEY")

client = OpenAI(
  api_key=key,
  base_url="https://api.x.ai/v1",
)

def xai_chat_response(message, history, model, system):
    print(history)

    def build_history_response(history, include_system=False):
        history_response = []
        if include_system:
            history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}"})
        for human, assistant in history:
            history_response.append({"role": "user", "content": human})
            history_response.append({"role": "assistant", "content": assistant})
        history_response.append({"role": "user", "content": message})
        return history_response

    try:
        history_response = build_history_response(history, include_system=True)

        # Request completion with streaming enabled
        completion = client.chat.completions.create(
            model=model,
            messages=history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Ensure content is not None
                partial_message += chunk.choices[0].delta.content
                yield partial_message

    except Exception as e:
        # Handle API error: retry, log, or notify
        yield f"xAI API returned an API Error: {e}"

