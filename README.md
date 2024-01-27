# NuclearGeek's ChatGPT

NuclearGeek's ChatGPT is an interactive chatbot application utilizing OpenAI's GPT Language Models. With a user-friendly Gradio interface, it allows the user to communicate with the ChatGPT, save and reset chat history, and easily continue an old conversation. The application supports multiple GPT models and is designed with a set of examples to provide a good starting point for various conversational scenarios. Tabs include Chat, Vision, and Dalle.

## Installation & Setup

1. Clone the repository:

```
git clone https://github.com/NuclearGeekETH/chatGPT-web-ui.git
```

2. Navigate to the project directory:

```
cd chatGPT-web-ui
```

3. Set up your OpenAI API key:

- Rename `.env.example` to `.env`:

  ```
  # For macOS and Linux:
  mv .env.example .env

  # For Windows:
  move .env.example .env
  ```
- Replace `your_openai_key` with your actual OpenAI API key.
  ```
  OPENAI_API_KEY=your_openai_key
  ```

## Running the Chatbot

### For Windows Users:

1. Start the chatbot application by double clicking on the `startup_chat.bat` file.

2. Access the Gradio interface through the URL displayed in the terminal.

3. Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.

### For macOS Users:

1. Open Terminal in your macOS.

2. Navigate to the project directory if you're not already there.

3. Before running this script on macOS, ensure you have the necessary permissions to execute it by running `chmod +x startup_chat.sh` in your terminal. This grants execution rights to the script.

4. Run the following command to start the chatbot application (assumes you have the necessary runtime environment like Python and required libraries installed):

```
bash startup_chat.sh
```

if `startup_chat.sh` does not work then setup environment manually using `python3 -m venv venv`, then use `source venv/bin/activate` and `pip install -r requirements.txt`, and finally `python3 chat_interface.py`.

5. Access the Gradio interface through the URL displayed in the Terminal.

## Common Steps

  - Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.

Note: The instructions for macOS assume that the Gradio app and any other necessary software can be started with a script similar to `startup_chat.bat` for Windows or a direct command like `python3 chat_interface.py`. If the original setup requires additional steps not covered here (like setting up a virtual environment, installing dependencies, or other preparatory steps specific to the application), you would need to follow those steps accordingly.





