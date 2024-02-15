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
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from modules.get_journals import get_soup_from_internet
from modules.get_journals import get_books
import google.generativeai as genai

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
subscription_key = os.getenv('BING_SEARCH_V7_SUBSCRIPTION_KEY')
search_endpoint =  "https://api.bing.microsoft.com/v7.0/search"
news_endpoint =  "https://api.bing.microsoft.com/v7.0/news/search"
GOOGLE_API_KEY= os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)
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

def google_chat_response(message, history, model, system):
    model = genai.GenerativeModel('gemini-pro')

    history_response = []

    # history_response.append({"role": "model", "parts": [f"{system} Current Date: {date.today()}"]})

    for human, assistant in history:
        history_response.append({"role": "user", "parts": [human]})
        history_response.append({"role": "model", "parts": [assistant]})

    history_response.append({"role": "user", "parts": [message]})

    # print(history_response)

    try:
        response = model.generate_content(
            history_response,
            stream=True
            )

        # print(response)
        # print(response.text)

        partial_message = ""
        for chunk in response:
            print(chunk.text)
            partial_message = partial_message + str(chunk.text)
            if partial_message:
                yield partial_message

    # try:
    #     completion = openai.chat.completions.create(
    #         model = model,
    #         messages = history_response,
    #         stream=True
    #     )

    #     # Stream Response
    #     partial_message = ""
    #     for chunk in completion:
    #         if chunk.choices[0].delta.content != None:
    #             partial_message = partial_message + str(chunk.choices[0].delta.content)
    #             if partial_message:
    #                 yield partial_message
    except Exception as e:
        return f'{type(e).__name__}: {e}'
        
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

def bing_search(text, history):
    """
    Use Bing API to perform a web search and return the first 10 snippets.
    """
    # Query term(s) to search for. 
    # Construct a request
    params = {'q': text}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    # Call the API
    try:
        response = requests.get(search_endpoint, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response JSON
        search_results = response.json()

        # Check if there are webPages results available
        if 'webPages' in search_results and 'value' in search_results['webPages']:

            message_response = []

            for result in search_results['webPages']['value']:
                name = result["name"] 
                url = result["url"]
                snippet = result["snippet"]

                message = F"📖 {name}\n" \
                    F"🔗 {url}\n" \
                    F"📃 {snippet}\n\n"


                message_response.append(message)

            concatenated_message = ' '.join(message_response)

            return concatenated_message

        else:
            return "No web page results found."
    
    except Exception as ex:
        return F"Something went wrong: {ex}"

def bing_news(text, history):
    """
    Use Bing API to perform a news search and return the first snippet.
    """
    # Query term(s) to search for. 
    # Construct a request
    params = {'q': text}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    # Call the API
    try:
        response = requests.get(news_endpoint, headers=headers, params=params)
        response.raise_for_status()

        # Parse the response JSON
        search_results = response.json()

        # Check if there are webPages results available
        if 'value' in search_results:
            
            message_response = []

            for article in search_results["value"]:
                name = article["name"]
                url = article["url"]
                description = article["description"]
                date_published = article["datePublished"]

                date_obj = datetime.fromisoformat(date_published.replace('Z', '+00:00'))

                # Format the datetime object into a more readable string
                # For example: "January 09, 2024 at 21:18"
                readable_date = date_obj.strftime("%B %d, %Y at %H:%M")

                message = F"📖 {name}\n" \
                    F"🔗 {url}\n" \
                    F"📅 {readable_date}\n" \
                    F"📃 {description}\n\n"

                message_response.append(message)


            concatenated_snippets = ' '.join(message_response)

            return concatenated_snippets

        else:
            return "No news results found."
    
    except Exception as ex:
        return f"Something went wrong: {ex}"

def annas_response(text, history, content, filetype, sort):
    """
    Use Annas API to perform a journal search.
    """
    try:
  
        url_base = "https://annas-archive.org/search?"

        title = text.replace(" ", "+")

        final_url = f"{url_base}index=&q={title}&content={content}&ext={filetype}&sort={sort}&lang=en"

        json_response = get_books(get_soup_from_internet(final_url))

        message = []

        for key in json_response:
            item = json_response[key]
            
            message.append({
                "title": item["title"],
                "authors": item["authors"],
                "href": item["href"]
            })

        formatted_message = f"{final_url}\n\n"

        for book in message:
            authors = book["authors"].replace(";", ", ")  # Simplify the authors string
            
            book_entry = f"📖  {book['title']}\n" \
                        f"👥  {authors}\n" \
                        f"🔗 **www.annas-archive.org{book['href']}**\n\n" \
                        
            formatted_message += book_entry

        return formatted_message

    except Exception as ex:
        return f"Something went wrong: {ex}"

def parse_indeed_feed(text, history, location):
    """
    Fetch and parse the Indeed jobs RSS feed, returning jobs in a chatbot-friendly format.
    """

    # Replace 'your_rss_feed_url' with your actual RSS feed URL
    rss_feed_url = f"https://www.indeed.com/rss?q={text}&l={location}&sort=date"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        # Fetch the RSS feed data
        response = requests.get(rss_feed_url, headers=headers)
        response.raise_for_status()
        
        # Parse the XML from the response content
        root = ET.fromstring(response.content)
        
        messages = []  # Will hold our job postings formatted for the chatbot
        
        # Iterate over each item in the feed
        for item in root.findall('.//item'):
            title = item.find('title').text
            link = item.find('link').text
            description = item.find('description').text.replace('&lt;br&gt;', '\n').replace('&amp;#8230;', '...')
            
            # Construct the message
            message = F"📖 {title}\n" \
                      F"🔗 {link}\n" \
                      F"📃 {description}\n\n"
            
            messages.append(message)
            
        return ' '.join(messages)
    
    except Exception as ex:
        return F"Something went wrong: {ex}"

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

    # GoogleGemini Tab
    with gr.Tab("GeminiChat"):
        gr.Markdown(f"<p>{'Use Google Gemini with optional parameters below'}</p>")

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
            value = f"You are Google Gemini, a large language model trained by Google based on the GPT architecture.",
            render = False
            )

        chat = gr.ChatInterface(
            fn = google_chat_response,
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

    # TTS Tab
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

    # WebChat Tab
    with gr.Tab("WebSearch"):
        gr.Markdown(f"<p>{'Get Web Search Snippets'}</p>")

        bot = gr.Chatbot(render=False)

        chat = gr.ChatInterface(
            fn = bing_search,
            chatbot = bot,
        )

    # NewsChat Tab
    with gr.Tab("NewsSearch"):
        gr.Markdown(f"<p>{'Get News Search Snippets'}</p>")

        bot = gr.Chatbot(render=False)

        chat = gr.ChatInterface(
            fn = bing_news,
            chatbot = bot,
        )

    # AnnasChat Tab
    with gr.Tab("AnnasSearch"):
        gr.Markdown(f"<p>{'Use search terms to get journal links'}</p>")

        bot = gr.Chatbot(render=False)

        with gr.Row():
            content_dropdown = gr.Dropdown(
                ["book_nonfiction", "book_fiction", "book_unknown", "journal_article", "book_comic", "magazine", "standards_document"],
                label = "Content Type",
                value = "journal_article",
                render = True
            )

            filetype_dropdown = gr.Dropdown(
                ["pdf", "epub", "cbr", "mobi", "fb2", "cbz", "azw3", "djvu", "fb2.zip"],
                label = "File Type",
                value = "pdf",
                render = True
            )

            sort_dropdown = gr.Dropdown(
                ["newest", "oldest", "largest", "smallest"],
                label = "Order by",
                value = "newest",
                render = True
            )


        chat = gr.ChatInterface(
            fn = annas_response,
            chatbot = bot,
            additional_inputs = [content_dropdown, filetype_dropdown, sort_dropdown]
        )

    # IndeedChat Tab
    with gr.Tab("IndeedSearch"):
        gr.Markdown(f"<p>{'Use search terms to get job openings'}</p>")

        bot = gr.Chatbot(render=False)

        with gr.Row():
            location_dropdown = gr.Textbox(
                label = "Location",
                value = "Remote",
                render = True
            )

        chat = gr.ChatInterface(
            fn = parse_indeed_feed,
            chatbot = bot,
            additional_inputs = [location_dropdown]
        )


if __name__ == "__main__":
    demo.queue()
    # # Toggle this on if you want to share you app, change the username and password
    # demo.launch(server_port=7862, share=True, auth=("admin", "password"))

    # Toggle this on if you want to only run local
    demo.launch(server_port=7862)
