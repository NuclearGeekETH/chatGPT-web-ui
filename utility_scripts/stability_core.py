import os
import requests
from dotenv import load_dotenv

load_dotenv()

stability_key = os.getenv('STABILITY_API_KEY')

prompt = "smiling sexy attractive 39 year old handsome cartoon bearded smart guy with glasses, blonde curly hair"

response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/core",
    headers={
        "authorization": f"Bearer {stability_key}",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": prompt,
        "output_format": "webp",
    },
)

if response.status_code == 200:
    with open("./stable_core.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))

response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
    headers={
        "authorization": f"Bearer {stability_key}",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": prompt,
        "output_format": "jpeg",
    },
)

if response.status_code == 200:
    with open("./stable3.jpeg", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))