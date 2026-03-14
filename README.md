# 📄 Systematic Review Data Extraction Agent

![Gemini](https://img.shields.io/badge/Gemini-2.0--Flash-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-orange)
![License](https://img.shields.io/badge/License-MIT-red)

An intelligent agent that automates high-fidelity data extraction from PDF full-text articles for systematic reviews and meta-analyses. 

> [!IMPORTANT]
> **API-First Methodology**: This agent primarily uses the **Google Gemini API** for high-speed, structured extraction. A Playwright-based browser fallback is provided for manual-like interaction.

---

## ✨ Key Features

- **🤖 AI-Powered Extraction**: Uses Google Gemini to intelligently extract structured data from PDF articles.
- **📋 Flexible Templates**: Define extraction fields using **Word (.docx)** or **Excel (.xlsx)** templates.
- **🔄 Auto-Detection**: Seamlessly switches between template formats.
- **💾 Incremental Saving**: Saves progress after each file, ensuring no data loss during long runs.
- **📊 Structured Excel Output**: Generates clean, ready-to-analyze Excel sheets.
- **🔁 Resume Support**: Automatically skips already-processed files for efficient restarts.

> [!NOTE]
> Running the extraction and validation agents requires the user to have or input an API key. Google allows a certain amount of free credits for every user, which is more than sufficient for these extraction and validation purposes; you do not need to worry about costs for typical review workloads.

---

## 🚀 Getting Started

### 📋 Prerequisites
- **Python 3.8+**
- **Google AI Studio Key** ([Get it here](https://a studio.google.com/app/apikey))
- **PDF Articles** (Placed in the `Articles/` directory)

### 📦 Installation
```bash
git clone https://github.com/DHIBIN-VIKASH/Systematic_review_extraction_agent.git
cd Systematic_review_extraction_agent
pip install -r requirements.txt
playwright install chromium
```

---

## 📖 Usage

### ⚡ Gemini API Extraction (Default & Recommended)
This is the fastest method. It uploads PDFs directly to the API, bypassing browser overhead.

```bash
python gemini_api_extractor.py --key "YOUR_API_KEY"
```

**Options:**
- `--key`: Your Google Gemini API Key (**Required**).
- `--template`: Path to custom template (defaults to `GLP1_Meta_Analysis_Data_Extraction_Template.docx`).
- `--limit`: Process only the first N files.

---

### 🌐 Browser-Based Extraction (Alternative)
Uses **Playwright** to interact with the Gemini web interface. Slower but allows you to watch the process in real-time.

```bash
python gemini_extractor.py --browser chrome
```

---

## 📝 Custom Templates

### Word Templates (.docx)
Structure your document with sections and fields ending in a colon:
```text
Baseline Characteristics
Age (Mean ± SD):
BMI (Mean ± SD):
```

### Excel Templates (.xlsx)
Simply create an Excel file where the first row contains the **Column Headers** representing your extraction fields.

---

## 📁 Project Structure

```text
Systematic_review_extraction_agent/
├── gemini_api_extractor.py     # High-speed API script
├── gemini_extractor.py         # Browser-based fallback script
├── template_parser.py          # Logic for reading Word/Excel templates
├── Articles/                   # Place research PDFs here
└── requirements.txt            # Python dependencies
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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

---
**Made with ❤️ for systematic review researchers**
m/DHIBIN-VIKASH/Systematic_review_extraction_agent/issues).

---

**Made with ❤️ for systematic review researchers**
