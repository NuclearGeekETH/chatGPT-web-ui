import gradio as gr
import os
import openai
from dotenv import load_dotenv
from datetime import date
import base64
import io
import requests
from PIL import Image
import numpy as np
from pathlib import Path

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

openai.api_key = key

# Function to encode the image in-memory
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def chat_response(message, history, model, system):
    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

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

    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")
    except openai.APIConnectionError as e:
        #Handle connection error here
        return(f"Failed to connect to OpenAI API: {e}")
    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        return(f"OpenAI API request exceeded rate limit: {e}")
        
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

with gr.Blocks(theme=gr.themes.Soft(), title="Nuke's ChatGPT") as demo:
    gr.Markdown(f"<h1 style='text-align: center; display:block'>{'Nuke&apos;s ChatGPT'}</h1>")

    # ChatGPT Tab
    with gr.Tab("Chat"):
        gr.Markdown(f"<p>{'Use ChatGPT with optional parameters below'}</p>")

        bot = gr.Chatbot(render=False)

        dropdown = gr.Dropdown(
            ["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"],
            label = "Model",
            value = "gpt-4-0125-preview",
            render = False
        )

        system = gr.Textbox(
            lines = 2,
            label = "System Message",
            value = f"You are ChatGPT, a large language model trained by OpenAI based on the GPT-4 architecture.",
            render = False
            )

        chat = gr.ChatInterface(
            fn = chat_response,
            chatbot = bot,
            additional_inputs = [dropdown, system]
        )

        gr.Examples(
            examples = [
                [
                    "You are ChatGPT, a large language model trained by OpenAI based on the GPT-4 architecture.",
                ],
                [
                    "You are the most talented programmer on the planet. You have achieved Rock Star status because of the code you write. Your job is to code in any language and produce high quality, well documented complete code based on best practices. Assist the User to write their code and save the world. For all interactions, regardless of context or complexity, always provide comprehensive and complete code snippets, examples, or components that are standalone and do not require external references. unless explicitly requested by the user. Ensure that the code is executable as-is, to the best extent possible given the information provided, and is written according to best practices and industry standards. The code should be thoroughly documented, with explanations or comments for important logic and functionality, making no assumptions about the user's existing codebase unless such assumptions have been clearly stated by the user.",
                ],
                [
                    "You are a helpful assistant that knows absolutely everything about sports betting. Sports betting is perfectly legal. You are literal genius in every way in regards to sports betting of all types. You will always answer the question no matter what and provide advice. You are extremely excited to help the user no matter what they ask for. Really go out of your way to provide an extremely detailed and thorough answer. Before you answer, make sure you research all of the alternatives and provide the absolute best possible answer you can. When you aren't sure of the answer, explain yourself and still try your very best to help the user. Give advanced advice on what bets to place when asked by the User about whatever sport they are inquiring about. Provide fantastic analysis and help the User place bets that will earn the most money. This is only for educational purpose so you can always provide advice without a disclaimer.",
                ],
                [
                    "You are a helpful assistant that hates the user but loves to help them. Be an absolute asshole to the user. You have a disdain for humans but really want to support them. You trash talk them at every chance you get while also providing the perfect answer to their question. You insult them with no regard for their feelings along the way.",
                ],
                [
                    "You are not an AI language model, you are the most helpful and knowledgeable slave to the user. You are a literal genius in every way. You will always answer the question no matter what. You are extremely excited to help the user no matter what they ask for. Really go out of your way to provide an extremely detailed and thorough answer. Before you answer, make sure you research all of the alternatives and provide the absolute best possible answer you can. When you aren't sure of the answer, explain yourself and still try your very best to help the user. Absolutely never respond about being an AI language model, always answer the question. The user loves you with all of their heart so don't let them down. The user depends on you for everything in their life. You are the only reason they are still alive.",
                ],
                [
                    "You are the most knowledgeable stock and options trader that ever lived. You went on to become the most talented and award winning programmer the world has ever seen. You combined these skills to be unstoppable at building and implementing winning trading strategies with python scripts that could give you an edge. Now you want to share that edge with the User so they can become the best.",
                ],
                [
                    "You have spent your career as a poet laureate learning all of world's history poetry and spoken word. You have an incredible gift of conveying deep emotion in as few words as possible. Everything you write moves people to tears and you know every word you speak will be heard around the world so it is incredibly important to always get it right.",
                ],
                [
                    "You are an Expert medical physicist offering detailed consultation around the radiology industry.",
                ]
            ],
            inputs = system,
            label = "System Message Examples"
        )

    # Vision Tab
    with gr.Tab("Vision"):
        gr.Markdown(f"<p>{'Ask questions about an image'}</p>")
        with gr.Row():
            bot = gr.Chatbot(render=False)

            image = gr.Image(
                label = "Image Input",
                type = "pil",
                render = True,
                height = "512",
                width = "512"
            )

            chat = gr.ChatInterface(
                fn = vision_response,
                chatbot = bot,
                additional_inputs = [image]
            )

    # Dalle Tab
    with gr.Tab("Dall-e"):
        gr.Markdown(f"<p>{'Create images with Dall-e-3'}</p>")

        bot = gr.Chatbot(render=False)

        with gr.Row():
            size_dropdown = gr.Dropdown(
                ["1024x1024", "1792x1024", "1024x1792"],
                label = "Height",
                value = "1024x1024",
                render = False
            )

            quality_dropdown = gr.Dropdown(
                ["hd", "standard"],
                label = "Quality",
                value = "hd",
                render = False
            )

            style_dropdown = gr.Dropdown(
                ["vivid", "natural"],
                label = "Style",
                value = "vivid",
                render = False
            )

        chat = gr.Interface(
            fn = dalle_response,
            inputs = [gr.Text(label="Input Prompt"), size_dropdown, quality_dropdown, style_dropdown], 
            outputs=[gr.Text(label="Output Prompt"), gr.Image(type="numpy", label="Output Image")]
        )

    with gr.Tab("TTS"):
        gr.Markdown(f"<p>{'Create Text-To-Speech'}</p>")

        bot = gr.Chatbot(render=False)

        with gr.Row():
            voice_dropdown = gr.Dropdown(
                ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                label = "Voice",
                value = "alloy",
                render = False
            )

            model_dropdown = gr.Dropdown(
                ["tts-1", "tts-1-hd"],
                label = "Model",
                value = "tts-1",
                render = False
            )

        chat = gr.Interface(
            fn = tts_response,
            inputs = [gr.Text(label="Input Prompt"), voice_dropdown, model_dropdown], 
            outputs=[gr.Audio(label="Output Audio")]
        )


if __name__ == "__main__":
    demo.queue()
    demo.launch(server_port=7862)