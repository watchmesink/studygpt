import openai
from typing import List
from config.config import Config

class QueryEngine:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
    
    def generate_response(self, query: str, context_chunks: List[str]) -> str:
        """Generate a response using GPT-4 with context."""
        # Combine context chunks
        context = "\n\n".join(context_chunks)
        
        # Create the system and user messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the provided context. "
                          "Always format your responses in Markdown. "
                          "If you cannot answer the question based on the context, say so and use general knowledge to answer the question. "
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\n"
                          "Please answer the question based on the context provided."
            }
        ]
        
        # Get response from GPT-4
        response = openai.chat.completions.create(
            model=Config.GPT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content 