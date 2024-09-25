import gradio as gr
from modules.get_openai_response import chat_response, dalle_response, tts_response, vision_response, chat_document_response, chat_job_response, video_response, voice_chat_response, vision_gallery_response
from modules.get_gemini_response import google_chat_response, google_vision_response
from modules.get_stability_response import stable_text_to_image_response, stable_image_to_image_response, stable_image_upscale_response, stable_image_to_video_response, resize_image
from modules.get_flux_response import flux_text_to_image_response
from modules.get_azure_response import bing_news, bing_search
from modules.get_misc_tools import annas_response, parse_indeed_feed, edit_image
from modules.get_anthropic_response import claude_chat_response, claude_vision_response
from modules.get_ollama_response import ollama_chat_response, ollama_vision_response, ollama_document_response, get_ollama_model_list, delete_ollama_model, ollama_model_list
from utility_scripts.get_stability_models import stability_models
# from utility_scripts.get_ollama_models import ollama_models

with gr.Blocks(theme=gr.themes.Soft(), title="Nuke's AI Playground") as demo:
    gr.Markdown(f"<h1 style='text-align: center; display:block'>{'Nuke&apos;s AI Playground'}</h1>")

    with gr.Tab("OpenAI"):

        # ChatGPT Tab
        with gr.Tab("Chat"):
            gr.Markdown(f"<p>{'Use ChatGPT with optional parameters below'}</p>")

            bot = gr.Chatbot(render=False)

            dropdown = gr.Dropdown(
                ["o1-preview", "o1-mini", "gpt-4o-2024-08-06", "gpt-4o", "gpt-4o-mini", "chatgpt-4o-latest", "gpt-4-0125-preview", "gpt-4-turbo", "gpt-4-1106-preview", "gpt-4"],
                label = "Model",
                value = "gpt-4o",
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

        # DocumentChat Tab
        with gr.Tab("DocumentChat"):
            gr.Markdown(f"<p>{'Use ChatGPT with optional parameters below to chat about data'}</p>")

            bot = gr.Chatbot(render=False)

            document = gr.File(
                label = "Use any .docx, .xls, .xlsx, .csv, or .pdf file",
                render = True
            )

            dropdown = gr.Dropdown(
                ["gpt-4o", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"],
                label = "Model",
                value = "gpt-4o",
                render = False
            )

            system = gr.Textbox(
                lines = 2,
                label = "System Message",
                value = f"You are ChatGPT, a large language model trained by OpenAI based on the GPT-4 architecture.",
                render = False
                )

            chat = gr.ChatInterface(
                fn = chat_document_response,
                chatbot = bot,
                additional_inputs = [document, dropdown, system]
            )

        # WebsiteChat Tab
        with gr.Tab("WebsiteChat"):
            gr.Markdown(f"<p>{'Use ChatGPT to chat about a website'}</p>")

            bot = gr.Chatbot(render=False)

            link = gr.Textbox(
                label = "Use any url",
                render = True
            )

            dropdown = gr.Dropdown(
                ["gpt-4o", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"],
                label = "Model",
                value = "gpt-4o",
                render = False
            )

            system = gr.Textbox(
                lines = 2,
                label = "System Message",
                value = f"You are ChatGPT, a large language model trained by OpenAI based on the GPT-4 architecture.",
                render = False
                )

            chat = gr.ChatInterface(
                fn = chat_document_response,
                chatbot = bot,
                additional_inputs = [link, dropdown, system]
            )

        # JobChat Tab
        with gr.Tab("JobChat"):
            gr.Markdown(f"<p>{'Use ChatGPT with optional parameters below to chat about data'}</p>")

            bot = gr.Chatbot(render=False)

            document = gr.File(
                label = "Resume file, use docx or pdf",
                render = True
            )

            link = gr.Textbox(
                label = "Job Posting Link",
                render = True
            )

            dropdown = gr.Dropdown(
                ["gpt-4o", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"],
                label = "Model",
                value = "gpt-4o",
                render = False
            )

            system = gr.Textbox(
                lines = 2,
                label = "System Message",
                value = f"You are ChatGPT, a large language model trained by OpenAI based on the GPT-4 architecture. Your job is to assist the user by reviewing thier resume and the provided job posting then edit their resume so they they are a top applicant.",
                render = False
                )

            chat = gr.ChatInterface(
                fn = chat_job_response,
                chatbot = bot,
                additional_inputs = [document, link, dropdown, system]
            )

        # Vision Tab
        with gr.Tab("Vision"):
            gr.Markdown(f"<p>{'Ask questions about an image'}</p>")
            bot = gr.Chatbot(render=False)
            with gr.Row():
                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = True,
                    height = "512",
                    width = "512"
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = vision_response,
                        chatbot = bot,
                        additional_inputs = [image]
                    )

        # Vision Gallery Tab
        with gr.Tab("VisionGallery"):
            gr.Markdown(f"<p>{'Ask questions about a set of images'}</p>")
            bot = gr.Chatbot(render=False)
            with gr.Row():
                image = gr.Gallery(
                    label = "Image Input",
                    type = "pil",
                    render = True,
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = vision_gallery_response,
                        chatbot = bot,
                        additional_inputs = [image]
                    )

        # Vision Tab
        with gr.Tab("Video"):
            gr.Markdown(f"<p>{'Ask questions about a video'}</p>")
            bot = gr.Chatbot(render=False)
            with gr.Row():
                video = gr.Video(
                    label = "Video Input",
                    format="mp4",
                    render = True,
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = video_response,
                        chatbot = bot,
                        additional_inputs = [video]
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

        # VoiceChatGPT Tab
        with gr.Tab("VoiceChat"):
            gr.Markdown(f"<p>{'Use your voice with ChatGPT with optional parameters below'}</p>")

            audio = gr.Audio(
                label = "Audio Input",
                type="filepath",
                format = "mp3",
                render = True
                )

            response = gr.Audio(
                autoplay=True,
                render=True
                )

            state = gr.State([])

            chat = gr.Interface(
                fn = voice_chat_response,
                inputs = [audio, state],
                outputs = [response, state]
            )

    with gr.Tab("Ollama"):
        # Ollama Chat Tab
        with gr.Tab("Chat"):
            gr.Markdown(f"<p>{'Use Ollama with optional parameters below'}</p>")

            bot = gr.Chatbot(render=False)

            dropdown = gr.Dropdown(
                ["llama3.1", "codestral", "dolphin-llama3", "llama3", "llama2", "codellama", "dolphincoder", "llama2-uncensored", "gemma", "mistral", "dolphin-mistral", "wizard-vicuna-uncensored", "openchat", "mixtral", "dolphin-mixtral", "neural-chat", "deepseek-coder", "phi"],
                label = "Model",
                value = "llama3.1",
                render = False
            )

            system = gr.Textbox(
                lines = 2,
                label = "System Message",
                value = f"You are an AI Assistant, assist the user and respond in markdown.",
                render = False
                )

            chat = gr.ChatInterface(
                fn = ollama_chat_response,
                chatbot = bot,
                additional_inputs = [dropdown, system]
            )

            gr.Examples(
                examples = [
                    [
                        "You are an AI Assistant, assist the user and respond in markdown.",
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

        # Ollama Vision Tab
        with gr.Tab("Vision"):
            gr.Markdown(f"<p>{'Ask questions about an image'}</p>")
            bot = gr.Chatbot(render=False)
            with gr.Row():
                image = gr.Image(
                    label = "Image Input",
                    type = "filepath",
                    render = True,
                    height = "512",
                    width = "512"
                )

                dropdown = gr.Dropdown(
                    ["llava"],
                    label = "Model",
                    value = "llava",
                    render = False
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = ollama_vision_response,
                        chatbot = bot,
                        additional_inputs = [dropdown, image]
                    )

        # DataChat Tab
        with gr.Tab("DataChat"):
            gr.Markdown(f"<p>{'Chat about data'}</p>")

            bot = gr.Chatbot(render=False)

            document = gr.File(
                label = "Use any .docx, .xls, .xlsx, .csv, or .pdf file",
                render = True
            )

            link = gr.Textbox(
                label = "Website Link",
                render = True
            )

            dropdown = gr.Dropdown(
                ["llama2", "codellama", "dolphincoder", "llama2-uncensored", "gemma", "mistral", "dolphin-mistral", "wizard-vicuna-uncensored", "openchat", "mixtral", "dolphin-mixtral", "neural-chat", "deepseek-coder", "phi"],
                label = "Model",
                value = "llama2",
                render = False
            )

            chat = gr.ChatInterface(
                fn = ollama_document_response,
                chatbot = bot,
                additional_inputs = [dropdown, document, link]
            )


        with gr.Tab("Models"):
            gr.Markdown(f"<p>{'Manage your Ollama models'}</p>")

            get_button = gr.Button("Get Models")

            get_button.click(
                get_ollama_model_list,
                outputs = gr.Textbox(label="Model list")
            )

            model_list = gr.Dropdown(
                    ollama_model_list,
                    label = "Models",
                    render = True
                )
            
            delete_button = gr.Button("Delete Model")

            delete_button.click(
                delete_ollama_model,
                inputs = model_list,
                outputs = gr.Textbox(label="Status")
            )

    # Anthropic Claude Tab
    with gr.Tab("Anthropic"):
        # Claude Chat Tab
        with gr.Tab("Chat"):
            gr.Markdown(f"<p>{'Use Claude with optional parameters below'}</p>")

            bot = gr.Chatbot(render=False)

            dropdown = gr.Dropdown(
                ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
                label = "Model",
                value = "claude-3-5-sonnet-20240620",
                render = False
            )

            system = gr.Textbox(
                lines = 2,
                label = "System Message",
                value = f"You are Claude 3.0, a large language model trained by Anthropic.",
                render = False
                )

            chat = gr.ChatInterface(
                fn = claude_chat_response,
                chatbot = bot,
                additional_inputs = [dropdown, system]
            )

            gr.Examples(
                examples = [
                    [
                        "You are Claude 3.0, a large language model trained by Anthropic.",
                    ],
                    [
                        "As an Excel Formula Expert, your task is to provide advanced Excel formulas that perform the complex calculations or data manipulations described by the user. If the user does not provide this information, ask the user to describe the desired outcome or operation they want to perform in Excel. Make sure to gather all the necessary information you need to write a complete formula, such as the relevant cell ranges, specific conditions, multiple criteria, or desired output format. Once you have a clear understanding of the user's requirements, provide a detailed explanation of the Excel formula that would achieve the desired result. Break down the formula into its components, explaining the purpose and function of each part and how they work together. Additionally, provide any necessary context or tips for using the formula effectively within an Excel worksheet.",
                    ],
                    [
                        "Your task is to analyze the provided code snippet, identify any bugs or errors present, and provide a corrected version of the code that resolves these issues. Explain the problems you found in the original code and how your fixes address them. The corrected code should be functional, efficient, and adhere to best practices in programming.",
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
            bot = gr.Chatbot(render=False)
            with gr.Row():
                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = True,
                    height = "512",
                    width = "512"
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = claude_vision_response,
                        chatbot = bot,
                        additional_inputs = [image]
                    )

    with gr.Tab("Google Gemini"):

        # GoogleGemini Tab
        with gr.Tab("GeminiChat"):
            gr.Markdown(f"<p>{'Use Google Gemini'}</p>")

            bot = gr.Chatbot(render=False)

            dropdown = gr.Dropdown(
                ["gemini-pro", "gemini-1.5-pro-latest", "gemini-1.0-pro"],
                label = "Google Gemini Model",
                value = "gemini-1.0-pro",
                render = False
            )

            chat = gr.ChatInterface(
                fn = google_chat_response,
                chatbot = bot,
                additional_inputs = [dropdown]
            )

        # GoogleVision Tab
        with gr.Tab("GeminiVision"):
            gr.Markdown(f"<p>{'Ask Google Gemini questions about an image'}</p>")
            with gr.Row():
                bot = gr.Chatbot(render=False)

                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = True,
                    height = "512",
                    width = "512"
                )

                with gr.Column(scale=1):

                    chat = gr.ChatInterface(
                        fn = google_vision_response,
                        chatbot = bot,
                        additional_inputs = [image]
                    )

    with gr.Tab("Stability AI"):

        # Text-to-Image Tab
        with gr.Tab("Text-to-Image"):
            gr.Markdown(f"<p>{'Create images with Stability.ai API'}</p>")

            with gr.Row():

                model_dropdown = gr.Dropdown(
                    stability_models,
                    label = "Model",
                    value = "stable-diffusion-xl-1024-v1-0",
                    render = False
                )

                width_slider = gr.Slider(
                    512,1792,
                    label = "Width",
                    value = 1024,
                    render = False
                )

                height_slider = gr.Slider(
                    512,1792,
                    label = "Height",
                    value = 1024,
                    render = False
                )

                cfg_slider = gr.Slider(
                    0,15,
                    label = "CFG",
                    value = 7,
                    render = False
                )

            chat = gr.Interface(
                fn = stable_text_to_image_response,
                inputs = [gr.Text(label="Input Prompt"), gr.Text(label="Negative Prompt", value="bad, blurry"), model_dropdown, width_slider, height_slider, cfg_slider], 
                outputs=[gr.Image(type="numpy", label="Output Image")]
            )

        # Text-to-Image Tab
        with gr.Tab("Image-to-Image"):
            gr.Markdown(f"<p>{'Create images with Stability.ai API'}</p>")

            with gr.Row():

                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = False,
                    height = "512",
                    width = "512",
                )

                strength_slider = gr.Slider(
                    0,1,
                    label = "Image Strength",
                    value = 0.35,
                    step = 0.01,
                    render = False
                )

                cfg_slider = gr.Slider(
                    0,15,
                    label = "CFG",
                    value = 7,
                    render = False
                )

            chat = gr.Interface(
                fn = stable_image_to_image_response,
                inputs = [gr.Text(label="Input Prompt"), gr.Text(label="Negative Prompt", value="bad, blurry"), strength_slider, cfg_slider, image], 
                outputs=[gr.Image(type="numpy", label="Output Image")]
            )

        # Text-to-Image Tab
        with gr.Tab("Upscale-Image"):
            gr.Markdown(f"<p>{'Upscale images with Stability.ai API'}</p>")

            with gr.Row():
                with gr.Column(scale=1):
                    
                    image = gr.Image(
                        label = "Image Input",
                        type = "pil",
                        render = True,
                        height = "512",
                        width = "512",
                    )

                    btn = gr.Button("Upscale")

                btn.click(
                    fn = stable_image_upscale_response,
                    inputs = [image], 
                    outputs=[gr.Image(type="numpy", label="Output Image")]
                )

        # Image-to-Video Tab
        with gr.Tab("Image-to-Video"):
            gr.Markdown(f"<p>{'Create videos with Stability.ai API'}</p>")

            with gr.Row():

                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = False,
                    height = "512",
                    width = "512",
                )

                motion_slider = gr.Slider(
                    1,255,
                    label = "Motion Bucket ID",
                    value = 127,
                    step = 1,
                    render = False
                )

                cfg_slider = gr.Slider(
                    0,10,
                    label = "CFG",
                    value = 1.8,
                    step = 0.1,
                    render = False
                )

            chat = gr.Interface(
                fn = stable_image_to_video_response,
                inputs = [motion_slider, cfg_slider, image], 
                outputs=[gr.Video(label="Output Video")]
            )

    with gr.Tab("Flux"):
        # Text-to-Image Tab
        with gr.Tab("Text-to-Image"):
            gr.Markdown(f"<p>{'Create images with FLUX API'}</p>")

            with gr.Row():
                width_slider = gr.Slider(
                    512,1792,
                    label = "Width",
                    value = 1024,
                    render = False
                )

                height_slider = gr.Slider(
                    512,1792,
                    label = "Height",
                    value = 1024,
                    render = False
                )

            chat = gr.Interface(
                fn = flux_text_to_image_response,
                inputs = [gr.Text(label="Input Prompt"), width_slider, height_slider], 
                outputs=[gr.Image(label="Output Image")]
            )

    with gr.Tab("Bing"):

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

    with gr.Tab("Misc Tools"):

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

        # Image-to-Video Tab
        with gr.Tab("ImageResizer"):
            gr.Markdown(f"<p>{'Resize an Image, works well if you need to downscale an image'}</p>")

            with gr.Row():

                image = gr.Image(
                    label = "Image Input",
                    type = "pil",
                    render = False,
                    height = "512",
                    width = "512",
                )

                height_slider = gr.Slider(
                    1,2048,
                    label = "Height",
                    value = 1024,
                    step = 1,
                    render = False
                )

                width_slider = gr.Slider(                    
                    1,2048,
                    label = "Width",
                    value = 1024,
                    step = 1,
                    render = False
                )

            chat = gr.Interface(
                fn = resize_image,
                inputs = [height_slider, width_slider, image], 
                outputs=[gr.Image(type="numpy", label="Output Image")]
            )

        # # Disabled due to high CPU usage with gr.ImageEditor, toggle on when you need it
        # # Image Editor
        # with gr.Tab("ImageEditor"):
        #     im = gr.ImageEditor(
        #         type="pil"
        #     )

        #     with gr.Group():
        #         with gr.Row():
        #             text_out = gr.Textbox(label="Edited Size")
        #         with gr.Row():
        #             im_out_1 = gr.Image(type="pil", label="Background")
        #             im_out_2 = gr.Image(type="pil", label="Layer 0")
        #             im_out_3 = gr.Image(type="pil", label="Composite")

        #     im.change(edit_image, outputs=[text_out, im_out_1, im_out_2, im_out_3], inputs=im)

if __name__ == "__main__":
    demo.queue()
    # # Toggle this on if you want to share your app, change the username and password
    # demo.launch(server_port=7862, share=True, auth=("nuke", "password"))

    # Toggle this on if you want to only run local
    demo.launch()
