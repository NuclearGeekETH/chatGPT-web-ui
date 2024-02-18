# NuclearGeek's AI Playground

NuclearGeek's AI Playground is an interactive web application utilizing multiple AI models. With a user-friendly Gradio interface, it allows the user to communicate with various OpenAI, Google Gemini and Stability.ai models including tools to analyze images with Vision, create images with Dall-e-3 or stability, search the web and news articles with Bing, search journal articles using Annas or even look for a new job with Indeed. The application supports multiple GPT and diffusion models and is designed with a set of examples to provide a good starting point for various scenarios. Tabs include OpenAI Chat, OpenAI Vision, Dall-e, Text-to-Speech, Google Gemini Chat, Google Gemini Vision, Stability.ai Text-to-Image, Stability.ai Image-to-Image, Bing Web Search, and Bing News Search.

## Installation & Setup

1. Clone the repository:

```
git clone https://github.com/NuclearGeekETH/chatGPT-web-ui.git
```

2. Navigate to the project directory:

```
cd chatGPT-web-ui
```

3. Set up your OpenAI API and Bing key:

- Rename `.env.example` to `.env`:

  ```
  # For macOS and Linux:
  mv .env.example .env

  # For Windows:
  move .env.example .env
  ```
- Replace `your_openai_key` with your actual OpenAI, Bing, Google, and Stability.ai API keys.
  ```
  OPENAI_API_KEY=your_openai_key
  BING_SEARCH_V7_SUBSCRIPTION_KEY=your_bing_key
  GOOGLE_API_KEY=your_google_key
  STABILITY_API_KEY-your_stability_key
  ```

## Links to get API Keys:

  - [OpenAI](https://platform.openai.com/docs/quickstart?context=python)

  - [Azure BING Search](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/search-api/)

  - [Google AI Studio](https://aistudio.google.com/app/apikey)

  - [Stability.ai](https://platform.stability.ai/)

## Running the Chatbot

### For Windows Users:

1. Start the chatbot application by double clicking on the `startup_chat.bat` file.

2. Access the Gradio interface through the URL displayed in the terminal.

3. Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.

### For macOS Users:

1. Open Terminal in your macOS.

2. Navigate to the project directory if you're not already there.

3. Before running this script on macOS, ensure you have the necessary permissions to execute it by running the following command in your terminal. This grants execution rights to the script:
  ```
  chmod +x startup_chat.sh
  ```

4. Run the following command to start the chatbot application (assumes you have the necessary runtime environment like Python and required libraries installed):

  ```
  bash startup_chat.sh
  ```

  if `startup_chat.sh` does not work then setup environment manually using `python3 -m venv venv`, then use `source venv/bin/activate` and `pip install -r requirements.txt`, and finally `python3 chat_interface.py`.

5. Access the Gradio interface through the URL displayed in the Terminal.

## Common Steps

  - Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.

  - For web and news search using bing, just use simple search terms like you would in a search engine.

##  Current Tabs

### OpenAI

#### Chat

OpenAI's text generation models (often called generative pre-trained transformers or large language models) have been trained to understand natural language, code, and images. The models provide text outputs in response to their inputs. The inputs to these models are also referred to as "prompts". Designing a prompt is essentially how you “program” a large language model model, usually by providing instructions or some examples of how to successfully complete a task.

Using OpenAI's text generation models, you can build applications to:

  - Draft documents
  - Write computer code
  - Answer questions about a knowledge base
  - Analyze texts
  - Give software a natural language interface
  - Tutor in a range of subjects
  - Translate languages
  - Simulate characters for games

#### Vision

GPT-4 with Vision, sometimes referred to as GPT-4V or gpt-4-vision-preview in the API, allows the model to take in images and answer questions about them. Historically, language model systems have been limited by taking in a single input modality, text. For many use cases, this constrained the areas where models like GPT-4 could be used.

GPT-4 with vision is currently available to all developers who have access to GPT-4 via the gpt-4-vision-preview model and the Chat Completions API which has been updated to support image inputs. Note that the Assistants API does not currently support image inputs.

#### Dall-e

The image generations endpoint allows you to create an original image given a text prompt. When using DALL·E 3, images can have a size of 1024x1024, 1024x1792 or 1792x1024 pixels.

By default, images are generated at standard quality, but when using DALL·E 3 you can set quality: "hd" for enhanced detail. Square, standard quality images are the fastest to generate.

#### Text-To-Speech

The Audio API provides a speech endpoint based on our TTS (text-to-speech) model. It comes with 6 built-in voices and can be used to:

  - Narrate a written blog post
  - Produce spoken audio in multiple languages
  - Give real time audio output using streaming

### Google Gemini

Gemini is a family of generative AI models that lets developers generate content and solve problems. These models are designed and trained to handle both text and images as input.

### Stability AI

Stability.ai is the company that created Stable Diffusion and SDXL. Tools available through their API are packaged here: Text-to-Image, Image-to-Image and Upscale-Image.

### Azure Bing Web and News Search

An easy-to-use, ad-free, commercial-grade search tool that lets you deliver the results you want.

### Miscellaneous Search

#### Annas Search

Search Anna's Archive. Anna's Archive mirrors Open Library, Library Genesis, Sci-Hub and Z-Library. Anna's Archive says that it does not host copyrighted materials and that it only indexes metadata that is already publicly available. As of February 1, 2024, Anna's Archive includes 25,530,302 books and 99,425,822 papers.

#### Indeed Job Search

Keyword and Location based job search using the Indeed XML feed.






