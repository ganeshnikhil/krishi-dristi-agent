import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
#gemini-3-flash-preview

from google.genai import types

def get_keywords_from_gemini(chat_text: str) -> List[str]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Using a configuration that forces a specific structure
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=f"Filter this chat for the 4 most actionable agri-keywords: {chat_text}",
        config=types.GenerateContentConfig(
            # This ensures the model follows a strict pattern
            response_mime_type='application/json',
            response_schema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 5 # Hard limit at the schema level
                    }
                }
            },
            temperature=0.1 # Minimum creativity for maximum accuracy
        )
    )
    
    # The output is now a clean dictionary
    import json
    data = json.loads(response.text)
    return data.get("keywords", [])


