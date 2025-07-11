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

# Bounding Box System Instructions
bounding_box_system_instructions = """
    Return bounding boxes as a JSON array with labels. Never return masks or code fencing. 
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, count etc.).
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

    return image

def detect_objects(image_path, prompt):
    """
    Load an image and use the Gemini API for object detection and bounding box generation.
    """
    im = Image.open(image_path)
    im.thumbnail([640, 640], Image.Resampling.LANCZOS)

    # Prompt the model
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt, im],
        config=types.GenerateContentConfig(
            system_instruction=bounding_box_system_instructions,
            temperature=0.5,
            safety_settings=safety_settings,
        ),
    )
    print(f"Model Response: {response.text}")
    return im, response.text

def run_detection(prompt, image):
    image, bounding_boxes = detect_objects(image, prompt)
    output_image = plot_bounding_boxes(image, bounding_boxes)
    return(output_image)