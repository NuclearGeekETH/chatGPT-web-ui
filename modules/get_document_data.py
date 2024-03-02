import fitz  # PyMuPDF
from docx import Document
import pandas as pd

def load_document_into_memory(file_path):
    """
    Loads an Excel file into memory using pandas.

    Parameters:
    file_path (str): The path to the Excel file to be loaded.

    Returns:
    pandas.DataFrame: A DataFrame containing the contents of the Excel file.
    """
    try:
        if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
            # Load the Excel file into a pandas DataFrame
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Returning the DataFrame
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