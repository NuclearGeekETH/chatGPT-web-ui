import ollama
import base64
import io
import json
import numpy as np

def ollama_chat_response(message, history, model):
    try:
        ollama.chat(model)
    except ollama.ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            print(f"Pulling model {model}" )
            yield f"Downloading model {model}" 
            ollama.pull(model)

    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        stream = ollama.chat(
            model=model,
            messages=history_response,
            stream=True,
        )

        partial_message = ""
        for chunk in stream:
            if chunk:
                partial_message = f"{partial_message}{str(chunk['message']['content'])}" 
                yield partial_message

    except Exception as e:
        return f"Error: {e}"
    
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str      

def process_image(image, max_len=1344, min_len=672):
    if max(image.size) > max_len:
        max_hw, min_hw = max(image.size), min(image.size)
        aspect_ratio = max_hw / min_hw
        shortest_edge = int(min(max_len / aspect_ratio, min_len, min_hw))
        longest_edge = int(shortest_edge * aspect_ratio)
        W, H = image.size
        if H > W:
            H, W = longest_edge, shortest_edge
        else:
            H, W = shortest_edge, longest_edge
        image = image.resize((W, H))

        return image

def ollama_vision_response(message, history, model, image=None):
    try:
        ollama.chat(model)
    except ollama.ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            print(f"Pulling model {model}" )
            yield f"Downloading model {model}" 
            ollama.pull(model)
    
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})


    if image:
        try:
            # partial_message = ""
            with open(image, 'rb') as img_file:
                img_content = img_file.read()

            # # Use the local image content instead of downloading it
            # for response in ollama.generate('llava', 'explain this image:', images=[img_content], stream=True):
            #     partial_message = f"{partial_message}{str(response['response'])}" 
            #     yield partial_message
            stream = ollama.generate(
                model,
                message,
                images=[img_content],
                stream=True,
            )

            partial_message = ""
            for chunk in stream:
                if chunk:
                    partial_message = f"{partial_message}{str(chunk['response'])}" 
                    yield partial_message

            # partial_message = ""
            # for response in ollama.generate(model, message, images=[image], stream=True):
            #     partial_message = f"{partial_message}{str(response['response'], end='', flush=True)}" 
            #     yield partial_message

        except Exception as e:
            return f"Error: {e}"

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer
