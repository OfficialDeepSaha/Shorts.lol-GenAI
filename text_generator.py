import openai
import re
from api_key import API_KEY

# Set your API key
openai.api_key = API_KEY

# Set the model to use
model_engine = "gpt-3.5-turbo"

# Set the prompt to generate text for
text = input("What topic you want to write about: ")
prompt = text

print("The AI BOT is trying now to generate a new text for you...")

# Generate text using the GPT-3.5-turbo model in streaming mode
stream = openai.ChatCompletion.create(
    model=model_engine,
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

# Initialize an empty string to collect the generated text
generated_text = ""

# Process the stream and build the output text
for chunk in stream:
    if chunk.choices[0].delta.get("content"):
        generated_text += chunk.choices[0].delta["content"]
        print(chunk.choices[0].delta["content"], end="")

# Save the generated text to a file
with open("generated_text.txt", "w") as file:
    file.write(generated_text.strip())

print("\nThe Text Has Been Generated Successfully!")
