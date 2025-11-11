from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import requests, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIX 1: This route will now serve your index.html file
@app.get("/", response_class=HTMLResponse)
def get_home():
    try:
        # Assumes index.html is in the same directory as main.py
        return FileResponse("index.html")
    except FileNotFoundError:
        return JSONResponse({"error": "index.html not found"}, status_code=500)

# FIX 2: The path is changed to '/api/remove-bg' to match your JavaScript
@app.post("/api/remove-bg")
async def remove_bg(
    file: UploadFile = File(None),
    image_url: str = Form(None)
):
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

        # Use a writeable directory in Railway's container
        output_path = "/tmp/output.png"
        with open(output_path, "wb") as f:
            f.write(result)

        return FileResponse(output_path, media_type="image/png", filename="output.png")

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
