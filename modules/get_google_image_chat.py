import os
import PIL
from PIL import Image
import base64
import io
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define necessary variables and create a global client
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Create the global genai client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Create the chat at the global level to persist the history
MODEL_ID = "gemini-2.0-flash-exp"
chat = client.chats.create(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        response_modalities=["Text", "Image"]
    ),
)

def google_image_chat_response(message, history, input_image=None):
    """
    Sends a message to the Google Gemini model (via persisted chat instance)
    and processes the response.

    Args:
        message (str): The input message or prompt.
        history (list): Chat history to display.
        input_image (str): Filepath to an optional input image.

    Returns:
        tuple: Text response and, optionally, an output image if generated.
    """
    print(f"Message: {message}")
    print(f"History: \n{history}")

    try:
        # Send a message with or without an image
        if input_image:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    message,
                    PIL.Image.open(input_image)
                ],
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
        else:
            response = chat.send_message(message)

        text = None
        image = None

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text = part.text
                print("Received Text Response: ", text)
            if part.inline_data is not None:
                mime = part.inline_data.mime_type
                print("Received Mime Type: ", mime)
                # Process image data if present
                if mime.startswith("image/"):
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))

        # Return the text and image response (or warnings if no response)
        return text if text else "No text response received.", image

    except Exception as e:
        print(f"Error Occurred: {str(e)}")
        return f"{type(e).__name__}: {e}", None