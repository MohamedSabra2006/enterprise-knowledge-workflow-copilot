
from groq import Groq
from app.core.config import settings

client = Groq(
    api_key=settings.GROQ_API_KEY
)

response = client.chat.completions.create(
    model=settings.GROQ_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Explain RAG in 3 sentences."
        }
    ],
    temperature=0.2,
)

print(response.choices[0].message.content)
