
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY");


client = Groq(
    api_key=API_KEY,
)

def getRespose(Query):
    print("\n\nModel called  chat".center(30,'-'))

    chat_completion = client.chat.completions.create(
        messages=[
            {   "role" : "system",
                "content": """You are a query refinement assistant. Your sole task is to rephrase the user's input into a clear, concise, and specific instruction. This refined instruction will be fed to an orchestration model that selects the correct tool (e.g., finance, IT).

                    Do not answer the query. Only output the refined instruction."""
            },
            {
                "role": "user",
                "content": f"user_Query :{Query} "
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    
    
    print("Model direct groq :\n\n",chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content