from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client()

prompt = "A futuristic cityscape at sunset with flying cars and neon lights"

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# Extract the generated image
for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")
        image.show()