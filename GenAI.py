from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import openai
import re
import os
import urllib.request
from gtts import gTTS
from moviepy.editor import *
import cloudinary
import cloudinary.uploader

from api_key import API_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your OpenAI API key
openai.api_key = API_KEY

# Configure Cloudinary
cloudinary.config(
  cloud_name=CLOUDINARY_CLOUD_NAME,
  api_key=CLOUDINARY_API_KEY,
  api_secret=CLOUDINARY_API_SECRET
)

# Create necessary folders if they don't exist
os.makedirs("audio", exist_ok=True)
os.makedirs("images", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Ensure ImageMagick is configured properly for MoviePy
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})  # Adjust path as needed

# Function to generate text from a prompt
def generate_text(prompt):
    print("The AI BOT is trying now to generate a new text for you...")
    
    # Generate text using the GPT-3.5-turbo model in streaming mode
    stream = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    # Initialize an empty string to collect the generated text
    generated_text = ""

    # Process the stream and build the output text
    for chunk in stream:
        if chunk.choices[0].delta.get("content"):
            generated_text += chunk.choices[0].delta["content"]

    # Save the generated text to a file
    with open("generated_text.txt", "w") as file:
        file.write(generated_text.strip())

    print("\nThe Text Has Been Generated Successfully!")

# Function to generate video from text
def generate_video():
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
            final_video_path = "final_video.mp4"
            final_video.write_videofile(final_video_path, fps=24)
            print("The final video has been created successfully!")
            return final_video_path
        else:
            print("No video clips found to concatenate.")
            return None

    except Exception as e:
        print(f"An error occurred while creating the final video: {e}")
        return None

# Function to upload video to Cloudinary
def upload_video_to_cloudinary(video_path):
    try:
        print("Uploading video to Cloudinary...")
        response = cloudinary.uploader.upload(video_path, resource_type="video")
        video_url = response['secure_url']
        print(f"Video URL: {video_url}")
        return video_url
    except Exception as e:
        print(f"An error occurred while uploading the video: {e}")
        return None

# Main function to generate video and upload
def main(topic):
    generate_text(topic)
    video_path = generate_video()
    if video_path:
        video_url = upload_video_to_cloudinary(video_path)
        return video_url
    return None

@app.route('/generate_video', methods=['POST'])
def generate_video_route():
    data = request.json
    topic = data.get('topic')
    if topic:
        video_url = main(topic)
        if video_url:
            return jsonify({"video_url": video_url}), 200
        else:
            return jsonify({"error": "Failed to create or upload the video."}), 500
    return jsonify({"error": "No topic provided."}), 400

if __name__ == "__main__":
    app.run(debug=True)
