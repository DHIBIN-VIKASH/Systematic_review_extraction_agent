# Systematic Review Data Extraction Agent

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Playwright](https://img.shields.io/badge/playwright-1.40+-orange.svg)

An intelligent agent that automates data extraction from PDF full-text articles for systematic reviews and meta-analyses using Google Gemini AI. Supports flexible template-based extraction with both **Word (.docx)** and **Excel (.xlsx)** template formats.

## ✨ Features

- **🤖 AI-Powered Extraction**: Uses Google Gemini to intelligently extract structured data from PDF articles
- **📋 Flexible Templates**: Define extraction fields using Word or Excel templates
- **🔄 Auto-Detection**: Automatically detects and parses template format
- **💾 Incremental Saving**: Saves progress after each file to prevent data loss
- **🌐 Browser Automation**: Uses Playwright for reliable Gemini interaction
- **📊 Excel Output**: Generates structured Excel files with extracted data
- **🔁 Resume Support**: Automatically skips already-processed files

## 📋 Prerequisites

- **Python 3.8+**
- **Google Account** (for Gemini access)
- **Dependencies**: See `requirements.txt`

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DHIBIN-VIKASH/Systematic_review_extraction_agent.git
cd Systematic_review_extraction_agent
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

## 📖 Usage

### Quick Start

1. **Place PDF articles** in the `Articles/` directory
2. **Run the extraction**:

```bash
python gemini_extractor.py
```

The script will use the default Word template and process all PDFs.

### ⚡ Fast API Extraction (Recommended)
The original browser-based extraction can be slow. We now offer a **direct API extraction** method using Google's free Gemini API. This method is significantly faster, more reliable, and recommended for most users.

#### Setup
1. Get a **Free API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Run the API extractor with your key:

```bash
python gemini_api_extractor.py --key "YOUR_API_KEY_HERE"
```

*Note: Replace `YOUR_API_KEY_HERE` with the actual key you generated.*

#### Output
Data extracted via the API method is saved to: **`extracted_studies_api.xlsx`**

#### Options
- `--key`: Your Google Gemini API Key (Required).
- `--template`: Path to your custom template (default: `GLP1_Meta_Analysis_Data_Extraction_Template.docx`).
- `--limit`: Limit the number of files to process (useful for testing).

### Using Custom Templates

#### With Word Template

```bash
python gemini_extractor.py --template my_template.docx
```

#### With Excel Template

```bash
python gemini_extractor.py --template my_template.xlsx
```

### Command-Line Options

```bash
python gemini_extractor.py [OPTIONS]

Options:
  --template PATH    Path to template file (.docx or .xlsx)
                     Default: GLP1_Meta_Analysis_Data_Extraction_Template.docx
  --limit N          Process only first N files (for testing)
  --browser BROWSER  Browser to use (chrome or msedge)
                     Default: chrome

Examples:
  python gemini_extractor.py --limit 5
  python gemini_extractor.py --template custom.xlsx --browser msedge
```

## 📝 Creating Templates

### Word Template Format

Create a `.docx` file with field definitions in this format:

```
Study Identification

Study ID:
First Author:
Year:
Journal:

Baseline Characteristics

Age (Mean ± SD):
BMI (Mean ± SD):
```

- **Section headers**: Plain text without colons
- **Field definitions**: Field name followed by colon
- **Descriptions**: Optional text after the colon

### Excel Template Format

Create an `.xlsx` file with:
- **Column headers** as field names
- Each column represents one extraction field
- First row contains field names

### Inspecting Templates

Use the inspection utility to view template structure:

```bash
python inspect_template.py template.docx
python inspect_template.py template.xlsx --verbose
```

## 🔧 How It Works

1. **Template Loading**: Parses your template file to extract field definitions
2. **Browser Launch**: Opens a persistent browser session with Gemini
3. **PDF Upload**: For each PDF, uploads to Gemini and sends extraction prompt
4. **Data Extraction**: Gemini analyzes the PDF and returns structured JSON
5. **Excel Export**: Saves extracted data to `extracted_studies.xlsx`
6. **Progress Tracking**: Remembers processed files for resume capability

## 🛠️ Troubleshooting

### Login Issues

If the script can't find the upload button:
- Ensure you're logged into Google Gemini in the browser window
- Wait for the page to fully load before the script continues
- Check that your Google account has Gemini access

### Template Errors

```bash
# Validate your template
python inspect_template.py your_template.docx
```

If no fields are found:
- Check that field names end with colons (Word templates)
- Verify column headers exist (Excel templates)
- Ensure the file isn't corrupted

### Browser Issues

```bash
# Try a different browser
python gemini_extractor.py --browser msedge

# Reinstall Playwright browsers
playwright install --force chromium
```

## 📚 Project Structure

```
Systematic_review_extraction_agent/
├── gemini_extractor.py              # Main extraction script
├── template_parser.py               # Template parsing module
├── inspect_template.py              # Template inspection utility
├── Articles/                        # Place PDFs here
├── GLP1_Meta_Analysis_Data_Extraction_Template.docx
├── GLP1_Meta_Analysis_Data_Extraction_Template (1).xlsx
├── requirements.txt
├── LICENSE
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for AI-powered extraction
- **Playwright** for browser automation
- Built for systematic review researchers and meta-analysts

## 📧 Citation

If you use this tool in your research, please cite:

```bibtex
@software{systematic_review_extraction_agent,
  author = {DHIBIN-VIKASH},
  title = {Systematic Review Data Extraction Agent},
  year = {2026},
  url = {https://github.com/DHIBIN-VIKASH/Systematic_review_extraction_agent}
}
```

## 🐛 Issues & Support

Found a bug or have a feature request? Please open an issue on [GitHub Issues](https://github.com/DHIBIN-VIKASH/Systematic_review_extraction_agent/issues).

---

**Made with ❤️ for systematic review researchers**
