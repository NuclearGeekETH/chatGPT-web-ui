import requests
import base64
import numpy as np
import io
import os
import time
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

# List of allowed sizes (width, height)
allowed_sizes = [
    (1024, 1024), (1152, 896), (1216, 832), (1344, 768),
    (1536, 640), (640, 1536), (768, 1344), (832, 1216),
    (896, 1152)
]

def resize_to_nearest_allowed_size(image):
    """
    Resize the image to the nearest allowed size with the same orientation, 
    maintaining the aspect ratio.
    """
    current_size = (image.width, image.height)
    current_aspect_ratio = current_size[0] / current_size[1]
    current_orientation = 'portrait' if current_size[0] < current_size[1] else 'landscape'
    
    if current_size not in allowed_sizes:
        # Filter allowed sizes based on the orientation of the original image.
        allowed_sizes_orientation_filtered = [
            size for size in allowed_sizes if (
                ('portrait' if size[0] < size[1] else 'landscape') == current_orientation
            )
        ]
        
        # Calculate the difference in aspect ratio between current size and each allowed size,
        # favoring those with the same orientation.
        size_differences = [(
            abs(current_aspect_ratio - (size[0] / size[1])),
            size)
            for size in allowed_sizes_orientation_filtered]
        
        # Sort sizes by their aspect ratio differences and choose the one with the smallest difference.
        nearest_size = sorted(size_differences, key=lambda x: x[0])[0][1]
        
        # Resize the image to the nearest allowed size with the same orientation
        print(f"Resizing image to nearest allowed size with same orientation: {nearest_size}")
        image = image.resize(nearest_size, Image.Resampling.LANCZOS)
    
    return image

def stable_image_to_image_response(positive_prompt, negative_prompt, strength_slider, cfg, image=None):
    if image:
        try:
            if int(image.width) * int(image.height) > 5242880:
                print("Resizing image because it's larger than 5MB")
                image = resize_to_nearest_allowed_size(image)

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

def stable_image_upscale_response(image=None):
    if image:
        try:
            if int(image.width) * int(image.height) > 5242880:
                print("Resizing image because it's larger than 5MB")
                image = resize_to_nearest_allowed_size(image)

            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            response = requests.post(
                f"https://api.stability.ai/v1/generation/esrgan-v1-x2plus/image-to-image/upscale",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {stability_key}"
                },
                files={
                    "image": buffered
                },
                data={
                    "height": int(image.height) * 2
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

# List of allowed sizes (width, height)
svd_allowed_sizes = [
    (1024, 576), (576, 1024), (768, 768)
]

def resize_to_nearest_allowed_size(image):
    """
    Resize the image to the nearest allowed size with the same orientation, 
    maintaining the aspect ratio.
    """
    current_size = (image.width, image.height)
    current_aspect_ratio = current_size[0] / current_size[1]
    current_orientation = 'portrait' if current_size[0] < current_size[1] else 'landscape'
    
    if current_size not in svd_allowed_sizes:
        # Filter allowed sizes based on the orientation of the original image.
        allowed_sizes_orientation_filtered = [
            size for size in svd_allowed_sizes if (
                ('portrait' if size[0] < size[1] else 'landscape') == current_orientation
            )
        ]
        
        # Calculate the difference in aspect ratio between current size and each allowed size,
        # favoring those with the same orientation.
        size_differences = [(
            abs(current_aspect_ratio - (size[0] / size[1])),
            size)
            for size in allowed_sizes_orientation_filtered]
        
        # Sort sizes by their aspect ratio differences and choose the one with the smallest difference.
        nearest_size = sorted(size_differences, key=lambda x: x[0])[0][1]
        
        # Resize the image to the nearest allowed size with the same orientation
        print(f"Resizing image to nearest allowed size with same orientation: {nearest_size}")
        image = image.resize(nearest_size, Image.Resampling.LANCZOS)
    
    return image

def stable_image_to_video_response(motion, cfg, image=None):
    if image:
        try:
            image = resize_to_nearest_allowed_size(image)

            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)

            response = requests.post(
                f"https://api.stability.ai/v2alpha/generation/image-to-video",
                headers={"authorization": f"Bearer {stability_key}"},
                files={"image": buffered},
                data={
                    "seed": 0,
                    "cfg_scale": cfg,
                    "motion_bucket_id": motion
                },
            )

            if response.status_code != 200:
                return(f"Non-200 response: {str(response.text)}")

            data = response.json()

            generation_id = data["id"]


            video_complete = False

            while video_complete == False:
                response = requests.request(
                    "GET",
                    f"https://api.stability.ai/v2alpha/generation/image-to-video/result/{generation_id}",
                    headers={
                        'Accept': "video/*",  # Use 'application/json' to receive base64 encoded JSON
                        'authorization': f"Bearer {stability_key}"
                    },
                )

                if response.status_code == 202:
                    print("Generation in-progress, try again in 10 seconds.")
                    time.sleep(10)
                elif response.status_code == 200:
                    print("Generation complete!")
                    video_complete = True
                    with open("video.mp4", 'wb') as file:
                        file.write(response.content)

                    return 'video.mp4'
                else:
                    raise Exception(str(response.json()))
                      
        except Exception as e:
            return(f"ERROR: {e}")
    else:
        answer = "Please upload an image"

        return(answer)

