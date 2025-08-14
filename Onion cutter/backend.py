from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import re

from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from transformers import pipeline

app = FastAPI()

# Allow all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and preprocessors once when server starts
model_name = "nlpconnect/vit-gpt2-image-captioning"
model = VisionEncoderDecoderModel.from_pretrained(model_name)
feature_extractor = ViTImageProcessor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# ---- Instruction-following Text Generator ----
# Using FLAN-T5 for better prompt adherence
text_model_name = "google/flan-t5-xl"  # can switch to flan-t5-xl if GPU is strong enough
generator = pipeline("text2text-generation", model=text_model_name, device=0 if torch.cuda.is_available() else -1)


@app.post("/process")
async def process_image(
    image: UploadFile = File(...)
):
    try:
        # Read image bytes and open PIL Image
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Prepare inputs for model
        pixel_values = feature_extractor(images=img, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # Generate caption
        output_ids = model.generate(
            pixel_values,
            min_length = 50,
            max_length=140,
            num_beams=5,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        result_body = generator(
            f"Write a long, funny, and absurd fake news article based on the following caption: {caption}. Make it very weird, creative, satirical, and over 300 words.",
            min_length=200,
            max_new_tokens=550,
            temperature=0.9,
            top_p=0.95,
            repetition_penalty=1.2,   # Discourages repeating phrases
            no_repeat_ngram_size=3,   # Prevents repeated 3-word sequences
            do_sample=True            # Ensures varied output
        )[0]["generated_text"]

        result_title = generator(
            f"Write a short, catchy, and absurd fake news headline for this article: {result_body}",
            min_length=5,
            max_new_tokens=150,
            temperature=0.9,
            top_p=0.95,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            do_sample=True
        )[0]["generated_text"]

        return {
            "captionL": caption,
            "image_size": f"{img.width}x{img.height}",
            "result body": result_body,
            "result head": result_title
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
