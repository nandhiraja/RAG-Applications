from sentence_transformers import  SentenceTransformer


class Embedding:

    def __init__(self,Model_name="all-MiniLM-L6-v2"):
        print("Model fetching .....")
        self.Embedd_Model = SentenceTransformer(Model_name)
        print("Model fetching Done.....")



    def getChunks(self ,datas,chunk_size=500,over_lap = 30 ,Chunk_method = None):
        if(datas):
            print("chuking data....")
            chunks=[]
            text =""

            # if(Chunk_method is not None):
            for i in datas:
                text+=i
                if(len(text)>=chunk_size):
                    chunks.append(text)
                    text=text[(len(text)-over_lap):]   # handle overlap
            # else:
                # chunks = datas.split(chunk_size)
            print("chunks done....\n\n\n")
            return chunks




    def getEmbeddings(self,datas):
        if(datas):
            print("Embeddings Begins \n\n", datas)
            Embedding_vectors = self.Embedd_Model.encode(datas)
            print("\n\nEmbeddings End \n\n")

            return Embedding_vectors
    