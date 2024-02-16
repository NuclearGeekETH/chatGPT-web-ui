import requests
import base64
import numpy as np
import io
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

stability_key = os.getenv('STABILITY_API_KEY')

def stable_text_to_image_response(positive_prompt, negative_prompt, width, height, cfg):
    try:
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        body = {
        "steps": 40,
        "width": width,
        "height": height,
        "seed": 0,
        "cfg_scale": cfg,
        "samples": 1,
        "text_prompts": [
            {
            "text": positive_prompt,
            "weight": 1
            },
            {
            "text": negative_prompt,
            "weight": -1
            }
        ],
        }

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stability_key}",
        }

        response = requests.post(
        url,
        headers=headers,
        json=body,
        )

        if response.status_code != 200:
            return(f"Non-200 response: {str(response.text)}")

        data = response.json()

        for i, image in enumerate(data["artifacts"]):
            img_bytes = base64.b64decode(image["base64"])
            img = Image.open(io.BytesIO(img_bytes))
            img_array = np.array(img)

            return(img_array)
        
    except Exception as e:
        return(f"ERROR: {e}")

def stable_image_to_image_response(positive_prompt, negative_prompt, strength_slider, cfg, image=None):
    if image:
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {stability_key}"
                },
                files={
                    "init_image": buffered
                },
                data={
                    "init_image_mode": "IMAGE_STRENGTH",
                    "image_strength": strength_slider,
                    "steps": 40,
                    "seed": 0,
                    "cfg_scale": cfg,
                    "samples": 1,
                    "text_prompts[0][text]": positive_prompt,
                    "text_prompts[0][weight]": 1,
                    "text_prompts[1][text]": negative_prompt,
                    "text_prompts[1][weight]": -1,
                }
            )

            if response.status_code != 200:
                return(f"Non-200 response: {str(response.text)}")

            data = response.json()

            for i, image in enumerate(data["artifacts"]):
                img_bytes = base64.b64decode(image["base64"])
                img = Image.open(io.BytesIO(img_bytes))
                img_array = np.array(img)

                return(img_array)
                      
        except Exception as e:
            return(f"ERROR: {e}")
    else:
        answer = "Please upload an image"

        return(answer)
