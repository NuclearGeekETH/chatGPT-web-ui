import openai
import os
import base64
import io
import requests
import numpy as np
from dotenv import load_dotenv
from datetime import date
from PIL import Image
from pathlib import Path
from urllib.parse import urlparse
import cv2
from moviepy.editor import VideoFileClip
import time
from .get_document_data import load_document_into_memory, get_website_data

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

openai.api_key = key

def chat_response(message, history, model, system):
    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content != None:
                partial_message = partial_message + str(chunk.choices[0].delta.content)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")

def is_url(s):
    result = urlparse(s)
    return all([result.scheme, result.netloc])

def chat_document_response(message, history, document, model, system):
    if is_url(document):
        document_data = get_website_data(document)
    else:
        document_data = load_document_into_memory(document)

    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}, Document Data: {document_data}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content != None:
                partial_message = partial_message + str(chunk.choices[0].delta.content)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")

def chat_job_response(message, history, document, link, model, system):
    try:
        website_data = get_website_data(link)
        document_data = load_document_into_memory(document)
    except Exception as e:
        return f"Error"

    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}. The resume is: {document_data}. The job posting is: {website_data}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            stream=True
        )

        # Stream Response
        partial_message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content != None:
                partial_message = partial_message + str(chunk.choices[0].delta.content)
                if partial_message:
                    yield partial_message

    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")


def dalle_response(message, size, quality, style):
    try:
        response = openai.images.generate(
            model = "dall-e-3",
            prompt = message,
            size = size,
            quality = quality,
            style = style, # natural
            n = 1,
            response_format = "b64_json" # b64_json url
        )

        image_data = response.data[0].b64_json
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)

        revised_prompt = response.data[0].revised_prompt

        return(revised_prompt, img_array)
    
    except openai.BadRequestError as e:
        return(f"ERROR: {e}")

def tts_response(message, voice, model):
    speech_file_path = Path(__file__).parent / "speech.mp3"

    try:
        response = openai.audio.speech.create(
            model = model,
            voice = voice,
            input = message
        )

        response.stream_to_file(speech_file_path)

        return(speech_file_path)
    
    except Exception as e:
        #Handle API error here, e.g. retry or log
        return(f"OpenAI API returned an API Error: {e}")

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str      

def vision_response(message, history, image=None):
    history_response = []

    history_response.append({"role": "system", "content": f"You are a helpful assistant that responds in Markdown. Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    if image:
        base64_image = encode_image_to_base64(image)
        # include the image in the messages
        history_response.append({"role": "user", "content": [
                                    {"type": "text", "text": message},
                                    {"type": "image_url", "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"}
                                    }
                                ]})
        try:
            completion = openai.chat.completions.create(
                model="gpt-4o",
                messages= history_response,
                temperature=0.0,
                stream=True
            )
            # Stream Response
            partial_message = ""
            for chunk in completion:
                if chunk.choices[0].delta.content != None:
                    partial_message = partial_message + str(chunk.choices[0].delta.content)
                    if partial_message:
                        yield partial_message
        
        except Exception as e:
            #Handle API error here, e.g. retry or log
            return(f"OpenAI API returned an API Error: {e}")

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer

def vision_gallery_response(message, history, images=None):
    history_response = []

    history_response.append({"role": "system", "content": f"You are a helpful assistant that responds in Markdown. Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    if images:
        base64Frames = []
        for image, _ in images:
            base64_image = encode_image_to_base64(image)
            base64Frames.append(base64_image)
        # include the image in the messages
        history_response.append({"role": "user", "content": [
                                    "These are the frames from the video.",
                                    *map(lambda x: {"type": "image_url", 
                                                    "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames),
                                    {"type": "text", "text": message},
                                    ],
                                }
                                )
        try:
            completion = openai.chat.completions.create(
                model="gpt-4o",
                messages= history_response,
                temperature=0.0,
                stream=True
            )
            # Stream Response
            partial_message = ""
            for chunk in completion:
                if chunk.choices[0].delta.content != None:
                    partial_message = partial_message + str(chunk.choices[0].delta.content)
                    if partial_message:
                        yield partial_message
        
        except Exception as e:
            #Handle API error here, e.g. retry or log
            return(f"OpenAI API returned an API Error: {e}")

    else:
        history_response.append({"role": "user", "content": message})

        answer = "Please upload an image"

        return answer

def transcribe_audio(audio_path):
    """
    Transcribe the audio at the given path using OpenAI's Whisper model.
    """
    with open(audio_path, 'rb') as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return response
    
def voice_chat_response(message, history, model, audio):
    history_response = []

    history_response.append({"role": "system", "content": f"You are a helpful assistant. Current Date: {date.today()}"})

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    # history_response.append({"role": "user", "content": message})

    print(audio)
    
    if audio:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio, "rb"),
        )

        history_response.append({"role": "user", "content": transcription.text})

        try:
            completion = openai.chat.completions.create(
                model = model,
                messages = history_response,
                stream=True
            )

            # Stream Response
            partial_message = ""
            for chunk in completion:
                if chunk.choices[0].delta.content != None:
                    partial_message = partial_message + str(chunk.choices[0].delta.content)
                    if partial_message:
                        yield partial_message

        except Exception as e:
            #Handle API error here, e.g. retry or log
            return(f"OpenAI API returned an API Error: {e}")

def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame=0

    # Loop through the video and extract frames at specified sampling rate
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    # Extract audio from video
    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    print(f"Extracted {len(base64Frames)} frames")
    print(f"Extracted audio to {audio_path}")
    return base64Frames, audio_path



def video_response(message, history, video=None):
    history_response = []

    for human, assistant in history:
        history_response.append({"role": "user", "content": human})
        history_response.append({"role": "assistant", "content": assistant})

    history_response.append({"role": "user", "content": message})

    if video:
        # Extract 1 frame per second. You can adjust the `seconds_per_frame` parameter to change the sampling rate
        base64Frames, audio_path = process_video(video, seconds_per_frame=1)

        # response = openai.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #     {"role": "system", "content": "You are generating a video summary. Please provide a summary of the video. Respond in Markdown."},
        #     {"role": "user", "content": [
        #         "These are the frames from the video.",
        #         *map(lambda x: {"type": "image_url", 
        #                         "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
        #         ],
        #     }
        #     ],
        #     temperature=0,
        # )
        # video_summary = response.choices[0].message.content

        # Transcribe the audio
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
        )
        ## OPTIONAL: Uncomment the line below to print the transcription
        #print("Transcript: ", transcription.text + "\n\n")

        # response = openai.chat.completions.create(
        #     model="whisper-1",
        #     messages=[
        #     {"role": "system", "content":"""You are generating a transcript summary. Create a summary of the provided transcription. Respond in Markdown."""},
        #     {"role": "user", "content": [
        #         {"type": "text", "text": f"The audio transcription is: {transcription.text}"}
        #         ],
        #     }
        #     ],
        #     temperature=0,
        # )
        # audio_summary = response.choices[0].message.content
        try:
            ## Generate a summary with visual and audio
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                {"role": "system", "content":"""You are generating a video summary. Create a summary of the provided video and its transcript. Respond in Markdown"""},
                {"role": "user", "content": [
                    "These are the frames from the video.",
                    *map(lambda x: {"type": "image_url", 
                                    "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames),
                    {"type": "text", "text": f"The audio transcription is: {transcription.text}"}
                    ],
                }
            ],
                temperature=0,
                stream=True
            )
            # print(response.choices[0].message.content)

            # Stream Response
            partial_message = ""
            for chunk in response:
                if chunk.choices[0].delta.content != None:
                    partial_message = partial_message + str(chunk.choices[0].delta.content)
                    if partial_message:
                        yield partial_message

        except Exception as e:
            #Handle API error here, e.g. retry or log
            return(f"OpenAI API returned an API Error: {e}")
