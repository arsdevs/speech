import pyttsx3
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import tempfile

app = FastAPI()

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

@app.get("/")
def root():
    return {"message": "Text-to-Speech Server running with pyttsx3!"}

@app.get("/voices")
def list_voices():
    voices = engine.getProperty('voices')
    voice_list = [{"id": voice.id, "name": voice.name, "lang": voice.languages} for voice in voices]
    return {"voices": voice_list}

@app.post("/tts")
async def tts_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")
    voice_id = data.get("voice_id", None)

    if not text:
        return JSONResponse(status_code=400, content={"error": "Text is required"})

    # Set the desired voice if provided
    if voice_id:
        voices = engine.getProperty('voices')
        selected_voice = next((voice for voice in voices if voice.id == voice_id), None)
        if selected_voice:
            engine.setProperty('voice', selected_voice.id)
        else:
            return JSONResponse(status_code=400, content={"error": f"Voice with id {voice_id} not found"})

    # Use a temporary file to store the output (cloud-friendly)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_filename = tmp_file.name
        engine.save_to_file(text, tmp_filename)
        engine.runAndWait()  # Ensure the file is saved

        # Return the generated audio file
        return FileResponse(tmp_filename, media_type="audio/mp3", filename=os.path.basename(tmp_filename))

