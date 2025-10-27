

from it_Agent import response_it
from Finance_Agent import response_finance
from groq  import Groq



from langgraph.graph import StateGraph, MessagesState, START, END



client = Groq(
    api_key="",
)



def orhestrate_response(user_query):
    chat_completion = client.chat.completions.create(
        messages=[
            {   "role" : "system",
                "content": "you are the agent u need to act like that. there will be provide the context and query"
            },
            {
                "role": "user",
                "content": f"user_Query :{user_query} "
            }
        ],
        model="llama-3.3-70b-versatile",
    )


    print("Orchestrate model : " ,chat_completion.choices[0].message.content)

graph = StateGraph(MessagesState)
graph.add_node(orhestrate_response)
graph.add_edge(START, "orhestrate_response")

graph.add_node(response_it)
graph.add_edge(START, "response_it")

graph.add_node(response_finance)
graph.add_edge(START, "response_finance")

graph.add_edge("mock_llm", END)
graph = graph.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi! how are  you"}]})