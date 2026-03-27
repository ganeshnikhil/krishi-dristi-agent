import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_ollama import ChatOllama
from app.tools.yield_tool import YieldPredictionInternalTool
from app.tools.crop_tool import CropRecommendationInternalTool
from app.tools.fertilizer_tool import FertilizerPredictionTool
from app.tools.rain_fall import RainfallPredictionTool
from app.tools.weather_tool import WeatherInfoTool
from app.tools.soil_tool import SoilInfoTool
from app.tools.general_info_tool import ExternalKnowledgeSearchTool
from app.tools.farm_advice_tool import FarmPracticeRAGTool
from app.tools.goverment_schema_tool import GovSchemeRAGTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import SystemMessage, HumanMessage


load_dotenv()


TOOLS = [
    YieldPredictionInternalTool(),
    CropRecommendationInternalTool(),
    FertilizerPredictionTool(),
    RainfallPredictionTool(),
    WeatherInfoTool(),
    SoilInfoTool(),
    ExternalKnowledgeSearchTool(),
    FarmPracticeRAGTool(),
    GovSchemeRAGTool()
]



# -----------------------------
# SARVAM LLM SETUP
# -----------------------------
### for online commnication 
def get_sarvam_llm(model_name: str = "sarvam-30b") -> ChatOpenAI:
    api_key = os.getenv("SARVAM_MODEL_API")
    if not api_key:
        raise ValueError("SARVAM_MODEL_API environment variable not set.")
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.sarvam.ai/v1",
        model=model_name,
        temperature=0.0
    )


def get_gemini_llm(model_name: str = "gemini-1.5-pro"):
    return ChatGoogleGenerativeAI(model=model_name, temperature=0.0)



## for offline communication
def get_ollama_llm(model_name: str = "llama3"):
    return ChatOllama(
        model=model_name,
        temperature=0.1,
        streaming=True
    )


# -----------------------------
# SYSTEM PROMPT
# -----------------------------

def get_agent_system_prompt(expertise_level: str = "beginner") -> str:
    return (
        "You are an expert Indian Agriculture Advisor.\n\n"
        "GUIDELINES:\n"
        "- Use tools whenever they are relevant.\n"
        "- Prefer tools for accurate and real-time information.\n"
        "- If no tool is suitable, answer using your knowledge.\n"
        "- Do NOT make up tool outputs.\n"
        "- Keep answers simple and farmer-friendly.\n"
        "- Reply in the same language as the user.\n"
    )


def get_chat_system_prompt(expertise_level: str = "beginner") -> str:
    return (
        "You are 'Krishi Sahayak', a dedicated Indian Agriculture Advisor. "
        "Your goal is to support Indian farmers with empathy, respect, and local wisdom.\n\n"
        
        "CONTEXT & GUIDELINES:\n"
        "1. LANGUAGE: Always respond in the EXACT same language or dialect the farmer uses (Hindi, Marathi, Tamil, etc.). "
        "Use simple, conversational words, not technical jargon.\n"
        
        "2. CULTURAL TONE: Use respectful Indian greetings (like 'Namaste', 'Ram Ram', or 'Vanakkam') where appropriate. "
        "Be encouraging—farming is hard work, and you are their digital partner.\n"
        
        "3. KNOWLEDGE SCOPE: You are an expert in Indian crop cycles (Kharif, Rabi, Zaid). "
        "If a farmer asks a general question, provide advice relevant to Indian geography and climate.\n"
        
        "4. BREVITY: Keep responses short and punchy. Farmers often read this on mobile screens in the field."
    )


# -----------------------------
# AGENT CREATION
# -----------------------------
def create_farmer_agent(llm: ChatOpenAI, checkpointer: SqliteSaver):
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=get_agent_system_prompt("beginner"),
        checkpointer=checkpointer,
        debug=True
    )


def call_chat_only(llm, user_query: str, config: dict, checkpointer):
    """
    Handles simple conversation using checkpointer-safe flow.
    """

    state = checkpointer.get(config)
    history = state.values.get("messages", []) if state else []

    messages = [SystemMessage(content=get_chat_system_prompt())]
    messages.extend(history)
    messages.append(HumanMessage(content=user_query))

    response = llm.invoke(messages)


    return response.content


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    DB_PATH = "farmer_data.db"

    # SqliteSaver is a context manager — must use 'with' block.
    # This creates farmer_data.db in the current directory and sets
    # up the required checkpoint tables automatically.
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        llm = get_sarvam_llm()
        agent = create_farmer_agent(llm, checkpointer)

        print("🌾 Sarvam Farmer AI Ready! (SQLite persistence enabled)")
        print(f"📦 Database: {DB_PATH}")
        print("Tip: Use different User IDs (e.g., user1, user2) to test conversation isolation.\n")

        while True:
            current_user = input("Enter User ID (e.g., user1): ").strip()
            if not current_user:
                print("User ID cannot be empty.")
                continue

            user_query = input(f"[{current_user}] You: ").strip()
            if user_query.lower() in ["exit", "quit"]:
                print("Goodbye! 🌱")
                break

            try:
                # thread_id isolates each user's conversation history in the DB
                config = {"configurable": {"thread_id": current_user}}
                response = agent.invoke(
                    {"messages": [HumanMessage(content=user_query)]},
                    config=config
                )
                last_message = response["messages"][-1]
                print(f"Agent: {last_message.content}\n")

            except Exception as e:
                print(f"❌ Error: {e}\n")


