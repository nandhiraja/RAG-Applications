import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os





vectorDB = chromadb.PersistentClient(path="./chroma_db")



# with open("./Finance_sector_Kb.txt", "r") as file:
#     data = file.read()
print("✅ Get Data...")

chunks = []
thresh_hold = 500
text = ""





# print("🔹 Getting chunks...")
# for i, ch in enumerate(data):
#     text += ch
#     if len(text) >= thresh_hold:
#         chunks.append(text)
#         text = ""
# if text:
#     chunks.append(text)

# print(f"✅ Total chunks created: {len(chunks)}")







# print("🧠 Embedding...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# embedded = embedding_model.encode(chunks).tolist()
# print(f"✅ Embedded {len(embedded)} vectors")


collection = vectorDB.get_or_create_collection("My_RAG_Datas")

doc_ids = [str(i) for i in range(len(chunks))]  # safer way

# collection.add(
#     ids=doc_ids,
#     documents=chunks,
#     embeddings=embedded,
#     metadatas=[{"source": "Finance"} for _ in chunks]
# )

print("💾 ChromaDB persisted successfully!")




result = collection.query(
    query_embeddings=embedding_model.encode(["I need to know the travel guidelines"]).tolist(),
    n_results=2
)

print(result["documents"])
    # print(i ,end="\n\n")