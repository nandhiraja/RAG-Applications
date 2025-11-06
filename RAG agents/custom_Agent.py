import vectorDataBase
import Emedding
from typing import List


embedd = Emedding.Embedding()
vector_database = vectorDataBase.vectorDataBase("My_Storage")

FINIANCE_COLLECTION = "Finance_datas"
IT_COLLECTION = "IT_datas"




def process_data(path: str ,collection_name) -> None:

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

    vector_database.storeData(embeddings_vectors, chunks,collection_name=collection_name)
    print(f"{collection_name} DONE PROCESS....!!!")







def get_related_data(query: str ,collection_name):
    q_emb = embedd.getEmbeddings(query)
    return vector_database.Query(q_emb,collection_name=collection_name)







def get_finance_datas(query : str):
    print(FINIANCE_COLLECTION)

    if not query:
        return "There is no query is provide"
        
    context = get_related_data(query,collection_name=FINIANCE_COLLECTION)
   
    print("\n user_query : ",query,"\n\nfinance context : ",context)

    return context


def get_IT_datas(query : str):
    print(IT_COLLECTION)
    if not query:
        return "There is no query is provide"
        
    context = get_related_data(query,collection_name=IT_COLLECTION)
   
    print("\nuser_query : ",query,"\n\nIT context : ",context)

    return context
    



if __name__ == "__main__":


    process_data("KnowledgeBase/Finance_sector_Kb.txt",FINIANCE_COLLECTION)
    process_data("KnowledgeBase/IT_Sector_Kb.txt",IT_COLLECTION)


