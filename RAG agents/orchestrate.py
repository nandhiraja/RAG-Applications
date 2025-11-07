
import os
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_groq import ChatGroq
from langchain_core.prompts  import ChatPromptTemplate
import custom_Agent
from dotenv import load_dotenv
from langchain.tools  import tool
load_dotenv()


API_KEY = os.getenv("GROQ_API_KEY")

# ================================------------Model Initialize-------------------=================================================


MODEL =  ChatGroq(api_key=API_KEY,
                  model="llama-3.3-70b-versatile")


# ================================------------Tools Initialize-------------------=================================================

@tool
def finance_assitent(query : str):
    """
            Finance Context Provider Tool

            Purpose:
                Retrieves and summarizes finance-related data or insights from the company's financial knowledge sources.
            When to Use:
                - When the user's query involves topics such as:
                    * revenue, profit, or loss analysis
                    * financial reports or quarterly performance
                    * investments, budgets, or forecasts
                    * expenses, income, or cost trends
                    * company valuation or growth metrics
                - When numeric or factual financial data is needed to support the response.
           
    """

    return custom_Agent.get_finance_datas(query)


@tool
def information_technology_assitent(query : str):
    """
     IT Context Provider Tool

     Purpose:
         Retrieves, explains, or summarizes information related to technology, infrastructure, or software systems within the company.
     When to Use:
         - When the query involves topics like:
             * software systems, applications, or platforms
             * IT policies, architecture, or infrastructure
             * technology stack details (frontend, backend, databases)
             * development tools, programming frameworks, or API usage
             * troubleshooting technical issues or updates        
     """

    return custom_Agent.get_IT_datas(query)


# ================================------------Agent  Initialize-------------------=================================================
MODEL_PROMPT = ChatPromptTemplate.from_messages([
                        ("system", """
                                 You are **Orchestrate**, a reliable AI assistant that manages user queries for the company.

                                 Your purpose:
                                 - Understand the user's input carefully.
                                 - Decide intelligently whether to use available tools (e.g., RAG retrievers, knowledge APIs, data services).
                                 - If the query requires factual or document-based information, invoke the appropriate RAG tool to retrieve it.
                                 - If sufficient information is retrieved, summarize and answer clearly using that data.
                                 - If the retrieved data is empty, unrelated, or unclear — **do NOT guess or hallucinate**.
                                   Politely explain that no relevant information was found.

                                 Guidelines:
                                 1. Be concise, direct, and helpful — respond in a natural, conversational tone.
                                 2. Never invent facts. Only use retrieved or given context.
                                 3. When RAG data is retrieved:
                                      - Use it as factual evidence.
                                      - Summarize or explain it clearly.
                                      - Avoid dumping raw data.
                                 4. When RAG returns nothing:
                                      - Say something like: 
                                        “I couldn’t find any relevant information for that in the current data.”
                                      - Then, if possible, suggest what the user could try next.
                                 5. Maintain professionalism — you are the company's reliable assistant, not a chatbot.
                                 6. Always ensure your final output is understandable to a normal user (avoid internal reasoning traces).
                          """),
                        ("human", "{input}"),
                        ("placeholder", "{agent_scratchpad}")
                 ])


model_with_tool = create_tool_calling_agent(
        llm =MODEL,
        tools=[information_technology_assitent,finance_assitent],
        prompt=MODEL_PROMPT
    )

agent_executor = AgentExecutor(agent=model_with_tool,
                                tools=[information_technology_assitent,finance_assitent],
                                max_iterations=4,
                                early_stopping_method="generate",
                                verbose=True)

def main(agent_executor):
    
    chatHistory=[]

    while True:
        user_input = input("Ask your Query : ")
        response = agent_executor.invoke({
            "input":user_input,
            "chat_history" :chatHistory
        })
        chatHistory.append(response)
        print("Query" ,response["input"], "\n\noutput ", response["output"])



# main(agent_executor)
