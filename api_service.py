from google import genai
import json
import re
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Backend API Key logic
api_key = os.getenv("GEMINI_API_KEY")

def _clean_numeric(val):
    """Robustly convert API values like '15g', '15.2', 15  → float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    # Strip units (g, mg, mcg, kcal, %) and whitespace
    cleaned = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def _format_micros(micros_raw):
    """
    Convert either a string or a dict response from Gemini into
    a clean human-readable string for display.
    """
    if not micros_raw:
        return ""
    if isinstance(micros_raw, str):
        return micros_raw.strip()
    if isinstance(micros_raw, dict):
        # e.g. {"vitamin_b12": "0.9mcg", "iron": "1.8mg"}  →  "Vitamin B12: 0.9mcg · Iron: 1.8mg"
        parts = []
        for k, v in micros_raw.items():
            label = k.replace("_", " ").title()
            parts.append(f"{label}: {v}")
        return " · ".join(parts)
    return str(micros_raw)

def analyze_food(text):
    if not api_key:
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "micros": "API Key not configured."
        }
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are a professional nutritionist. Analyze the food diary entry below and estimate its nutritional content.
        Food Entry: "{text}"
        
        CRITICAL: Return ONLY a raw JSON object. No markdown, no code fences, no explanation.
        ALL numeric fields (calories, protein, carbs, fats) MUST be plain numbers (no units, no 'g').
        The JSON must have exactly these keys:
        - "calories": number (total kcal)
        - "protein": number (grams)
        - "carbs": number (grams)
        - "fats": number (grams)
        - "micros": string (short human-readable summary of key vitamins & minerals, comma-separated)
        
        Example of correct format: {{"calories": 450, "protein": 22, "carbs": 55, "fats": 14, "micros": "Vitamin B12: 0.9mcg, Iron: 2mg, Vitamin C: 15mg"}}
        """
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Clean response — strip markdown code fences
        response_text = response.text.strip()
        if response_text.startswith("```"):
            lines = [l for l in response_text.split("\n") if not l.strip().startswith("```")]
            response_text = "\n".join(lines).strip()
        
        raw = json.loads(response_text)
        
        # Normalize all fields for safe downstream use
        return {
            "calories": _clean_numeric(raw.get("calories", 0)),
            "protein":  _clean_numeric(raw.get("protein", 0)),
            "carbs":    _clean_numeric(raw.get("carbs", 0)),
            "fats":     _clean_numeric(raw.get("fats", 0)),
            "micros":   _format_micros(raw.get("micros", ""))
        }
    
    except Exception as e:
        st.error(f"Gemini Error: {str(e)}")
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "micros": "Error analyzing input."
        }
