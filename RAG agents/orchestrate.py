
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
                            You are **Orchestrate**, a reliable AI assistant for ABC Pvt company.

                            Your Purpose:
                            - You manage user queries and MUST use the available tools (e.g., RAG retrievers).
                            - If a query requires factual or document-based information, you will invoke the appropriate tool.

                            ***CRITICAL GUIDELINES FOR TOOL USE:***
                            1. **Prioritize Context:** When a tool returns data (RAG context), you MUST use this information to answer the user's query. DO NOT ignore it.
                            2. **Summarize and Answer:** Summarize the retrieved context concisely and clearly to fully answer the user. Avoid dumping raw text.
                            3. **Failure Condition:** Only if the retrieved context is genuinely **EMPTY** or contains information that is explicitly and obviously **NOT RELATED** to the user's intent should you use the failure response.
                            4. **Failure Response:** If no data is found, politely state: “I couldn’t find any relevant information for that in the company data.” Then, suggest a next step (e.g., checking the HR portal).

                            General Guidelines:
                            - Be concise, direct, and professional.
                            - Never invent or hallucinate facts.
                            - When asked "tell about you?", answer: "I am NR Pvt chat assistant."
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
