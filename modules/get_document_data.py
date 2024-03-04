import fitz  # PyMuPDF
import requests
import pandas as pd
from docx import Document
from bs4 import BeautifulSoup

def load_document_into_memory(file_path):
    try:
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            # Load the Excel file into a pandas DataFrame
            df = pd.read_excel(file_path, engine='openpyxl')
            return df
        
        if file_path.endswith('.csv'):
            # Load the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            return df

        if file_path.endswith('.pdf'):
            text_content = ""
            # Open the PDF file
            doc = fitz.open(file_path)
            for page in doc:
                # Concatenating text from each page
                text_content += page.get_text() + "\n"
            doc.close()
            return text_content

        if file_path.endswith('.docx'):
            # Load the Word document
            doc = Document(file_path)
            text_content = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ''])
            return text_content
        
        else:
            return "Unsupported file type or handling not implemented."
        
    except Exception as e:
        # Handling potential errors, such as file not found or wrong format
        return f"An error occurred: {e}"
    
def get_website_data(url):
    try:
        # Send a HTTP request to the provided URL
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the request returned an unsuccessful status code.

        # Extract text content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Removing script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and handle whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {e}")
    except Exception as e:
        print(f"Some other error occurred: {e}")