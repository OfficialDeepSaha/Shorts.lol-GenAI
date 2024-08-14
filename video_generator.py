import openai
import re
import os
import urllib.request
from requests import get
from gtts import gTTS
from moviepy.editor import *

from api_key import API_KEY

# Set your OpenAI API key
openai.api_key = API_KEY

# Create necessary folders if they don't exist
os.makedirs("audio", exist_ok=True)
os.makedirs("images", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Ensure ImageMagick is configured properly for MoviePy
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})  # Adjust path as needed

# Read the text file
with open("generated_text.txt", "r") as file:
    text = file.read()

# Split the text by , and .
paragraphs = re.split(r"[,.]", text)

# Loop through each paragraph and generate an image, audio, and video for each
i = 1
for para in paragraphs[:-1]:
    try:
        # Generate image from the paragraph
        print("Generating AI image from paragraph...")
        response = openai.Image.create(
            model="dall-e-3",
            prompt=para.strip(),
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        image_path = f"images/image{i}.jpg"
        urllib.request.urlretrieve(image_url, image_path)
        print(f"Image {i} saved in the 'images' folder!")

        # Generate audio from the paragraph using gTTS
        print("Converting paragraph to voiceover...")
        tts = gTTS(text=para.strip(), lang='en', slow=False)
        audio_path = f"audio/voiceover{i}.mp3"
        tts.save(audio_path)
        print(f"Voiceover {i} saved in the 'audio' folder!")

        # Create a video using the image and voiceover
        print("Creating video from image and voiceover...")
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

        # Customize the text clip
        text_clip = TextClip(para.strip(), fontsize=50, color="white", bg_color="black")
        text_clip = text_clip.set_pos('center').set_duration(audio_clip.duration)

        # Concatenate the image, text, and audio into a final video clip
        video_clip = CompositeVideoClip([image_clip, text_clip])
        final_clip = video_clip.set_audio(audio_clip)
        final_video_path = f"videos/video{i}.mp4"
        final_clip.write_videofile(final_video_path, fps=24)
        print(f"Video {i} saved in the 'videos' folder!")

        i += 1

    except Exception as e:
        print(f"An error occurred while processing paragraph {i}: {e}")

# Concatenate all generated video clips into a single final video
try:
    print("Concatenating all video clips into a final video...")
    clips = [VideoFileClip(f"videos/{file}") for file in os.listdir("videos") if file.endswith('.mp4')]
    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile("final_video.mp4", fps=24)
        print("The final video has been created successfully!")
    else:
        print("No video clips found to concatenate.")

except Exception as e:
    print(f"An error occurred while creating the final video: {e}")
