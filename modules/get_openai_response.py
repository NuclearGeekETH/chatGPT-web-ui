import openai
import os
import base64
import io
import wave
import mimetypes
import numpy as np
from dotenv import load_dotenv
from datetime import date
from PIL import Image
from pathlib import Path
from urllib.parse import urlparse
import cv2
from moviepy.editor import VideoFileClip
from .get_document_data import load_document_into_memory, get_website_data

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

openai.api_key = key

def chat_response(message, history, model, system, reasoning_effort):
    print(history)

    def build_history_response(history, include_system=False):
        history_response = []
        if include_system:
            history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}"})
        for human, assistant in history:
            history_response.append({"role": "user", "content": human})
            history_response.append({"role": "assistant", "content": assistant})
        history_response.append({"role": "user", "content": message})
        return history_response

    try:
        test_models = ["o1-preview", "o1-mini"]
        reasoning_models = ["o4-mini-2025-04-16", "o3-2025-04-16", "o3-mini-2025-01-31"]

        if model in reasoning_models:
            history_response = build_history_response(history, include_system=True)
            
            # Request completion with streaming enabled
            completion = openai.chat.completions.create(
                model=model,
                messages=history_response,
                reasoning_effort=reasoning_effort,
                stream=True
            )

            # Stream Response
            partial_message = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:  # Ensure content is not None
                    partial_message += chunk.choices[0].delta.content
                    yield partial_message

        elif model in test_models:
            history_response = build_history_response(history, include_system=False)

            # Request completion without streaming
            completion = openai.chat.completions.create(
                model=model,
                messages=history_response,
            )

            answer = completion.choices[0].message.content
            yield answer

        else:
            history_response = build_history_response(history, include_system=True)

            # Request completion with streaming enabled
            completion = openai.chat.completions.create(
                model=model,
                messages=history_response,
                stream=True
            )

            # Stream Response
            partial_message = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:  # Ensure content is not None
                    partial_message += chunk.choices[0].delta.content
                    yield partial_message

    except Exception as e:
        # Handle API error: retry, log, or notify
        yield f"OpenAI API returned an API Error: {e}"

def reset_conversation():
    global last_response_id
    last_response_id = None

last_response_id = None  # For real use, store in session/state

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    mime, _ = mimetypes.guess_type(image_path)
    if mime is None:
        mime = "image/png"
    return f"data:{mime};base64,{encoded}"

def multi_modal_response(message, history, model, system):
    global last_response_id

    if system:
        if isinstance(system, dict):
            system_text = system.get("text", "")
        else:
            system_text = str(system)
        system_prompt = f"{system_text} Current Date: {date.today()}"
    else:
        system_prompt = f"Current Date: {date.today()}"

    user_text = message.get("text") if isinstance(message, dict) else str(message)
    user_files = message.get("files", []) if isinstance(message, dict) else []

    request_kwargs = {
        "model": model,
        "tools": [{"type": "image_generation"}],
        "stream": True
    }

    # --- FIRST message: full prompt/context ---
    if last_response_id is None:
        input_blocks = [{"role": "system", "content": system_prompt}]
        if user_text:
            user_content = [{"type": "input_text", "text": user_text}]
            for f in user_files:
                file_path = f if isinstance(f, str) else f.get("path")
                mime_type = f.get("mimetype") if isinstance(f, dict) else None
                if not mime_type:
                    mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type and mime_type.startswith("image/") and os.path.exists(file_path):
                    image_url = encode_image(file_path)
                    user_content.append({"type": "input_image", "image_url": image_url})

            input_blocks.append({"role": "user", "content": user_content})

        request_kwargs["input"] = input_blocks

    # --- EVERY FOLLOWUP: ONLY latest message and images + prev id ---
    else:
        content_blocks = []
        if user_text:
            user_content = [{"type": "input_text", "text": user_text}]
            for f in user_files:
                file_path = f if isinstance(f, str) else f.get("path")
                mime_type = f.get("mimetype") if isinstance(f, dict) else None
                if not mime_type:
                    mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type and mime_type.startswith("image/") and os.path.exists(file_path):
                    image_url = encode_image(file_path)
                    user_content.append({"type": "input_image", "image_url": image_url})                

            content_blocks.append({"role": "user", "content": user_content})

            request_kwargs["input"] = content_blocks

        request_kwargs["previous_response_id"] = last_response_id

    try:
        # print(f"SENDING TO OPENAI: {request_kwargs}")
        stream = openai.responses.create(**request_kwargs)

        # print(f"stream: {stream}")

        partial_message = ""
        files = []
        for event in stream:
            # print(f"event: {event}")
            etype = getattr(event, "type", None)
            # print(etype)
            if getattr(event, "type", None) == "response.completed" or event.__class__.__name__ == "ResponseCompletedEvent":
                last_response_id = event.response.id
            if etype == "response.image_generation_call.partial_image":
                idx = event.partial_image_index
                image_base64 = event.partial_image_b64
                image_bytes = base64.b64decode(image_base64)
                filename = f"river{idx}.png"
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                files.append(filename)
                yield {"text": "Image is created:", "files": files}

            if etype == "response.output_text.delta":
                if getattr(event, "delta", None):
                    partial_message += event.delta
                    yield {"text": partial_message, "files": files if files else []}

    except Exception as e:
        yield {"text": f"OpenAI API returned an API Error: {e}", "files": []}   

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

def quiz_response(message, document, model, system):
    if is_url(document):
        document_data = get_website_data(document)
    else:
        document_data = load_document_into_memory(document)

    history_response = []

    history_response.append({"role": "system", "content": f"{system} Current Date: {date.today()}, Document Data: {document_data}"})

    history_response.append({"role": "user", "content": message})

    try:
        completion = openai.chat.completions.create(
            model = model,
            messages = history_response,
            response_format={ "type": "json_object" }
        )

        completion_response = completion.choices[0].message.content

        print(completion_response)

        return completion_response

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

def convert_audio_to_pcm_base64(audio_data, sample_rate, num_channels=1, sample_width=2):
    # Ensure audio data is in the correct format
    if audio_data.dtype != np.int16:
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            # Normalize and convert to 16-bit PCM
            audio_data = (audio_data * 32767).astype(np.int16)
        else:
            raise ValueError("Audio data type conversion is required to 16-bit integer format.")

    # Create a bytes buffer to write the WAV file
    wav_buffer = io.BytesIO()

    # Establish a WAV file writer
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    # Retrieve the WAV file bytes
    wav_bytes = wav_buffer.getvalue()

    # Encode the WAV bytes into Base64
    wav_base64 = base64.b64encode(wav_bytes)

    # Return the Base64 string
    return wav_base64.decode('utf-8')

def realtime_response(text, audio_id, audio_data, voice):
    content = []
    history_response = []

    # audio = AudioSegment.from_file(io.BytesIO(audio_np))
    
    # # Resample to 24kHz mono pcm16
    # pcm_audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2).raw_data
    
    # # Encode to base64 string
    # pcm_base64 = base64.b64encode(audio_np).decode()

    if text:
        content.append({"type": "text", "text": text})

    if audio_data:
        sample_rate, audio_np = audio_data

        pcm_base64 = convert_audio_to_pcm_base64(audio_np, sample_rate)
        content.append({"type": "input_audio", "input_audio": {"data": pcm_base64, "format": "wav"}})

    # if audio_id:
    #     history_response.append({"role": "user", "content": content})

    history_response.append({"role": "user", "content": content})

    print(history_response)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
            messages=history_response
        )

        transcript = response.choices[0].message.audio.transcript
        
        print(transcript)

        try:
            wav_bytes = base64.b64decode(response.choices[0].message.audio.data)

            audio_id = response.choices[0].message.audio.id

            return transcript, wav_bytes, audio_id
        except:
            return transcript, None, None

    except Exception as e:
        print(f"Error during communication: {e}")
        return None, None, None
    
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
    
def voice_chat_response(audio, history):

    history_response = []

    history_response.append({"role": "system", "content": f"You are a helpful assistant, keep responses short and succinct as they will be spoken. Be over the top friendly. Current Date: {date.today()}"})

    for idx, item in enumerate(history):
        print(f"Processing item {idx}: {item}")
        history_response.append(item)

    if audio:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio, "rb"),
        )

        history_response.append({"role": "user", "content": transcription.text})

        try:
            completion = openai.chat.completions.create(
                model = "gpt-4o",
                messages = history_response,
            )

            completion_response = completion.choices[0].message.content

            history_response.append({"role": "assistant", "content": completion_response})

            speech_file_path = Path(__file__).parent / "speech.mp3"

            try:
                response = openai.audio.speech.create(
                    model = "tts-1",
                    voice = "shimmer",
                    input = completion_response
                )

                response.stream_to_file(speech_file_path)

                return speech_file_path, history_response
            
            except Exception as e:
                #Handle API error here, e.g. retry or log
                return(f"OpenAI API returned an API Error: {e}")

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
