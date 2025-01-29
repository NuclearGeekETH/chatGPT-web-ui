import ollama
from ollama import chat
import base64
import io
from .get_document_data import load_document_into_memory, get_website_data

def ollama_chat_response(message, history, model, system):
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
    # history_response.append({"role": "system", "content": system})

    try:
        stream = chat(
            model=model,
            messages=history_response,
            stream=True,
        )

        partial_message = ""
        for chunk in stream:
            # print(chunk)
            if chunk:
                print(chunk['message']['content'], end='', flush=True)
                # Remove <think> and </think> tags
                cleaned_content = str(chunk['message']['content']).replace("<think>", "**THINKING**\n").replace("</think>", "\n**DONE THINKING**\n___")

                # Append to partial_message
                partial_message = f"{partial_message}{cleaned_content}"
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
            with open(image, 'rb') as img_file:
                img_content = img_file.read()

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

        except Exception as e:
            return f"Error: {e}"

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer

def get_ollama_model_list():
    try:
        ollama_model_list = ollama.list()
        model_list = []
        for x in ollama_model_list['models']:
            model_list.append(x['name'])
        return model_list
    except:
        return f"Error returning Ollama Models"

ollama_model_list = get_ollama_model_list()

def delete_ollama_model(model):
    try:
        ollama.delete(model)
        return f"{model} deleted"
    except Exception as e:
        return f"Error: {e}"
    
def ollama_document_response(message, history, model, document=None, link=None):

    history_response = []

    if link:
        website_data = get_website_data(link)
        history_response.append({"role": "user", "content": f"The website data is: {website_data}"})
    if document:
        document_data = load_document_into_memory(document)
        history_response.append({"role": "user", "content": f"The website data is: {document_data}"})

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
        #Handle API error here, e.g. retry or log
        return(f"Error: {e}")
