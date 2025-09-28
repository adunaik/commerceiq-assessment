# CommerceIQ Diagnostic Reporting Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

⚡ Automated pipeline that consolidates **catalog, inventory, performance, competitor, and marketplace data** into actionable insights.  
Generates **JSON, CSV, HTML (with charts), and Excel (multi-sheet)** reports with executive summaries, trends, and recommendations.

---

## 📊 Features

- ✅ Stockouts & high-priority risk detection  
- ✅ Price benchmarking vs competitors  
- ✅ Marketing ROI & efficiency checks  
- ✅ Marketplace content quality diagnostics  
- ✅ Competitor promotions & launches tracking  
- ✅ Executive-ready **HTML + Excel** outputs with charts  
- ✅ Logging pipeline for full traceability  

---

## 🚀 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/adunaik/commerceiq-assessment.git
cd commerceiq-assessment/scripts_new
2. Create & activate virtual environment
bash
Copy code
python -m venv venv
venv\Scripts\activate       # Windows
# or
source venv/bin/activate    # macOS/Linux
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Run the pipeline
bash
Copy code
python report.py
5. Outputs
Reports are generated inside the outputs/ folder:

diagnostic_report.json

diagnostic_report.csv

diagnostic_report.html (boardroom-ready with charts)

diagnostic_report.xlsx (multi-sheet with summary, risks, trends, issues)

Logs are saved in logs/pipeline.log.
