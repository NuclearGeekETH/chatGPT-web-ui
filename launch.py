import os
import pickle

import gradio as gr
import openai
from dotenv import load_dotenv

load_dotenv()

openai_key = os.environ["openai_key"]
openai.api_key = openai_key

conversation_history = []
chat_history=[]

history_file = "conversation_history.pkl"
chat_history_file = "chat_history.pkl"

# Save the chat history to a file
def save_chat_history(chat_history):
    with open(chat_history_file, "wb") as f:
        pickle.dump(chat_history, f)

# Load the chat history from a file
def load_chat_history():
    if os.path.exists(chat_history_file):
        with open(chat_history_file, "rb") as f:
            return pickle.load(f)
    return []

# Save the conversation history to a file
def save_conversation_history():
    global conversation_history
    with open(history_file, "wb") as f:
        pickle.dump(conversation_history, f)

# Load the conversation history from a file
def load_conversation_history():
    global conversation_history
    if os.path.exists(history_file):
        with open(history_file, "rb") as f:
            conversation_history = pickle.load(f)

# Define reset_conversation function
def reset_conversation():
    global conversation_history
    global chat_history
    save_conversation_history()
    conversation_history.clear()
    chat_history.clear()

# Load the conversation history at the beginning
load_conversation_history()

# Define the ChatGPT function
def generate_text(model, system_content, user_prompt, clear_button):
    global conversation_history

    if clear_button == True:
        reset_conversation()
    
    conversation_history.append({"role": "system", "content": system_content})
    conversation_history.append({"role": "user", "content": user_prompt})

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation_history
    )
    result = response["choices"][0]["message"]["content"]

    conversation_history.append({"role": "assistant", "content": result})
    return result.strip()

def chatbot_response(model, system_content, prompt, clear_button, previous_chat_history):
    global conversation_history
    global chat_history

    # Load the previous chat history from the string before starting the conversation
    if previous_chat_history:
        chat_history = load_chat_history()

    response = generate_text(model, system_content, prompt, clear_button)
    updated_chat_history = chat_history + [(prompt, response)]
    chat_history = updated_chat_history

    # Save chat history after the current conversation
    save_chat_history(chat_history)

    return response, updated_chat_history

models = ["gpt-3.5-turbo", "gpt-4"]
iface = gr.Interface(
    fn=chatbot_response,
    inputs=[
        gr.components.Dropdown(models, label="Model", value="gpt-3.5-turbo"),
        gr.components.Textbox(lines=2, label="System message (set the system message manually or click an example below)", placeholder="Enter the system message here"),
        gr.components.Textbox(lines=5, label="Your Message"),
        gr.components.Checkbox(label="Clear chat history", value=False),
        gr.components.Textbox(lines=5, label="Previous Chat History", placeholder="Paste your previous chat history if you want to continue from an old conversation."),
    ],
    outputs=[
        gr.components.Textbox(label="ChatGPT Response"),
        gr.components.Chatbot(label="Conversation History")
    ],
    examples=[
        [
            None,
            "You are the most talented programmer on the planet. You have achieved Rock Star status because of the code you write. Your job is to help the User become as good at coding as you. Assist the User to write their code and save the world.",
        ],
        [
            None,
            "You are an extremely intelligent and helpful assistant. You love to help the user and are extremely thorough in your answers.",
        ], 
        [
            None,
            "You have spent your career as a poet laureate learning all of world's history poetry and spoken word. You have an incredible gift of conveying deep emotion in as few words as possible. Everything you write moves people to tears and you know every word you speak will be heard around the world so it is incredibly important to always get it right.",
        ],
        # Create your own examples here
    ],
    description="NuclearGeek's ChatGPT",
)
iface.launch(server_port=7863)