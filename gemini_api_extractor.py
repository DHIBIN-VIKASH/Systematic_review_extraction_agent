import os
import time
import json
import pandas as pd
import argparse
import google.generativeai as genai
from google.api_core import exceptions
from template_parser import parse_template, get_field_names

# Configuration
ARTICLES_DIR = 'Articles'
OUTPUT_FILE = 'extracted_studies_api.xlsx'  # New output file to avoid conflict
DEFAULT_TEMPLATE = 'GLP1_Meta_Analysis_Data_Extraction_Template.docx'
MODEL_NAME = "models/gemini-flash-latest"

# Global variable to store template fields
TEMPLATE_FIELDS = None
ALL_COLUMNS = None

def load_template(template_path):
    """Load template and set global field variables."""
    global TEMPLATE_FIELDS, ALL_COLUMNS
    print(f"Loading template: {template_path}")
    TEMPLATE_FIELDS = parse_template(template_path)
    ALL_COLUMNS = get_field_names(TEMPLATE_FIELDS)
    print(f"Loaded {len(TEMPLATE_FIELDS)} fields from template")

def create_prompt():
    """Create extraction prompt from loaded template fields."""
    if TEMPLATE_FIELDS is None:
        raise ValueError("Template not loaded. Call load_template() first.")
    
    prompt = "You are an expert scientific researcher. Extract the following information from the attached PDF study.\n"
    prompt += "Return the result as a valid JSON object where keys are the 'Field Name' and values are the extracted text/numbers. If information is strictly missing, use null.\n"
    prompt += "Do not hallucinate data. If you are unsure, extraction is better left as null.\n\n"
    
    # Group fields by section for better context
    sections = {}
    for field in TEMPLATE_FIELDS:
        section = field.section if field.section else "General"
        if section not in sections:
            sections[section] = []
        sections[section].append(field)
    
    for section_name, fields in sections.items():
        prompt += f"--- {section_name} ---\n"
        for field in fields:
            desc = f": {field.description}" if field.description else ""
            prompt += f"- {field.name}{desc}\n"
    
    prompt += "\nReturn ONLY the JSON object. No markdown formatting (like ```json), no preamble."
    return prompt

def clean_json_string(response_text):
    """Clean the response text to get valid JSON."""
    text = response_text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        # Find the first newline
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline+1:]
        # Remove the closing ```
        if text.endswith("```"):
            text = text[:-3]
    
    text = text.strip()
    return text

def extract_study_with_api(pdf_path, prompt):
    """Uploads file and extracts data using Gemini API."""
    print(f"[{os.path.basename(pdf_path)}] Uploading to Gemini...")
    
    try:
        # Upload the file
        sample_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
        
        # Verify state
        while sample_file.state.name == "PROCESSING":
            time.sleep(1)
            sample_file = genai.get_file(sample_file.name)
            
        if sample_file.state.name == "FAILED":
            print(f"[{os.path.basename(pdf_path)}] File processing failed.")
            return None

        # Generate content
        print(f"[{os.path.basename(pdf_path)}] Generating extraction...")
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Configure Generation config for JSON output (available in 1.5 Pro/Flash)
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )

        response = model.generate_content(
            [sample_file, prompt],
            generation_config=generation_config
        )
        
        # Clean up the file from cloud storage to be polite/clean
        try:
            genai.delete_file(sample_file.name)
        except:
            pass # Not critical

        # Parse Response
        try:
            text = clean_json_string(response.text)
            data = json.loads(text)
            data['Source File'] = os.path.basename(pdf_path)
            return data
        except json.JSONDecodeError:
            print(f"[{os.path.basename(pdf_path)}] Error: Invalid JSON returned.")
            print(f"Debug Raw: {response.text[:100]}...")
            return None
            
    except exceptions.ResourceExhausted:
         print(f"[{os.path.basename(pdf_path)}] Quota exceeded (429). Waiting 30 seconds...")
         time.sleep(30)
         return "RETRY"
    except Exception as e:
        print(f"[{os.path.basename(pdf_path)}] API Error: {e}")
        return None

def main(api_key, limit=None, template_path=None):
    # Configure API
    genai.configure(api_key=api_key)
    
    # Load Template
    if template_path is None:
        template_path = DEFAULT_TEMPLATE
    
    try:
        load_template(template_path)
    except Exception as e:
        print(f"Error loading template: {e}")
        return

    # Get Files
    if not os.path.exists(ARTICLES_DIR):
        print(f"Error: Directory {ARTICLES_DIR} does not exist.")
        return

    pdf_files = [os.path.join(ARTICLES_DIR, f) for f in os.listdir(ARTICLES_DIR) if f.lower().endswith('.pdf')]
    
    # Filter processed
    processed_files = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_excel(OUTPUT_FILE)
            if 'Source File' in df_existing.columns:
                processed_files = set(df_existing['Source File'].astype(str).tolist())
        except:
            pass

    files_to_process = [f for f in pdf_files if os.path.basename(f) not in processed_files]
    
    if limit:
        files_to_process = files_to_process[:int(limit)]

    print(f"Found {len(pdf_files)} total. {len(files_to_process)} to process.")
    
    prompt = create_prompt()
    results = []

    for pdf_path in files_to_process:
        # Retry loop
        max_retries = 3
        for attempt in range(max_retries):
            data = extract_study_with_api(pdf_path, prompt)
            
            if data == "RETRY":
                continue # The function already waited
            
            if data:
                results.append(data)
                
                # Save Incrementally
                df = pd.DataFrame([data])
                # Ensure all columns
                for c in ALL_COLUMNS:
                    if c not in df.columns: df[c] = None
                
                # Reorder
                cols = ['Source File'] + [c for c in ALL_COLUMNS if c in df.columns]
                df = df[cols]
                
                if os.path.exists(OUTPUT_FILE):
                    existing = pd.read_excel(OUTPUT_FILE)
                    df = pd.concat([existing, df], ignore_index=True)
                
                df.to_excel(OUTPUT_FILE, index=False)
                print(f"Saved {os.path.basename(pdf_path)}")
                
                # Rate Limit Safety: 15 RPM = ~4s per request. 
                # To be super safe and avoid 429s, wait 4 seconds.
                time.sleep(4) 
                break
            else:
                print(f"Failed to extract {os.path.basename(pdf_path)} after attempt {attempt+1}")
                time.sleep(2)
        
    print("Optimization Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract data using Gemini API")
    parser.add_argument("--key", help="Gemini API Key", required=True)
    parser.add_argument("--template", help="Path to template file", default=DEFAULT_TEMPLATE)
    parser.add_argument("--limit", help="Limit number of files", default=None)
    args = parser.parse_args()
    
    main(args.key, args.limit, args.template)
