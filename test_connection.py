import google.generativeai as genai
import sys
import time
from google.api_core import exceptions

key = sys.argv[1]
genai.configure(api_key=key)

models_to_test = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro"
]

print("--- Data Extraction Model Test ---")

for model_name in models_to_test:
    print(f"\nTesting: {model_name} ...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Reply with 'OK' if you receive this.")
        print(f"SUCCESS: {response.text}")
        break # Found a working one!
    except exceptions.NotFound:
        print("FAILED: Model not found (404).")
    except exceptions.ResourceExhausted:
         print("FAILED: Quota/Rate Limit Exceeded (429).")
    except Exception as e:
        print(f"FAILED: {type(e).__name__} - {e}")
    
    time.sleep(1)
