import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

def google_chat_response(message, history):
    model = genai.GenerativeModel('gemini-pro')

    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "parts": [human]})
        history_response.append({"role": "model", "parts": [assistant]})

    history_response.append({"role": "user", "parts": [message]})
   
    try:
        response = model.generate_content(
            history_response,
            stream=True
            )

        partial_message = ""
        for chunk in response:
            partial_message = partial_message + str(chunk.text)
            if partial_message:
                yield partial_message

    except Exception as e:
        return f'{type(e).__name__}: {e}'

def google_vision_response(message, history, image=None):
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "parts": human})
        history_response.append({"role": "model", "parts": assistant})

    history_response.append({"role": "user", "parts": message})

    if image:
        try:
            model = genai.GenerativeModel('gemini-pro-vision')
            # response = model.generate_content(image)
            response = model.generate_content([message, image])
            response.resolve()
            return response.text
        except Exception as e:
            return f'{type(e).__name__}: {e}'

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer

