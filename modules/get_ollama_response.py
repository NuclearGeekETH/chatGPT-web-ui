import ollama
import base64
import io


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
        base64_image = encode_image_to_base64(image)
        # include the image in the messages
        try:
            stream = ollama.generate(
                model=model,
                messages=history_response,
                images=[base64_image],
                stream=True,
            )

            partial_message = ""
            for chunk in stream:
                if chunk:
                    partial_message = f"{partial_message}{str(chunk['message']['content'])}" 
                    yield partial_message

        except Exception as e:
            return f"Error: {e}"

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer
