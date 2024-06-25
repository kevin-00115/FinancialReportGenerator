import os
import pandas as pd
from crewai import Agent, Crew, Task
from dotenv import load_dotenv
import time 

# Load environment variables from .env file (if any)
load_dotenv()

# Ensure necessary OpenAI API keys and configurations are set
os.environ["OPENAI_API_KEY"]='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'
os.environ["OPENAI_API_BASE"] = 'https://api.groq.com/openai/v1'
os.environ['OPENAI_MODEL_NAME'] = 'llama3-70b-8192'

class FinancialAnalysisAgent:
    def financial_analyst(self):
        return Agent(
            role='The Best Financial Analyst',
            goal="""Impress all customers with your financial data 
            and market trends analysis""",
            backstory="""The most seasoned financial analyst with 
            lots of expertise in Gold market analysis and investment
            strategies that is working for a super important customer.""",
            verbose=True
        )

articles_per_batch = 5  # Define how many articles per batch

def batch_articles(dataframe, articles_per_batch):
    # Split DataFrame into batches of specified number of articles
    return [dataframe.iloc[i:i + articles_per_batch] for i in range(0, len(dataframe), articles_per_batch)]

def accumulate_batches(agent, article_batches):
    # Function to let the agent read all text batches
    for batch_index, batch in enumerate(article_batches):
        texts = batch['body'].tolist()  # Get list of articles' texts from the batch
        for article_index, text in enumerate(texts):
            read_task = Task(
                description=f"Read and assimilate this text: {text}, do not generate any output",
                agent=agent,
                expected_output= "no output"
            )
            read_crew = Crew(agents=[agent], tasks=[read_task], verbose=True)
            # Execute the task
            read_crew.kickoff()

            # Print the progress message
            print(f"Read Article {article_index + 1} from Batch {batch_index + 1}")

            # Optional: sleep between processing each article if needed to manage load or API usage
            time.sleep(1)  # Sleep for 1 second between articles

def generate_final_report(agent, accumulated_text):
    # Generate a report after all text has been read
    final_report_task = Task(
        description=f"""
            Read the {accumulated_text} and using the accumulated knowledge from all the text read,
            generate a comprehensive summary report on the latest news,
            market sentiment shifts, and potential impacts on the gold market.
        """,
        agent=agent,
        expected_output="The final comprehensive report of the latest news, market sentiment, and potential impacts on gold."
    )
    final_crew = Crew(agents=[agent], tasks=[final_report_task], verbose=True)
    final_report = final_crew.kickoff()
    return final_report

def run(dataframe):
    # Split the DataFrame into batches
    article_batches = batch_articles(dataframe, articles_per_batch)
    # Create the agent
    agent = FinancialAnalysisAgent().financial_analyst()
    # Accumulate all batches of text
    accumulate_batches(agent, article_batches)
    # Generate the final report considering the entire text
    final_report = generate_final_report(agent, "accumulated article data")
    return final_report

if __name__ == "__main__":
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv("combined_articles.csv")
    # Generate the analysis report
    final_report = run(df)
    # Print the generated report
    print(final_report)