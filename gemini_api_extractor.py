import os
import time
import json
import pandas as pd
import argparse
import google.generativeai as genai
from google.api_core import exceptions
from template_parser import parse_template, get_field_names
from datetime import datetime

# Configuration
ARTICLES_DIR = 'Articles'
OUTPUT_FILE = 'extracted_studies_api.xlsx'
DISCREPANCY_FILE = 'extraction_discrepancies.xlsx'
AUDIT_LOG_FILE = 'extraction_audit_log.json'
DEFAULT_TEMPLATE = 'GLP1_Meta_Analysis_Data_Extraction_Template.docx'
MODEL_NAME = "models/gemini-2.0-flash"
# Fallbacks tried (in order) if the primary model is unavailable for the key.
MODEL_CANDIDATES = [
    "models/gemini-2.0-flash",
    "models/gemini-2.5-flash",
    "models/gemini-1.5-flash",
    "models/gemini-flash-latest",
]


def resolve_model():
    """Pick the first candidate model that the configured key can actually call.
    Sets and returns the global MODEL_NAME."""
    global MODEL_NAME
    for name in MODEL_CANDIDATES:
        try:
            genai.GenerativeModel(name).generate_content("ping")
            MODEL_NAME = name
            print(f"Using model: {name}")
            return name
        except exceptions.NotFound:
            print(f"Model unavailable (404): {name}")
        except exceptions.ResourceExhausted:
            # Quota hit but the model exists — good enough to select it.
            MODEL_NAME = name
            print(f"Using model: {name} (quota-limited)")
            return name
        except Exception as e:
            print(f"Model {name} failed probe: {type(e).__name__}")
    print(f"Warning: no candidate model verified; falling back to {MODEL_NAME}")
    return MODEL_NAME


def _values_equal(v1, v2):
    """Compare two extracted values, treating numerically-equal strings
    (e.g. '5' vs '5.0', '1,000' vs '1000') as equal to avoid spurious
    discrepancy flags."""
    if v1 is None or v2 is None:
        return v1 is None and v2 is None
    s1 = str(v1).strip().lower()
    s2 = str(v2).strip().lower()
    if s1 == s2:
        return True
    try:
        return float(s1.replace(',', '')) == float(s2.replace(',', ''))
    except (ValueError, TypeError):
        return False

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

def create_prompt(pass_num=1):
    """Create extraction prompt from loaded template fields.
    Pass 1 uses standard extraction. Pass 2 uses a rephrased strategy."""
    if TEMPLATE_FIELDS is None:
        raise ValueError("Template not loaded. Call load_template() first.")
    
    if pass_num == 1:
        prompt = "You are an expert scientific researcher. Extract the following information from the attached PDF study.\n"
        prompt += "Return the result as a valid JSON object where keys are the 'Field Name' and values are the extracted text/numbers. If information is strictly missing, use null.\n"
        prompt += "Do not hallucinate data. If you are unsure, extraction is better left as null.\n\n"
    else:
        # Pass 2: Different parsing strategy (rephrased prompt as described in paper)
        prompt = "You are a meticulous data extraction specialist conducting a systematic review. Your task is to independently verify and extract structured data from the attached PDF.\n"
        prompt += "For each field below, carefully search the Methods, Results, and Tables sections of the PDF. Return a JSON object with field names as keys.\n"
        prompt += "Use null ONLY when the information truly does not exist anywhere in the document. For each null value, also provide a justification field named '<FieldName>_justification' explaining why it is null.\n\n"
    
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

def compare_extractions(pass1_data, pass2_data, source_file):
    """
    Compare two extraction passes field-by-field.
    Returns (merged_data, discrepancies, justifications).
    """
    if not pass1_data and not pass2_data:
        return None, [], []
    if not pass1_data:
        return pass2_data, [], []
    if not pass2_data:
        return pass1_data, [], []

    merged = {'Source File': source_file}
    discrepancies = []
    justifications = []
    
    # Get all field names from both passes
    all_keys = set(list(pass1_data.keys()) + list(pass2_data.keys()))
    # Filter out meta keys and justification keys
    field_keys = [k for k in all_keys if k != 'Source File' and not k.endswith('_justification')]
    
    for key in field_keys:
        v1 = pass1_data.get(key)
        v2 = pass2_data.get(key)
        
        # Collect justifications from Pass 2
        justification_key = f"{key}_justification"
        if justification_key in pass2_data:
            justifications.append({
                'field': key,
                'justification': pass2_data[justification_key]
            })
        
        if _values_equal(v1, v2):
            # Agreement (including numeric equality like 5 vs 5.0) —
            # use Pass 1 value to preserve original casing/formatting.
            merged[key] = v1
        elif v1 is None and v2 is not None:
            # Pass 1 missed it, use Pass 2
            merged[key] = v2
            discrepancies.append({
                'Source File': source_file,
                'Field': key,
                'Pass1_Value': str(v1),
                'Pass2_Value': str(v2),
                'Resolution': 'Used Pass 2 (Pass 1 was null)',
                'Severity': 'MINOR'
            })
        elif v2 is None and v1 is not None:
            # Pass 2 missed it, use Pass 1
            merged[key] = v1
            discrepancies.append({
                'Source File': source_file,
                'Field': key,
                'Pass1_Value': str(v1),
                'Pass2_Value': str(v2),
                'Resolution': 'Used Pass 1 (Pass 2 was null)',
                'Severity': 'MINOR'
            })
        else:
            # Both have values but they differ — flag for human review
            merged[key] = v1  # Keep Pass 1, flag discrepancy
            discrepancies.append({
                'Source File': source_file,
                'Field': key,
                'Pass1_Value': str(v1),
                'Pass2_Value': str(v2),
                'Resolution': 'NEEDS HUMAN REVIEW (used Pass 1 value)',
                'Severity': 'CRITICAL'
            })
    
    return merged, discrepancies, justifications


def main(api_key, limit=None, template_path=None, dual_pass=True):
    # Configure API
    genai.configure(api_key=api_key)

    # Select a model this key can actually use.
    resolve_model()

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

    print(f"\n{'='*70}")
    mode_label = "DUAL-PASS" if dual_pass else "SINGLE-PASS"
    print(f"{mode_label} DATA EXTRACTION AGENT")
    print(f"{'='*70}")
    print(f"Found {len(pdf_files)} total. {len(files_to_process)} to process.")
    if dual_pass:
        print("Mode: Cross-agent redundancy (two independent extraction passes)")
    
    prompt_pass1 = create_prompt(pass_num=1)
    prompt_pass2 = create_prompt(pass_num=2) if dual_pass else None
    
    all_discrepancies = []
    all_justifications = []
    audit_entries = []

    for pdf_path in files_to_process:
        basename = os.path.basename(pdf_path)
        print(f"\n--- Processing: {basename} ---")
        
        # Pass 1
        print(f"  [Pass 1] Extracting...")
        data1 = extract_study_with_api(pdf_path, prompt_pass1)
        if data1 == "RETRY":
            data1 = extract_study_with_api(pdf_path, prompt_pass1)  # One more try
        if data1 == "RETRY":
            data1 = None
        
        if dual_pass and data1:
            # Pass 2 (independent, different prompt strategy)
            print(f"  [Pass 2] Independent re-extraction...")
            time.sleep(4)  # Rate limit safety
            data2 = extract_study_with_api(pdf_path, prompt_pass2)
            if data2 == "RETRY":
                data2 = extract_study_with_api(pdf_path, prompt_pass2)
            if data2 == "RETRY":
                data2 = None
            
            # Compare passes
            merged, discrepancies, justifications = compare_extractions(data1, data2, basename)
            all_discrepancies.extend(discrepancies)
            all_justifications.extend(justifications)
            
            n_critical = sum(1 for d in discrepancies if d['Severity'] == 'CRITICAL')
            n_minor = sum(1 for d in discrepancies if d['Severity'] == 'MINOR')
            if discrepancies:
                print(f"  ⚠️ {len(discrepancies)} discrepancies ({n_critical} critical, {n_minor} minor)")
            else:
                print(f"  ✅ Both passes agree")
            
            audit_entries.append({
                'source_file': basename,
                'pass1_extracted': data1 is not None,
                'pass2_extracted': data2 is not None,
                'discrepancies': len(discrepancies),
                'critical_discrepancies': n_critical,
                'justifications': justifications
            })
            
            data = merged
        else:
            data = data1
            if data:
                data['Source File'] = basename
            audit_entries.append({
                'source_file': basename,
                'pass1_extracted': data is not None,
                'pass2_extracted': False,
                'discrepancies': 0,
                'critical_discrepancies': 0,
                'justifications': []
            })
        
        if data:
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
            print(f"  💾 Saved {basename}")
            
            # Rate Limit Safety
            time.sleep(4) 
        else:
            print(f"  ❌ Failed to extract {basename}")
    
    # Save discrepancies
    if all_discrepancies:
        disc_df = pd.DataFrame(all_discrepancies)
        disc_df.to_excel(DISCREPANCY_FILE, index=False)
        print(f"\n⚠️ Extraction discrepancies saved to: {DISCREPANCY_FILE}")
    
    # Save audit log
    total_critical = sum(e['critical_discrepancies'] for e in audit_entries)
    total_justifications = sum(len(e['justifications']) for e in audit_entries)
    
    audit_output = {
        'timestamp': datetime.now().isoformat(),
        'template': template_path,
        'model': MODEL_NAME,
        'dual_pass': dual_pass,
        'summary': {
            'files_processed': len(files_to_process),
            'files_extracted': sum(1 for e in audit_entries if e['pass1_extracted']),
            'total_discrepancies': len(all_discrepancies),
            'critical_discrepancies': total_critical,
            'justification_logs': total_justifications
        },
        'entries': audit_entries,
        'discrepancies': all_discrepancies,
        'justifications': all_justifications
    }
    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(audit_output, f, indent=2, ensure_ascii=False)
    print(f"📝 Audit log saved to: {AUDIT_LOG_FILE}")
    
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed:        {len(files_to_process)}")
    print(f"Successfully extracted:  {sum(1 for e in audit_entries if e['pass1_extracted'])}")
    if dual_pass:
        print(f"Total discrepancies:    {len(all_discrepancies)}")
        print(f"Critical discrepancies: {total_critical}")
        print(f"Justification logs:     {total_justifications}")
    print(f"{'='*60}")
    print("Extraction Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract data using Gemini API with dual-pass redundancy")
    parser.add_argument("--key", help="Gemini API Key (or set GEMINI_API_KEY env var)", default=None)
    parser.add_argument("--template", help="Path to template file", default=DEFAULT_TEMPLATE)
    parser.add_argument("--limit", help="Limit number of files", default=None)
    parser.add_argument("--single-pass", action="store_true",
                        help="Run single pass only (skip cross-agent redundancy)")
    args = parser.parse_args()

    # Prefer the env var so the key never lands in shell history / process list.
    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        parser.error("No API key provided. Pass --key or set the GEMINI_API_KEY environment variable.")

    main(api_key, args.limit, args.template, dual_pass=not args.single_pass)
