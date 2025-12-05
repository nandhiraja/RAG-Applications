
# RAG Agent Chat Application

---


This is a full-stack Retrieval-Augmented Generation (RAG) application that uses a multi-agent system to answer questions from a knowledge base. It features a React frontend and a FastAPI backend.

##  Core Features

*   **Multi-Agent System**:  
     > An orchestrator agent delegates queries to specialized **Finance** and **IT** agents.
*   **Dynamic Knowledge Base**: 
     > Upload documents via a drag-and-drop UI to build and manage knowledge collections.
*   **Vector Search**: 
    >Uses `ChromaDB` for persistent vector storage and `sentence-transformers` for efficient retrieval.
*   **Modern UI/UX**: 
    >A clean, responsive frontend built with `React` for both chat and admin functions.

##  Tech Stack

*   **Backend**: `FastAPI`, `LangChain`, `Groq`
*   **Frontend**: `React`
*   **Database**: `ChromaDB`
*   **Embedding**: `all-MiniLM-L6-v2`

##  How It Works

1.  **Admin Uploads File**: 
    An admin adds a document to a specific collection (e.g., "IT\_datas").
2.  **User Asks Question**: 
    A user sends a query through the chat interface.
3.  **Agent Orchestration**: 
    The main agent determines the query's topic (e.g., IT) and routes it to the correct specialized agent.
4.  **Context Retrieval**: 
    The specialized agent queries ChromaDB to find relevant document chunks.
5.  **Response Generation**: 
    The retrieved context is passed to the Groq LLM, which generates a final, accurate answer.

##  Getting Started

### Prerequisites

*   **Python 3.10+ & Node.js 18+**
*   **A Groq API Key**

### Backend

```bash
# 1. Navigate to the backend folder
cd backend/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file with your API key
echo "GROQ_API_KEY=your_groq_api_key" > .env

# 4. Run the server
uvicorn main:app --reload --port 8000
```



### Frontend

```bash
# 1. Navigate to the frontend folder
cd frontend/

# 2. Install dependencies
npm install

# 3. Run the development server
npm run dev
```
## Images 

<img width="1689" height="1003" alt="Image" src="https://github.com/user-attachments/assets/a8f0c149-6edf-4b0a-996d-fb3fe68f24f7" />

<img width="1724" height="1007" alt="Image" src="https://github.com/user-attachments/assets/fd275c0c-945d-4180-8f01-17f6a1fbdbf8" />

<img width="1724" height="1007" alt="Image" src="https://github.com/user-attachments/assets/da1c48f0-8957-4d73-ad99-16f8c8d7489e" />

<img width="1724" height="1007" alt="Image" src="https://github.com/user-attachments/assets/c865e4e9-6ef8-4b1b-b102-3834f1a3ea4f" />


## API Endpoints

| Method | Endpoint                    | Description                                  |
| :----- | :-------------------------- | :------------------------------------------- |
| `POST` | `/api/upload`               | Upload a document to a collection.           |
| `POST` | `/api/chat`                 | Send a message to the chat agent.            |
| `GET`  | `/api/collections`          | List all available collections.              |
| `DELETE`|`/api/files/{collection_name}`| Delete a collection from the database.       |

## Troubleshooting

*   **Collection Not Found**: Ensure you have uploaded a document to the collection (e.g., `IT_datas`) before querying it.
*   **`Failed to call a function`**: The LLM is confused. Make the tool descriptions in `orchestrate.py` more specific and distinct.
*   **CORS Errors**: Add your frontend URL (e.g., `http://localhost:5173`) to the `allow_origins` list in `main.py`.