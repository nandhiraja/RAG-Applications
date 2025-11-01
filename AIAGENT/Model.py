
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY");


client = Groq(
    api_key=API_KEY,
)

def getRespose(Query,context):


    chat_completion = client.chat.completions.create(
        messages=[
            {   "role" : "system",
                "content": "you are the agent u need to act like that. there will be provide the context and query"
            },
            {
                "role": "user",
                "content": f"user_Query :{Query} , context : {context}"
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    
    
    print(chat_completion.choices[0].message.content)