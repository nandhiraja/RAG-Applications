import vectorDataBase
import  Emedding 
import Model
vector_database =  vectorDataBase.vectorDataBase("My_Storage","Finance_documents")
embedd = Emedding.Embedding()

def processData(Url):

    with open (Url,'r',encoding="utf-8") as file:
         data = file.read()
    
    if(data):
        chunks =embedd.getChunks(data)

        embeddings_vectors =[]
        try :
            for index, chunk in enumerate (chunks):
                print("Embedding...",index)
                embeddings_vectors.append(embedd.getEmbeddings(chunk))                
        except e:
            print("Something Issues..")
        vector_database.storeData(embeddings_vectors,chunks)
        print("DONE PROCESS....!!!")



def getRelatedData(Query):
    embedding = embedd.getEmbeddings(Query)
    results = vector_database.Query(embedding)
    return results



processData("/home/nandhiraja/Nandhiraja C/Agentic AI Application/KnowledgeBase/Finance_sector.txt")


while(True):
    userInput = input("Enter the Question Finance related ? ")
    if(userInput.lower()=="no"):
        break
    related_data = getRelatedData(userInput)
    
    # print(related_data)
    print("Generating ....")
    response = Model.getRespose(userInput, related_data)
    
    print("-- Model Ans : \n", response)