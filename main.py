import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF

from db_connection import add_to_table, get_db_connection
from fx_scraper import FX
from kitco_scraper import Scraper
from llama3 import (
    FinancialAnalysisAgent,
    accumulate_batches,
    batch_articles,
    generate_final_report,
)

load_dotenv()

# Step 1: Initialize Scrapers for Kitco and FX articles
kitco_scraper = Scraper()
kitco_articles_df = kitco_scraper.scrape_articles()

fx_scraper = FX()
fx_articles_df = fx_scraper.scrape_articles()

kitco_articles_df = pd.read_csv("articles.csv")
fx_articles_df = pd.read_csv("FX.csv")

# Step 2: Combine both DataFrames
combined_articles_df = pd.concat([kitco_articles_df, fx_articles_df], ignore_index=True)

# Step 3: Save the combined DataFrame to the database
table_name = 'articles'
get_db_connection(df=fx_articles_df, table_name=table_name)
print("table 1 added successfully")

add_to_table(table_name=table_name, df=kitco_articles_df)
print("table 2 added successfully")

df = pd.read_csv("combined_articles.csv")

articles_per_batch = 5

def run(text):
    # Split the text into batches
    text_batches = batch_articles(df, articles_per_batch)
    # Create the agent
    agent = FinancialAnalysisAgent().financial_analyst()
    # Accumulate all batches of text
    accumulate_batches(agent, text_batches)
    # Generate the final report considering the entire text
    final_report = generate_final_report(agent, text)
    return final_report

def save_report_as_pdf(report_text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add the text
    for line in report_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Save the PDF
    pdf.output(filename)

if __name__ == "__main__":
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv("combined_articles.csv")
    # Combine all the text from the 'body' column into a single string
    content = df["body"]
    # Generate the analysis report
    final_report = run(content)
    # Print the generated report
    print(final_report)
    # Save the report as a PDF
    save_report_as_pdf(final_report, "final_report.pdf")
    print("Final report saved as final_report.pdf")


