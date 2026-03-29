# import os
# from dotenv import load_dotenv
# from langchain_core.messages import HumanMessage
# from langgraph.checkpoint.sqlite import SqliteSaver

# # Your custom app imports
# from app.agents.online_farmer_agent import get_sarvam_llm, create_farmer_agent, call_chat_only
# from app.agents.router_logic import get_routing_decision
# from app.core.user_context import set_current_user

# load_dotenv()

# if __name__ == "__main__":
#     DB_PATH = "app/data/farmer_data.db"
    
#     # Get model names from env
#     tool_model_name = os.getenv("SARVAM105_MODEL_NAME")
#     chat_model_name = os.getenv("SARVAM30_MODEL_NAME")
    
#     # Initialize persistence
#     with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        
#         # 1. Pre-initialize both LLMs once
#         # Use the 30B (smaller/faster) for tools if you prefer, 105B for rich chat
#         agent_llm = get_sarvam_llm(tool_model_name) 
#         chat_llm = get_sarvam_llm(chat_model_name)
        
#         # 2. Create the agent once
#         agent = create_farmer_agent(agent_llm, checkpointer)
        
#         print("\n🌾 Sarvam Krishi AI is Online!")
#         print(f"📁 Memory Logged to: {DB_PATH}\n")

#         while True:
#             current_user = input("Enter User ID (e.g., user1): ").strip()
#             if not current_user: continue
            
#             user_query = input(f"[{current_user}] You: ").strip()
#             if user_query.lower() in ["exit", "quit"]:
#                 print("Shubhkamnaye! 🌱 (Goodbye)")
#                 break

#             try:
#                 # Configuration for thread-based memory
#                 config = {"configurable": {"thread_id": current_user}}
                
#                 # --- ROUTING LOGIC ---
#                 # Decision happens fast here
#                 decision = get_routing_decision(user_query)
                
#                 if decision == "TOOL":
#                     print(f"[System] 🛠️ Routing to Agricultural Tool Agent...")
#                     # ✅ Set the active user so tools read the right location & crop
#                     set_current_user(current_user)
#                     response = agent.invoke(
#                         {"messages": [HumanMessage(content=user_query)]},
#                         config=config
#                     )
#                     # LangGraph agents return the full message list
#                     final_text = response["messages"][-1].content
#                 else:
#                     print(f"[System] 💬 Routing to Conversational Chat...")
#                     # USE THE PRE-INITIALIZED chat_llm (Faster!)
#                     final_text = call_chat_only(chat_llm, user_query, config, checkpointer)

#                 print(f"\nAgent: {final_text}\n" + "-"*40)

#             except Exception as e:
#                 print(f"❌ System Error: {e}\n")



from app.tools.yield_tool import YieldPredictionInternalTool
from app.tools.crop_tool import CropRecommendationInternalTool
from app.tools.fertilizer_tool import FertilizerPredictionTool
from app.tools.rain_fall import RainfallPredictionTool
from app.tools.weather_tool import WeatherInfoTool
from app.tools.soil_tool import SoilInfoTool
from app.tools.general_info_tool import ExternalKnowledgeSearchTool
from app.tools.farm_advice_tool import FarmPracticeRAGTool
from app.tools.goverment_schema_tool import GovSchemeRAGTool


tool = RainfallPredictionTool()

print("=== Yield Tool Test ===")

result = tool._run()

print(result)