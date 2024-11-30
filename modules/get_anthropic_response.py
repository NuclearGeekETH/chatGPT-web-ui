import os
import anthropic
import base64
import io
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
            max_tokens=4096,
            system=system,
            messages=history_response,
            model=model,
        ) as stream:
            for text in stream.text_stream:
                partial_message = partial_message + str(text)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str   

def claude_vision_response(message, history, image=None):
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    if image:
        base64_image = encode_image_to_base64(image)    
        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image,
                    }
                }
            ]
        }
        history_response.append(image_message)

        try:
            message =  client.messages.create(
                max_tokens=4096,
                system="You are Claude 3.0 trained by Anthropic. Your goal is to help the user with image analysis.",
                messages=history_response,
                model="claude-3-opus-20240229",
            )

            return message.content[0].text

        except Exception as e:
            #Handle API error here, e.g. retry or log
            return(f"Error: {e}")

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer
