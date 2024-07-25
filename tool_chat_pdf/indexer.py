# indexer.py
import os
from PyPDF2 import PdfFileReader

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf = PdfFileReader(file)
        for page_num in range(pdf.getNumPages()):
            page = pdf.getPage(page_num)
            text += page.extract_text()
    return text

def index_pdfs(pdf_folder):
    documents = []
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            path = os.path.join(pdf_folder, filename)
            text = extract_text_from_pdf(path)
            documents.append({"text": text, "filename": filename})
    return documents

def create_index(documents):
    from langchain.vectorstores import SimpleVectorStore
    from langchain.embeddings import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings()
    store = SimpleVectorStore()
    for doc in documents:
        store.add_text(doc["text"], embeddings)
    return store

def main(pdf_folder):
    documents = index_pdfs(pdf_folder)
    index = create_index(documents)
    return index

if __name__ == "__main__":
    pdf_folder = "pdfs"
    index = main(pdf_folder)
    print("Indexing completed.")
