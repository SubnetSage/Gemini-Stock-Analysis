import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from PyPDF2 import PdfReader
import docx
import os
import re
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload
import datetime
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key from environment variables
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("Gemini API key is not set. Please add it to the .env file.")

# Set up Google Docs API credentials
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]

def get_google_services(credentials_file):
    """Initialize Google Drive and Docs services."""
    credentials = Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    docs_service = build('docs', 'v1', credentials=credentials)
    return drive_service, docs_service

def analyze_document(file_content, analysis_type="financial"):
    """Send document content to Gemini API for analysis."""
    try:
        # Configuring the Gemini API
        genai.configure(api_key=GENAI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        if analysis_type == "financial":
            prompt = (
                "Please provide a detailed summary of the company's financial performance in the document. "
                "Include insights on revenue growth, profitability, major expenses, and any notable trends or challenges. "
                "Focus on the overall financial health and performance of the company in the past quarter or year.\n\n"
                "Analyze the following key financial aspects based on the provided quarterly earnings report:\n"
                "1. Revenue and Growth: Is revenue growing or shrinking? Which business segments contributed to revenue growth or decline?\n"
                "2. Profitability: What are the gross, operating, and net profit margins? How do they compare to previous periods or industry peers?\n"
                "3. Earnings Per Share (EPS): What is the company’s EPS? Is it growing or declining?\n"
                "4. Cash Flow: Is the company generating positive operating cash flow? What is the free cash flow (FCF)?\n"
                "5. Balance Sheet: Does the company have more assets than liabilities? What is the debt-to-equity ratio?\n"
                "6. Liquidity: Does the company have enough cash to meet short-term obligations? What is the company’s cash position?\n"
                "7. Expenses: Are expenses growing faster than revenue? How is the company managing costs?\n"
                "8. One-Time Costs and Adjustments: Are there any significant one-time charges or non-recurring items affecting profitability?\n"
                "9. Investment and Capital Spending: How much has the company invested in CapEx or R&D?\n"
                "10. Dividends and Shareholder Returns: Does the company pay a dividend or buy back shares?\n"
                "11. Tax and Risks: What is the effective tax rate? Are there any significant tax or liquidity risks?\n"
                "12. Comparative Performance: How does the company’s financial performance compare to competitors? Is the stock price justified?\n\n"
                + file_content
            )
        elif analysis_type == "swot":
            prompt = (
            "Analyze the provided document to identify the company's strengths, weaknesses, opportunities, and threats (SWOT analysis). "
            "Focus on both internal factors (strengths, weaknesses) and external factors (opportunities, threats) that impact the company's financial health or performance.\n\n"
            "Please provide the result in the following JSON format:\n"
            '{"strengths": ["strength 1", "strength 2"], "weaknesses": ["weakness 1", "weakness 2"], "opportunities": ["opportunity 1", "opportunity 2"], "threats": ["threat 1", "threat 2"]}\n\n'
            + file_content
            )
        elif analysis_type == "summary":
            prompt = (
                "Please provide a concise summary of the key points discussed in the document. "
                "Include information about the main topics covered, any important findings, and the overall message of the document.\n\n"
                + file_content
            )
        elif analysis_type == "chart":
           prompt = (
            "Extract numerical financial data from the document and present it in JSON format for easy plotting. "
            "Identify key metrics such as revenue, profit, expenses, EPS, cash flow, etc, and include the corresponding values "
            "wherever available. Use the format below:\n"
            '{\n "metrics": [\n   {"name": "Revenue", "values": [value1, value2, ... ]},\n   {"name": "Profit", "values": [value1, value2, ... ]},\n   {"name": "Expenses", "values": [value1, value2, ... ]},\n   {"name": "EPS", "values": [value1, value2, ... ]},\n   {"name": "Cash Flow", "values": [value1, value2, ... ]}\n ]\n}\n\n'
            + file_content
        )

        else:
            return "Invalid analysis type."

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return None

def read_file(file):
    """Read content from uploaded file and return as text."""
    file_content = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            file_content += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for paragraph in doc.paragraphs:
            file_content += paragraph.text + "\n"
    else:
        st.error("Unsupported file format. Please upload a PDF or Word document.")
    return file_content

def google_search_stock(ticker):
    """Perform a Google search for the given stock ticker."""
    try:
        search_query = f"latest news and analysis for {ticker} stock"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(search_url, headers=headers)
        response.raise_for_status() # Raise exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        search_results = []
        for result in soup.find_all('div', class_='g'):
             link = result.find('a')
             if link:
               search_results.append(link['href'])

        return search_results

    except requests.exceptions.RequestException as e:
        st.error(f"Error during Google search: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during Google search: {e}")
        return None


def create_google_doc(docs_service, title, content):
    """Creates a new Google Doc and returns its ID."""
    try:
        document = docs_service.documents().create(body={'title': title}).execute()
        doc_id = document.get('documentId')
        requests = [{'insertText': {'location': {'index': 1}, 'text': content}}]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        return doc_id
    except Exception as e:
        st.error(f"Error creating Google Doc: {e}")
        return None

def save_to_google_drive(drive_service, doc_id, title, folder_id=None):
    """Saves the Google Doc to Google Drive."""
    try:
      file_metadata = {
          'name': title,
          'mimeType': 'application/vnd.google-apps.document'
      }
      if folder_id:
          file_metadata['parents'] = [folder_id]
      else:
        file_metadata['parents'] = ['root']  # Save to root if no folder ID

      file = drive_service.files().copy(fileId=doc_id, body=file_metadata).execute()
      return file.get('id')
    except Exception as e:
        st.error(f"Error saving file to Google Drive: {e}")
        return None

def list_google_drive_folders(drive_service):
    """Lists folders in Google Drive for selection."""
    try:
      results = drive_service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
      folders = results.get('files', [])
      return folders
    except Exception as e:
      st.error(f"Error listing Google Drive folders: {e}")
      return []

def display_analysis_results(analysis_result, analysis_type):
    """Display analysis results in a simple way."""
    if analysis_result:
        st.subheader("Analysis Results")
        st.write(analysis_result)
    else:
        st.error("Failed to generate analysis.")



def fetch_and_combine_url_content(urls):
  """Fetches content from URLs and combines it."""
  combined_content = ""
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
  if urls:
    for url in urls:
        try:
            response = requests.get(url,headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from relevant tags (customize as needed)
            text_content = ' '.join([p.text for p in soup.find_all(['p','h1','h2','h3','h4','h5','h6'])])
            combined_content += text_content + "\n"
        except requests.exceptions.RequestException as e:
            st.warning(f"Error fetching content from {url}: {e}")
        except Exception as e:
            st.warning(f"Error parsing content from {url}: {e}")
  return combined_content



def main():
    st.title("Financial Document & Stock Analyzer")
    st.write(
        "Upload a financial document (PDF or Word) to get an analysis of the company's performance,"
        " and search for recent news about the company."
    )

    # Get ticker symbol input
    ticker_symbol = st.text_input("Enter the stock ticker symbol (e.g., AAPL):").upper()
    
    # Upload file
    uploaded_file = st.file_uploader("Choose a financial document", type=["pdf", "docx"])
    
    #Analysis type selection
    analysis_type = st.selectbox("Select analysis type:", ["financial", "swot", "summary", "chart"])
    # Search Analysis Type
    search_analysis_type = st.selectbox("Select search analysis type:", ["financial", "swot", "summary"])


    # Google Drive and Docs services
    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    if credentials_file:
      drive_service, docs_service = get_google_services(credentials_file)
      st.success("Google services initialized.")
    
    if ticker_symbol and uploaded_file:
       with st.spinner("Processing..."):
         file_content = read_file(uploaded_file)
         if file_content:
            st.write("Analyzing financial document...")
            analysis_result = analyze_document(file_content,analysis_type)
            display_analysis_results(analysis_result, analysis_type)


         st.write("Searching for recent news about the company...")
         search_results = google_search_stock(ticker_symbol)
         if search_results:
            st.write("Fetching and Analyzing search results")
            combined_search_content = fetch_and_combine_url_content(search_results)
            if combined_search_content:
              search_analysis_result = analyze_document(combined_search_content, search_analysis_type)
              display_analysis_results(search_analysis_result,search_analysis_type)
            else:
              st.error("Could not fetch content from the URL's")
         else:
           st.error("Failed to generate search results. Please try again.")
    elif ticker_symbol or uploaded_file:
       st.warning("Please upload a financial document and enter the stock ticker symbol")

    if credentials_file and ticker_symbol and uploaded_file:

        if analysis_result or (search_results and search_analysis_result):
          # Folder Selection
          st.subheader("Choose Google Drive Folder:")
          folders = list_google_drive_folders(drive_service)
          folder_options = {folder['name']: folder['id'] for folder in folders}
          folder_options['root'] = None
          selected_folder = st.selectbox("Select a folder or use root:", options=list(folder_options.keys()))
          selected_folder_id = folder_options[selected_folder]

          # Save to Google Docs and Drive
          now = datetime.datetime.now()
          timestamp = now.strftime("%Y%m%d%H%M%S")

          if analysis_result:
              analysis_doc_title = f"{ticker_symbol}_{analysis_type.capitalize()}_Analysis_{timestamp}"
              analysis_doc_id = create_google_doc(docs_service, analysis_doc_title, analysis_result)
              if analysis_doc_id:
                analysis_drive_file_id = save_to_google_drive(drive_service, analysis_doc_id, analysis_doc_title, selected_folder_id)
                if analysis_drive_file_id:
                    st.success(f" {analysis_type.capitalize()} Analysis saved to Google Drive with file ID: {analysis_drive_file_id} to folder {selected_folder}")
                else:
                    st.error(f"Failed to save {analysis_type.capitalize()} analysis to Google Drive.")
              else:
                  st.error(f"Failed to create {analysis_type.capitalize()} analysis Google Doc.")

          if search_results and search_analysis_result:
             search_doc_title = f"{ticker_symbol}_News_{search_analysis_type}_{timestamp}"
             search_doc_id = create_google_doc(docs_service,search_doc_title, search_analysis_result)
             if search_doc_id:
               search_drive_file_id = save_to_google_drive(drive_service,search_doc_id,search_doc_title, selected_folder_id)
               if search_drive_file_id:
                 st.success(f"Google search results saved to Google Drive with file ID: {search_drive_file_id} to folder {selected_folder}")
               else:
                 st.error("Failed to save search results to Google Drive.")
             else:
                st.error("Failed to create search results Google Doc.")
        else:
             st.warning("No results to save to Google Drive.")

    elif credentials_file and not (ticker_symbol and uploaded_file):
        st.warning("Google services available, upload financial document and ticker symbol for Drive saving.")
    
    elif not credentials_file:
        st.warning("Google credentials file not set. Add the file path to your .env file for Drive saving.")


if __name__ == "__main__":
    main()