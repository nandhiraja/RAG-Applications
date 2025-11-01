# finance_agent.py

import vectorDataBase
import Emedding
import Model

from typing import List, Union, Dict, Any
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage

vector_database = vectorDataBase.vectorDataBase("My_Storage", "Finance_documents")
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

def _safe_to_text(x: Any) -> str:
    if x is None:
        return "No finance answer could be generated at this time."
    if isinstance(x, str):
        s = x.strip()
        return s if s else "No finance answer could be generated at this time."
    if isinstance(x, dict) and "content" in x:
        c = x.get("content")
        if isinstance(c, str) and c.strip():
            return c.strip()
    return str(x)

def response_finance(state: MessagesState):
    if not state["messages"]:
        return {"messages": []}
    user_query = state["messages"][-1].content or ""
    if not user_query.strip():
        return {"messages": []}

    related_data = get_related_data(user_query)

    print("Generating..... Finance")
    try:
        raw_answer = Model.getRespose(user_query, related_data)
    except Exception as e:
        raw_answer = f"Encountered an error while generating the Finance answer: {e}"
    answer = _safe_to_text(raw_answer)

    return {"messages": [AIMessage(
        content=answer,
        response_metadata={"agent": "finance"},
        name="finance_agent"
    )]}

if __name__ == "__main__":
    # Build the index once at startup
    process_data("KnowledgeBase/Finance_sector_Kb.txt")
    print("Finance index built.")
