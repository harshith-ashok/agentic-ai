from fastapi import APIRouter, HTTPException, status
from ollama import Client
router = APIRouter()

# Initialize the Ollama client (don't pass `model` here; the client methods accept `model`)
client = Client()


@router.post("/generate-text/")
def generate_text(prompt: str):
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt is required")

    try:
        # Generate text using the Ollama client (pass model here)
        response = client.generate(model="llama3.2", prompt=prompt)
        return {"generated_text": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
