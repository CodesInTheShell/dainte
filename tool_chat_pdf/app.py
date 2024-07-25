# main.py
import streamlit as st
from indexer import main as index_main
from retriever import create_retriever, retrieve_documents

st.title("PDF Retriever with RAG")
st.write("Upload your PDFs and query the indexed content.")

pdf_folder = "pdfs"
uploaded_files = st.file_uploader("Choose PDFs", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        with open(os.path.join(pdf_folder, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.write("Files uploaded successfully!")

    if st.button("Index PDFs"):
        with st.spinner("Indexing..."):
            index = index_main(pdf_folder)
        st.success("Indexing completed.")

    query = st.text_input("Enter your query:")
    if st.button("Retrieve"):
        with st.spinner("Retrieving..."):
            retriever = create_retriever(index)
            results = retrieve_documents(retriever, query)
        st.write("Results:")
        for result in results:
            st.write(result)
