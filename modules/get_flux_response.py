import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

flux_key = os.getenv('FLUX_API_KEY')

def flux_text_to_image_response(prompt, width, height):
    try:
        url = f"https://api.bfl.ml/v1/image"

        json = {
            "prompt": prompt,
            "width": width, 
            "height": height,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-key": flux_key,
        }

        response = requests.post(
            url,
            headers=headers,
            json=json,
        ).json()
      
        request_id = response["id"]

        while True:
            time.sleep(0.5)
            result = requests.get(
                'https://api.bfl.ml/v1/get_result',
                headers={
                    'accept': 'application/json',
                    'x-key': flux_key,
                },
                params={
                    'id': request_id,
                },
            ).json()
            if result["status"] == "Ready":
                print(f"Result: {result['result']['sample']}")
                return result['result']['sample']
            else:
                print(f"Status: {result['status']}")
       
    except Exception as e:
        return(f"ERROR: {e}")

