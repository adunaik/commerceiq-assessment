# CommerceIQ Diagnostic Reporting Pipeline

⚡ Automated pipeline that consolidates **catalog, inventory, performance, competitor, and marketplace data** into actionable insights.  
Generates **JSON, CSV, HTML (with charts), and Excel (multi-sheet)** reports with executive summaries, trends, and recommendations.

---

## ✨ Features
- ✅ Stockouts & high-priority risk detection  
- ✅ Price benchmarking vs competitors  
- ✅ Marketing ROI & ad efficiency checks  
- ✅ Marketplace content quality diagnostics  
- ✅ Competitor promotions & launches tracking  
- ✅ Executive-ready **HTML + Excel** outputs with charts  
- ✅ Logging pipeline for full traceability  

---

## 🚀 Quickstart (Run This Project)

Follow these steps to run the pipeline locally:

### **1. Clone the repo**
```bash
git clone https://github.com/adunaik/commerceiq-assessment.git
cd commerceiq-assessment/scripts_new

### **2. Create & activate virtual environment**
python -m venv venv
venv\Scripts\activate       # Windows
# or
source venv/bin/activate    # macOS/Linux

Install dependencies
pip install -r requirements.txt

Run the pipeline
python report.py
