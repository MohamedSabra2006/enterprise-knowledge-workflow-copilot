
from groq import Groq

from app.core.config import settings
from app.rag.prompt import SYSTEM_PROMPT
from app.rag.retrieval import RAGRetriever


class RAGService:

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )
    
        

        self.retriever = RAGRetriever()
    def close(self):
        self.retriever.close()
        
    def build_context(self, retrieved_chunks):
        context_parts = []

        for index, chunk in enumerate(
            retrieved_chunks, start=1
        ):
            context_parts.append(
                f"""
[Document {index}]
Source: {chunk["source_name"]}
Citation: {chunk["citation"]}

Content:
{chunk["text"]}
"""
            )

        return "\n\n".join(context_parts)

    def build_user_prompt(self, question, context):
        return f"""
Use the following authorized company documents
to answer the question.

AUTHORIZED CONTEXT:
{context}

USER QUESTION:
{question}

Remember:
- Answer only using the authorized context.
- Cite the sources used.
- If the context is insufficient, say so.
"""

    def answer_question(
        self,
        question: str,
        role: str,
        top_k: int = 5
    ):

        # 1. Retrieve authorized documents
        retrieved_chunks = self.retriever.search(
            query=question,
            role=role,
            top_k=top_k
        )

        # 2. Handle empty retrieval
        if not retrieved_chunks:
            return {
                "answer": (
                    "I couldn't find sufficient information "
                    "in the documents available to your account."
                ),
                "sources": [],
                "retrieved_chunks": []
            }

        # 3. Build context
        context = self.build_context(
            retrieved_chunks
        )

        # 4. Build user prompt
        user_prompt = self.build_user_prompt(
            question=question,
            context=context
        )

        # 5. Generate answer using Groq
        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content

        # 6. Collect citations
        sources = list(
            dict.fromkeys(
                chunk["citation"]
                for chunk in retrieved_chunks
            )
        )

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks
        }
