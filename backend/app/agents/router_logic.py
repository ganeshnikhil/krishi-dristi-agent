import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama


def get_routing_decision(user_input: str) -> str:
    """
    Categorizes input into 'TOOL' or 'CHAT' using Sarvam 30B.
    """
    # 1. Initialize Sarvam as the Router
    # Using the smaller 30B model ensures this decision is fast (low latency)
    api_key = os.getenv("SARVAM_MODEL_API")
    model_name = os.getenv("SARVAM30_MODEL_NAME") # Ensure this is set to the 30B model
    
    router_llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.sarvam.ai/v1",
        model=model_name,
        temperature=0.0
    )

    # 2. Strict Router Prompt
    # 2. Multilingual-Aware Router Prompt
    router_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert multilingual routing assistant for an Indian agricultural app.\n"
            "Analyze the user's input, which may be in English, Hindi, Marathi, Tamil, Telugu, or any Indian regional language.\n\n"
            
            "Classify the input into exactly one of two categories:\n"
            "1. 'TOOL': If the user is asking about technical farming data (crops, soil, weather, fertilizer, rainfall) in ANY language.\n"
            "2. 'CHAT': If the user is giving a greeting (like 'Namaste', 'Ram Ram', 'Vanakkam'), saying 'Thank you', or just making small talk.\n\n"
            
            "Output ONLY the word 'TOOL' or 'CHAT'. Do not explain your choice."
        )),
        ("human", "{input}"),
    ])


    # 3. Execution Chain
    decision_chain = router_prompt | router_llm | StrOutputParser()
    
    try:
        decision = decision_chain.invoke({"input": user_input})
        return decision.strip().upper()
    except Exception as e:
        # Fallback to CHAT if the router fails to ensure the user gets a response
        print(f"Router Error: {e}")
        return "CHAT"
    



def get_routing_decision_x(user_input: str) -> str:
    """
    Categorizes input into 'TOOL' or 'CHAT' using Sarvam 30B.
    """

    
    model_name = "lfm2.5-thinking:latest "
    router_llm = ChatOllama(
        model=model_name,
        temperature=0.1,
        streaming=True
    )
    
    


    # 2. Strict Router Prompt
    # 2. Multilingual-Aware Router Prompt
    router_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert multilingual routing assistant for an Indian agricultural app.\n"
            "Analyze the user's input, which may be in English, Hindi, Marathi, Tamil, Telugu, or any Indian regional language.\n\n"
            
            "Classify the input into exactly one of two categories:\n"
            "1. 'TOOL': If the user is asking about technical farming data (crops, soil, weather, fertilizer, rainfall) in ANY language.\n"
            "2. 'CHAT': If the user is giving a greeting (like 'Namaste', 'Ram Ram', 'Vanakkam'), saying 'Thank you', or just making small talk.\n\n"
            
            "Output ONLY the word 'TOOL' or 'CHAT'. Do not explain your choice."
        )),
        ("human", "{input}"),
    ])


    # 3. Execution Chain
    decision_chain = router_prompt | router_llm | StrOutputParser()
    
    try:
        decision = decision_chain.invoke({"input": user_input})
        return decision.strip().upper()
    except Exception as e:
        # Fallback to CHAT if the router fails to ensure the user gets a response
        print(f"Router Error: {e}")
        return "CHAT"
