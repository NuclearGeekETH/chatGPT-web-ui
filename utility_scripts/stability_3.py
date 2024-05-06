import os
import requests
from dotenv import load_dotenv

load_dotenv()

stability_key = os.getenv('STABILITY_API_KEY')

prompt = "Generate an ultra-detailed, high-resolution image that depicts a bustling, futuristic cityscape at dusk, blending elements of cyberpunk aesthetics with green, sustainable architecture. The city should feature a wealth of contrasting styles: towering graphene skyscrapers with glowing neon advertisements, lush rooftop gardens, and winding canals used by autonomous water taxis. The atmosphere should be dynamic, with drones buzzing overhead and holographic billboards displaying animated ads. Include diverse pedestrians interacting with advanced technologies such as augmented reality interfaces, visible through transparent, digital displays they wear or manipulate with gestures. The lighting should be dramatic, with the setting sun casting golden hues that contrast sharply with the deep blues of the approaching night sky and the vibrant neon lights of the city. The scene should also capture reflections in the water and on the glossy surfaces of buildings with intricate, realistic textures like weathered concrete, polished glass, and brushed steel."


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
    with open("./test.jpeg", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))