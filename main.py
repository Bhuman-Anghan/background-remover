from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import requests, os

app = FastAPI()

# Allow all origins for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root route for Render health check
@app.get("/")
def home():
    return {"message": "✅ Background Remover API running!"}


@app.post("/remove-bg")
async def remove_bg(
    file: UploadFile = File(None),
    image_url: str = Form(None)
):
    try:
        # Get image input
        if file:
            input_bytes = await file.read()
        elif image_url:
            resp = requests.get(image_url)
            if resp.status_code != 200:
                return JSONResponse({"error": "❌ Failed to fetch image"}, status_code=400)
            input_bytes = resp.content
        else:
            return JSONResponse({"error": "No image provided"}, status_code=400)

        # Remove background
        result = remove(input_bytes)

        # Save output (Render allows /tmp for file writing)
        output_path = "/tmp/output.png"
        with open(output_path, "wb") as f:
            f.write(result)

        return FileResponse(output_path, media_type="image/png", filename="output.png")

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
