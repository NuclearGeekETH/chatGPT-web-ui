# NuclearGeek's ChatGPT

NuclearGeek's ChatGPT is an interactive chatbot application utilizing OpenAI's GPT Language Models. With a user-friendly Gradio interface, it allows the user to communicate with the ChatGPT, save and reset chat history, and easily continue an old conversation. The application supports multiple GPT models and is designed with a set of examples to provide a good starting point for various conversational scenarios.

## Installation & Setup

1. Clone the repository:

```
git clone https://github.com/yourusername/nucleargeeks-chatgpt.git
```

2. Navigate to the project directory:

```
cd nucleargeeks-chatgpt
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Set up your OpenAI API key:

- Create a `.env.example` file in the project directory with the following content:

  ```
  openai_key=your_openai_key
  ```

- Replace `your_openai_key` with your actual OpenAI API key.

- Rename `.env.example` to `.env`:

  ```
  mv .env.example .env
  ```

## Running the Chatbot

1. Start the chatbot application by running:

```
python chatgpt.py
```

2. Access the Gradio interface through the URL displayed in the terminal.

3. Choose a GPT model, enter a system message or select one from the provided examples, and start chatting with the chatbot.

4. If you have previous chat history, paste it in the 'Previous Chat History' textbox.

5. To clear the chat history during a session, check the 'Clear chat history' checkbox.
