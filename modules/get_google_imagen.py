import os
import base64
import io
from PIL import Image
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

client = genai.Client(api_key=GOOGLE_API_KEY)

def imagen_response(message):
    try:
        response = client.models.generate_image(
            model='imagen-3.0-generate-002',
            prompt=message,
            config=types.GenerateImageConfig(
                negative_prompt= 'people',
                number_of_images= 1,
                include_rai_reason= True,
                output_mime_type= 'b64_json'
            )
        )

        image_data = response.data[0].b64_json
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)

        return(img_array)
    
    except Exception as e:
        return(f"ERROR: {e}")