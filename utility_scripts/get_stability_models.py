import requests
import os
from dotenv import load_dotenv

load_dotenv()

stability_key = os.getenv('STABILITY_API_KEY')

api_host = os.getenv('API_HOST', 'https://api.stability.ai')
url = f"{api_host}/v1/engines/list"

if stability_key is None:
    raise Exception("Missing Stability API key.")

response = requests.get(url, headers={
    "Authorization": f"Bearer {stability_key}"
})

if response.status_code != 200:
    raise Exception("Non-200 response: " + str(response.text))

# Do something with the payload...
payload = response.json()

print(payload)