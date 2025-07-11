import os
import asyncio
import wave
from dotenv import load_dotenv
from google import genai
from google.genai import types
import io
import contextlib

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})

async def main():
    file_index = 0
    async def receive_audio(session):
        """Receives audio data from the session and writes it to a WAV file."""
        nonlocal file_index

        try:
            with wave.open(f"audio_{file_index}.wav", "wb") as wf:
                file_index += 1
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(48000)

                print(f"Starting to receive audio and save to audio_{file_index -1}.wav")
                async for message in session.receive():
                    audio_data = message.server_content.audio_chunks[0].data
                    if audio_data:
                        wf.writeframes(audio_data)

                print(f"Finished receiving audio and saving to audio_{file_index -1}.wav")

        except Exception as e:
            print(f"Receive Audio Error: {e}")

    async with client.aio.live.music.connect(model='models/lyria-realtime-exp') as session:
        print("Successfully connected to the music generation service.")
        # Create and start the receive_audio task
        receive_task = asyncio.create_task(receive_audio(session))

        try:
            # Send initial prompts and config
            print("Setting weighted prompts...")
            await session.set_weighted_prompts(
                prompts=[
                    types.WeightedPrompt(text='minimal techno', weight=1.0),
                ]
            )
            print("Weighted prompts set.")

            print("Setting music generation config...")
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0)
            )
            print("Music generation config set.")

            # Start streaming music
            print("Starting music generation...")
            await session.play()
            print("Music generation started.")

            print("Keeping the session alive for 60 seconds...")
            await asyncio.sleep(60)  # Keep the session alive for 60 seconds
            print("Stopping the session...")
            await session.stop()  # Stop to gracefully close the session

        finally:
            print("Cancelling receive task...")
            receive_task.cancel()
            try:
                await receive_task  # Await the task to handle any cancellation errors
            except asyncio.CancelledError:
                print("Receive task cancelled successfully.")
            print("Exiting main function.")

if __name__ == "__main__":
    asyncio.run(main())