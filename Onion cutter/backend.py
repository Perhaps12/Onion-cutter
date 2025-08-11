from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch

from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

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


@app.post("/process")
async def process_image(
    image: UploadFile = File(...),
    note: str = Form("No note")
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
            num_beams=12,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return {
            "caption12": caption,
            "note": note,
            "image_size": f"{img.width}x{img.height}"
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
