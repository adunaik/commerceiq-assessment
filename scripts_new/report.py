import pandas as pd
import json
import os
import logging
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from analyze import analyze
from ingest import load_data

# PDF export (requires wkhtmltopdf installed)
import pdfkit  

# --------------------
# Setup Logger
# --------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(base_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_report():
    logging.info("Starting report generation pipeline...")

    # Load Data
    catalog, inventory, performance, competitor, marketplace = load_data()
    logging.info("Datasets loaded successfully.")

    # Run Analysis
    insights = analyze(catalog, inventory, performance, competitor, marketplace)
    logging.info("Analysis completed. Found %d insights.", len(insights))

    # Define output directory
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON
    json_path = os.path.join(output_dir, "diagnostic_report.json")
    with open(json_path, "w") as f:
        json.dump(insights, f, indent=4)

    # Save CSV
    csv_path = os.path.join(output_dir, "diagnostic_report.csv")
    df = pd.DataFrame(insights)
    df.to_csv(csv_path, index=False)

    # --------------------
    # Bar Chart: Issues by Count
    # --------------------
    plt.figure(figsize=(8, 5))
    plt.barh(df["issue"], df["count"], color="#2E86C1")
    plt.xlabel("Count")
    plt.ylabel("Issue")
    plt.title("Issues Detected by Category")
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    issues_img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close()

    chart_html = f"""
    <h3 style='color:#2E86C1;'>Issues Overview</h3>
    <img src="data:image/png;base64,{issues_img_base64}" style="max-width:100%; height:auto;">
    <hr>
    """

    # --------------------
    # Weekly Trends Chart
    # --------------------
    if "week_ending" in performance.columns:
        perf_trend = performance.copy()
        perf_trend["week_ending"] = pd.to_datetime(perf_trend["week_ending"])
        trend_data = perf_trend.groupby("week_ending").agg(
            avg_roi=("revenue", lambda x: (x.sum() / perf_trend.loc[x.index, "ad_spend"].sum())),
            stockouts=("conversions", lambda x: (x == 0).sum())
        ).reset_index()

        plt.figure(figsize=(8, 5))
        plt.plot(trend_data["week_ending"], trend_data["avg_roi"], marker="o", label="Avg ROI", color="#28B463")
        plt.bar(trend_data["week_ending"], trend_data["stockouts"], alpha=0.5, label="Stockouts", color="#E74C3C")
        plt.title("Weekly Trends: ROI vs Stockouts")
        plt.xlabel("Week Ending")
        plt.ylabel("Value")
        plt.legend()
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        trend_img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close()

        trend_html = f"""
        <h3 style='color:#2E86C1;'>Weekly Trends</h3>
        <img src="data:image/png;base64,{trend_img_base64}" style="max-width:100%; height:auto;">
        <hr>
        """
    else:
        trend_html = ""
        trend_data = pd.DataFrame()
        logging.warning("No 'week_ending' column in performance data. Skipping trend chart.")

    # --------------------
    # Summary
    # --------------------
    total_issues = df["count"].sum()
    top_risks = df.sort_values("count", ascending=False).head(3)
    summary_html = f"""
    <h2 style='color:#2E86C1;'>Diagnostic Report Summary</h2>
    <p><b>Total Issues Detected:</b> {total_issues}</p>
    <p><b>Top Risks:</b></p>
    <ul>
        {''.join([f"<li>{row['issue']} ({row['count']})</li>" for _, row in top_risks.iterrows()])}
    </ul>
    <hr>
    """

    # --------------------
    # Styled HTML Table
    # --------------------
    styled = df.style.set_table_styles(
        [
            {"selector": "th", "props": [("background-color", "#2E86C1"), ("color", "white"), ("font-weight", "bold")]},
            {"selector": "td", "props": [("border", "1px solid #ddd"), ("padding", "8px")]},
            {"selector": "tr:nth-child(even)", "props": [("background-color", "#f2f2f2")]},
            {"selector": "tr:hover", "props": [("background-color", "#ddd")]}
        ]
    ).set_properties(**{"text-align": "left"})

    html_path = os.path.join(output_dir, "diagnostic_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(summary_html + chart_html + trend_html + styled.to_html())

    # --------------------
    # Excel Export with Styling
    # --------------------
    excel_path = os.path.join(output_dir, "diagnostic_report.xlsx")
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        # Summary
        pd.DataFrame({"Metric": ["Total Issues Detected"], "Value": [total_issues]}).to_excel(
            writer, sheet_name="Summary", index=False
        )
        top_risks.to_excel(writer, sheet_name="Top Risks", index=False)
        df.to_excel(writer, sheet_name="Issues", index=False)
        if not trend_data.empty:
            trend_data.to_excel(writer, sheet_name="Trends", index=False)

        workbook = writer.book
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#2E86C1", "font_color": "white"})
        alt_fmt = workbook.add_format({"bg_color": "#f9f9f9"})

        for sheet in writer.sheets:
            worksheet = writer.sheets[sheet]
            # Style header
            worksheet.set_row(0, None, header_fmt)
            # Auto column width
            df_to_use = df if sheet == "Issues" else (top_risks if sheet == "Top Risks" else trend_data)
            if sheet == "Summary":
                df_to_use = pd.DataFrame({"Metric": ["Total Issues Detected"], "Value": [total_issues]})
            if not df_to_use.empty:
                for i, col in enumerate(df_to_use.columns):
                    max_len = max(df_to_use[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
            # Freeze header row
            worksheet.freeze_panes(1, 0)

    # --------------------
    # PDF Export
    # --------------------
    pdf_path = os.path.join(output_dir, "diagnostic_report.pdf")
    try:
        pdfkit.from_file(html_path, pdf_path)
        logging.info("PDF report saved: %s", pdf_path)
    except Exception as e:
        logging.warning("PDF generation skipped (wkhtmltopdf not installed): %s", e)

    logging.info("All reports generated successfully.")

if __name__ == "__main__":
    generate_report()
    print("Reports generated in outputs/. Check logs/pipeline.log for details.")
