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

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Set up your OpenAI API key:

- Rename `.env.example` to `.env`:

  ```
  mv .env.example .env
  windows:
  move .env.example .env
  ```
- Replace `your_openai_key` with your actual OpenAI API key.
  ```
  OPENAI_API_KEY=your_openai_key
  ```

## Running the Chatbot

1. Start the chatbot application by double clicking on the `startup_chat.bat` file.

2. Access the Gradio interface through the URL displayed in the terminal.

3. Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.





