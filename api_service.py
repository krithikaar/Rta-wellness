from google import genai
import json
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Backend API Key logic - google-genai automatically looks for GEMINI_API_KEY
# but we'll check it here for error reporting.
api_key = os.getenv("GEMINI_API_KEY")

@st.cache_data
def analyze_food(text):
    if not api_key:
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "micros": "API Key not configured in backend."
        }
    
    try:
        # Initialize the new Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Act as a professional nutritionist. Analyze the following food diary entry and estimate the nutritional content.
        Food Entry: "{text}"
        
        Return ONLY a JSON object. Do not include any markdown formatting like ```json or ```. Just the raw JSON string.
        The JSON should have these keys:
        - "calories": (total kcal as a number)
        - "protein": (total protein in grams as a number)
        - "carbs": (total carbohydrates in grams as a number)
        - "fats": (total fats in grams as a number)
        - "micros": (a short string summarizing key vitamins/minerals found)
        
        If the entry is vague, provide your best professional estimate.
        """
        
        # New SDK syntax: client.models.generate_content
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt
        )
        
        # Clean response text
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(response_text)
    
    except Exception as e:
        st.error(f"Gemini Error: {str(e)}")
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "micros": "Error analyzing input."
        }
