import chromadb

class vectorDataBase:

    def __init__(self,path_to_store,collection_name):
        self.client = chromadb.PersistentClient(path_to_store)
        self.collection = self.client.get_or_create_collection(collection_name)




    def storeData(self,vector_embeddings,documents,indexs=None,meta_data=None):
        if(indexs==None):
            indexs = [str(i) for i in range(0,len(vector_embeddings))]

        print(len(indexs))
        # print(vector_embeddings,documents)

        self.collection.add(
            embeddings=vector_embeddings,
            ids=indexs,
            documents=documents
        )
        print("Successfully add to Collection ")




    def Query(self,Query_vectors,n_result=3):
        return self.collection.query(query_embeddings=Query_vectors,n_results=n_result)