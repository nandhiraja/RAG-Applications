# it_Agent.py

import vectorDataBase
import Emedding
import Model

from typing import List
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage

vector_database = vectorDataBase.vectorDataBase("My_Storage", "It_documents")
embedd = Emedding.Embedding()

def process_data(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    if not data:
        return
    chunks: List[str] = embedd.getChunks(data)
    embeddings_vectors: List[List[float]] = []
    try:
        for idx, chunk in enumerate(chunks):
            print("Embedding...", idx)
            embeddings_vectors.append(embedd.getEmbeddings(chunk))
    except Exception as e:
        print("Embedding issues:", e)
    vector_database.storeData(embeddings_vectors, chunks)
    print("DONE PROCESS....!!!")

def get_related_data(query: str):
    q_emb = embedd.getEmbeddings(query)
    return vector_database.Query(q_emb)

def _safe_to_text(x) -> str:
    # Normalize model outputs to a string
    if x is None:
        return "No answer could be generated at this time."
    if isinstance(x, str):
        return x.strip() or "No answer could be generated at this time."
    # If your model returns dict with 'content', use it
    if isinstance(x, dict) and "content" in x:
        c = x.get("content")
        return c.strip() if isinstance(c, str) and c.strip() else "No answer could be generated at this time."
    # Fallback to string conversion
    return str(x)

def response_it(state: MessagesState):
    if not state["messages"]:
        return {"messages": []}
    user_query = state["messages"][-1].content or ""
    if not user_query.strip():
        return {"messages": []}

    related_data = get_related_data(user_query)

    print("Generate..... IT")
    try:
        raw_answer = Model.getRespose(user_query, related_data)
    except Exception as e:
        raw_answer = f"Encountered an error while generating the IT answer: {e}"
    answer = _safe_to_text(raw_answer)

    return {"messages": [AIMessage(
        content=answer,
        response_metadata={"agent": "it"},
        name="it_agent"
    )]}
