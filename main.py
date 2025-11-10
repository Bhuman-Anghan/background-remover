from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rembg import remove
import requests, os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve the frontend (index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serve the index.html page"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(None), image_url: str = Form(None)):
    """Remove background from uploaded file or image URL"""
    try:
        if file:
            input_bytes = await file.read()
        elif image_url:
            resp = requests.get(image_url)
            if resp.status_code != 200:
                return JSONResponse({"error": "❌ Failed to fetch image"}, status_code=400)
            input_bytes = resp.content
        else:
            return JSONResponse({"error": "No image provided"}, status_code=400)

        result = remove(input_bytes)
        output_path = "/tmp/output.png"
        with open(output_path, "wb") as f:
            f.write(result)

        return FileResponse(output_path, media_type="image/png", filename="output.png")

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # ✅ Render sets $PORT automatically
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
