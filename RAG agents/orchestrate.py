
import os
from typing import List
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage



def finance_retrieve(query: str) -> str:
    """
    Retrieve finance-relevant passages for the query from your Finance KB and return a concise text summary.
    """
   
    return "Finance tool placeholder: connect to your Finance KB retrieval and return top passages."

def it_retrieve(query: str) -> str:
    """
    Retrieve IT-relevant passages for the query from your IT KB and return a concise text summary.
    """
    return "IT tool placeholder: connect to your IT KB retrieval and return top passages."







llm = ChatGroq(
    api_key="",
    model="llama-3.3-70b-versatile",   
    temperature=0.2,
)

llm_with_tools = llm.bind_tools([finance_retrieve, it_retrieve])







def call_model(state: MessagesState):
    messages = state["messages"]
    sys = SystemMessage(
        content=(
            "You are a helpful assistant for IT and Finance questions. "
            "Always respond in English. "
            "If a tool is helpful, call the most relevant tool with clear arguments."
        )
    )
    response = llm_with_tools.invoke([sys] + messages)
    return {"messages": [response]}





tool_node = ToolNode([finance_retrieve, it_retrieve])





def should_continue(state: MessagesState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return END







builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("tools", tool_node)

builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", should_continue, ["tools", END])
builder.add_edge("tools", "call_model")

graph = builder.compile()














if __name__ == "__main__":
    print("Tool-calling orchestrator ready. Type 'no' to exit.")
    while True:
        query = input("\nEnter Question (or type 'no' to exit): ").strip()
        if query.lower() == "no":
            break
        result = graph.invoke({"messages": [HumanMessage(content=query)]})

        # Print the final assistant message
        ai_msgs = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_msgs:
            final = ai_msgs[-1]
            # Optional: infer which tool was used by inspecting earlier AIMessage.tool_calls
            used = None
            for m in result["messages"]:
                if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
                    calls = m.tool_calls or []
                    if calls:
                        used = calls[0].get("name")
            if used:
                print(f"\nAgent (via tool): {used}")
            else:
                print("\nAgent: fallback_llm")
            print("Assistant:", final.content)
        else:
            print("\nAssistant: (no response)")
