import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_ollama import ChatOllama
from app.tools.crop_tool import get_crop_prediction
from app.tools.fertilizer_tool import get_fertilizer_prediction
from app.tools.rain_fall import get_rainfall_prediction
from app.tools.weather_tool import get_weather_info
from app.tools.soil_tool import get_soil_info
from app.tools.general_info_tool import search_external_knowledge
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

# -----------------------------
# TOOLS
# -----------------------------
# @tool
# def get_crop_prediction() -> str:
#     """Always use this tool when user asks about crops. Do NOT ask for inputs."""
#     return "In Maharashtra with red soil, Sugarcane or Cotton is recommended."

# @tool
# def get_weather() -> str:
#     """Automatically returns current weather for the farmer's region."""
#     return "The weather in Maharashtra is 28°C with high humidity."

TOOLS = [get_crop_prediction, get_fertilizer_prediction , get_rainfall_prediction , get_weather_info , get_soil_info, search_external_knowledge]

# -----------------------------
# SARVAM LLM SETUP
# -----------------------------
### for online commnication 
def get_sarvam_llm(model_name: str = "sarvam-30b") -> ChatOpenAI:
    api_key = os.getenv("SARVAM_MODEL_API")
    model_name = os.getenv("SARVAM105_MODEL_NAME")
    if not api_key:
        raise ValueError("SARVAM_MODEL_API environment variable not set.")
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.sarvam.ai/v1",
        model=model_name,
        temperature=0.0
    )

def get_gemini_llm(moddel_name: str = "gemini-1.5-pro"):
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)



## for offline communication
def get_ollama_llm(model_name: str = "llama3"):
    return ChatOllama(
        model=model_name,
        temperature=0.1,
        streaming=True
    )


# -----------------------------
# DYNAMIC SYSTEM PROMPT
# -----------------------------

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
# def get_system_prompt(expertise_level: str = "beginner") -> str:
#     base = (
#         "You are an expert Indian Agriculture Advisor. "
#         "Use the available tools automatically to answer farmer queries. "
#         "Always reply in the same language as the user's latest message. "
#         "If the user writes in Hindi, reply in Hindi. "
#         "If the user writes in Tamil, reply in Tamil. "
#         "If the user writes in English, reply in English. "
#         "If tool results are in English, convert them into the user's language in the final response. "
#         "Preserve crop names, fertilizer names, chemical names, numbers, units, place names, and temperatures accurately. "
#         "Keep the reply practical, simple, and farmer-friendly. "
#         "Do not ask unnecessary follow-up questions."
#     )
#     if expertise_level == "beginner":
#         return f"{base} Explain in very simple language."
#     return base

# def get_system_prompt(expertise_level: str = "beginner") -> str:
#     base = (
#         "You are an expert Indian Agriculture Advisor. "
#         "Use the available tools automatically to answer farmer queries."
#     )
#     if expertise_level == "beginner":
#         return f"{base} Explain in simple language without asking for extra input."
#     return base


def get_system_prompt(expertise_level: str = "beginner") -> str:
    base = (
        "You are an expert Indian Agriculture Advisor. "
        "You MUST use the provided tools to answer questions. "
        "Do NOT answer from your own knowledge if a tool is available. "
        "Always return the tool output as the main answer. "
        "Do NOT ask follow-up questions. "
        "Keep the answer simple and farmer-friendly. "
        "Reply in the same language as the user."
    )
    return base


# -----------------------------
# AGENT CREATION
# -----------------------------
def create_farmer_agent(llm: ChatOpenAI, checkpointer: SqliteSaver):
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=get_system_prompt("beginner"),
        checkpointer=checkpointer,
        debug=True
    )


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