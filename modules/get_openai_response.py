import openai
import os
import base64
import io
import requests
import numpy as np
from dotenv import load_dotenv
from datetime import date
from PIL import Image
from pathlib import Path
from .get_document_data import load_document_into_memory

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

openai.api_key = key

def chat_response(message, history, model, system):
    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content != None:
                partial_message = partial_message + str(chunk.choices[0].delta.content)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")

def chat_document_response(message, history, document, model, system):
    document_data = load_document_into_memory(document)

    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}, Document Data: {document_data}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content != None:
                partial_message = partial_message + str(chunk.choices[0].delta.content)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")



def dalle_response(message, size, quality, style):
    try:
        response = openai.images.generate(
            model = "dall-e-3",
            prompt = message,
            size = size,
            quality = quality,
            style = style, # natural
            n = 1,
            response_format = "b64_json" # b64_json url
        )

        image_data = response.data[0].b64_json
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)

        revised_prompt = response.data[0].revised_prompt

        return(revised_prompt, img_array)
    
    except openai.BadRequestError as e:
        return(f"ERROR: {e}")

def tts_response(message, voice, model):
    speech_file_path = Path(__file__).parent / "speech.mp3"

    try:
        response = openai.audio.speech.create(
            model = model,
            voice = voice,
            input = message
        )

        response.stream_to_file(speech_file_path)

        return(speech_file_path)
    
    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")
    except openai.APIConnectionError as e:
        #Handle connection error here
        return(f"Failed to connect to OpenAI API: {e}")
    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        return(f"OpenAI API request exceeded rate limit: {e}")

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str      

def vision_response(message, history, image=None):
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    if image:
        base64_image = encode_image_to_base64(image)
        # include the image in the messages
        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
        history_response.append(image_message)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": history_response,
            "max_tokens": 1000
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = response.json()["choices"][0]["message"]["content"]

            return(result)
        
        except:
            return(f"ERROR: {response}")

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer
