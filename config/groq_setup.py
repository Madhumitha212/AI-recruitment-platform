import os
from dotenv import load_dotenv

from openai import  AsyncOpenAI 
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found")

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

provider = OpenAIProvider(openai_client=client)

MODEL = OpenAIChatModel(
    "llama-3.3-70b-versatile",
    provider=provider
)