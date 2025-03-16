"""
Comprehensive Python Script for Gemini 2.0 Object Detection & Spatial Understanding
Dependencies:
- google-genai
- PIL (Pillow)
- requests
Ensure all dependencies are installed and API Key is configured.
"""

import os
import json
import random
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor  # GUI creation and image handling
from google import genai
from google.genai import types  # Types for configuration
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

client = genai.Client(api_key=GOOGLE_API_KEY)

# Set the Model Name
model_name = "gemini-2.0-flash-exp"

# Bounding Box System Instructions
bounding_box_system_instructions = """
    Return bounding boxes as a JSON array with labels. Never return masks or code fencing. Limit to 25 objects.
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, etc.).
"""

# Safety Settings
safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_NONE",
    ),
]

def get_font(font_size=14):
    """
    Attempts to load a default available font for rendering text.
    """
    try:
        return ImageFont.truetype("arial.ttf", font_size)  # Use Arial on Windows
    except OSError:
        print("Default font not found, trying PIL's default font.")
        return ImageFont.load_default()
    
# Function to Parse JSON Output from the Model
def parse_json(json_output):
    """
    Parses out the fenced JSON content from the output string.
    """
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i + 1:])  # Remove everything before "```json"
            json_output = json_output.split("```")[0]  # Remove everything after the closing "```"
            break
    return json_output

# Function to Plot Bounding Boxes
def plot_bounding_boxes(image, bounding_boxes):
    """
    Plots bounding boxes on an image with names and visual markers.

    Args:
        image: The image (PIL) to annotate.
        bounding_boxes: A JSON string list of bounding box objects (box_2d, label).
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)

    colors = [
        'red', 'green', 'blue', 'yellow', 'orange',
        'pink', 'purple', 'brown', 'gray', 'beige',
        'turquoise', 'cyan', 'magenta', 'lime', 'navy'
    ] + list(ImageColor.colormap.keys())

    font = get_font(font_size=14)

    bounding_boxes = parse_json(bounding_boxes)
    for i, bounding_box in enumerate(json.loads(bounding_boxes)):
        color = colors[i % len(colors)]
        abs_y1 = int(bounding_box["box_2d"][0] / 1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1] / 1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2] / 1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3] / 1000 * width)

        if abs_x1 > abs_x2:
            abs_x1, abs_x2 = abs_x2, abs_x1
        if abs_y1 > abs_y2:
            abs_y1, abs_y2 = abs_y2, abs_y1

        draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)
        if "label" in bounding_box:
            draw.text((abs_x1 + 8, abs_y1 + 6), bounding_box["label"], fill=color, font=font)

    # Show the image
    image.show()
    image.save("output.png")


# Main Functionality: Load an Image, Prompt, Detect Objects, and Render Results
def detect_objects(image_path, prompt):
    """
    Load an image and use the Gemini API for object detection and bounding box generation.
    """
    im = Image.open(image_path)
    im.thumbnail([640, 640], Image.Resampling.LANCZOS)

    # Prompt the model
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, im],
        config=types.GenerateContentConfig(
            system_instruction=bounding_box_system_instructions,
            temperature=0.5,
            safety_settings=safety_settings,
        ),
    )
    print(f"Model Response: {response.text}")
    return im, response.text

# # Download Example Images
# def download_sample_images():
#     """
#     Downloads images from hosted URLs to local directory.
#     """
#     sample_images = {
#         "Socks.jpg": "https://storage.googleapis.com/generativeai-downloads/images/socks.jpg",
#         "Cupcakes.jpg": "https://storage.googleapis.com/generativeai-downloads/images/Cupcakes.jpg",
#         "Japanese_bento.png": "https://storage.googleapis.com/generativeai-downloads/images/Japanese_Bento.png",
#         "Origamis.jpg": "https://storage.googleapis.com/generativeai-downloads/images/origamis.jpg",
#         "Spill.jpg": "https://storage.googleapis.com/generativeai-downloads/images/spill.jpg",
#     }
#     for filename, url in sample_images.items():
#         if not os.path.exists(filename):
#             print(f"Downloading {filename}...")
#             response = requests.get(url)
#             with open(filename, "wb") as f:
#                 f.write(response.content)
#             print(f"Saved {filename} locally.")

# Entry Point
if __name__ == "__main__":
    # Download example images
    # download_sample_images()

    # Example usage
    image_file = "fruit.webp"
    example_prompt = "Detect the 2d bounding boxes of the fruit (with 'label' as fruit type)."

    # Process the Image
    image, bounding_boxes = detect_objects(image_file, example_prompt)

    # Render the Bounding Boxes
    plot_bounding_boxes(image, bounding_boxes)