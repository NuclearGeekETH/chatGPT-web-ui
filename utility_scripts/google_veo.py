import time
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

client = genai.Client(api_key=GOOGLE_API_KEY)

prompt = """
Shaking a half open, half empty box of matches
"""

# GENERATE VIDEO FROM TEXT
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        person_generation="allow_adult",  # "dont_allow" or "allow_adult"
        aspect_ratio="9:16",  # "16:9" or "9:16"
        numberOfVideos=2,
        durationSeconds=8
    ),
)

while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

for n, generated_video in enumerate(operation.response.generated_videos):
    client.files.download(file=generated_video.video)
    generated_video.video.save(f"video{n}.mp4")  # save the video