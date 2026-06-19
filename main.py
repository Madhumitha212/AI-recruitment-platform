from fastapi import FastAPI

from api.routes import router
app = FastAPI(
    title="AI Recruitment Intelligence Platform"
)

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "AI Recruitment Intelligence Platform Running"
    }