#Financial Document & Stock Analyzer

## Overview
The **Financial Document & Stock Analyzer** is a powerful Streamlit-based application that allows users to upload financial documents, perform detailed analyses using the Gemini API, and search for recent news about a company's stock. With integration into Google Drive and Docs, the app provides seamless saving and sharing capabilities for analyzed content.

---

## Features
1. **Document Upload and Analysis**:
   - Supports PDF and Word documents.
   - Analyzes financial performance, SWOT analysis, summaries, and charts using the Gemini API.

2. **Stock News Search**:
   - Fetches recent news and analysis for a given stock ticker using Google search.

3. **Google Integration**:
   - Creates Google Docs from analyzed content.
   - Saves documents to Google Drive, including support for selecting specific folders.

4. **Data Visualization**:
   - Extracts numerical data and plots financial metrics using Plotly.

5. **Customizable Analysis**:
   - Offers multiple analysis types, including financial performance, SWOT, summaries, and chart data extraction.

---

## Prerequisites
1. **Python Libraries**:
   - `streamlit`
   - `google.generativeai`
   - `googleapiclient`
   - `PyPDF2`
   - `docx`
   - `dotenv`
   - `requests`
   - `bs4` (BeautifulSoup)
   - `pandas`
   - `plotly`

2. **API Credentials**:
   - Gemini API Key: Store in a `.env` file as `GENAI_API_KEY`.
   - Google Service Account Credentials: Provide a credentials file path in the `.env` file as `GOOGLE_CREDENTIALS_FILE`.

3. **Environment Variables**:
   - `.env` file with:
     ```
     GENAI_API_KEY=your_gemini_api_key
     GOOGLE_CREDENTIALS_FILE=/path/to/your/credentials.json
     ```

4. **Google API Scopes**:
   - Enable the following Google APIs:
     - Google Drive API
     - Google Docs API

---

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/financial-doc-analyzer.git
   cd financial-doc-analyzer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add API Keys**:
   - Create a `.env` file and add your Gemini API key and Google credentials file path:
     ```env
     GENAI_API_KEY=your_gemini_api_key
     GOOGLE_CREDENTIALS_FILE=/path/to/your/credentials.json
     ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

---

## Usage
1. **Upload a Document**:
   - Select a financial document (PDF or Word) and upload it.

2. **Choose Analysis Type**:
   - Select from `financial`, `swot`, `summary`, or `chart` for detailed insights.

3. **Search for Stock News**:
   - Enter a stock ticker symbol (e.g., AAPL) to fetch relevant news and articles.

4. **Save and Share**:
   - Optionally save analyzed content to Google Drive or create Google Docs.

---

## Error Handling
- **Missing API Key**: Ensure `GENAI_API_KEY` is set in `.env`.
- **Invalid File Format**: Only PDF and Word files are supported.
- **Google API Errors**: Verify the credentials file and ensure API access is enabled.
- **Network Errors**: Check internet connectivity for Google and Gemini API access.

---

## Future Enhancements
- Add support for additional file formats.
- Improve visualization with interactive dashboards.
- Integrate machine learning for predictive financial analysis.

---

## License
This project is licensed under the MIT License.

---

## Author
**Your Name**  
For questions or suggestions, contact: [your-email@example.com]
