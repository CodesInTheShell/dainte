# retriever.py
from langchain.vectorstores import SimpleVectorStore

class VectorStoreRetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query):
        return self.vectorstore.similarity_search(query, k=5)

def create_retriever(index):
    retriever = VectorStoreRetriever(vectorstore=index)
    return retriever

def retrieve_documents(retriever, query):
    results = retriever.retrieve(query)
    return results

if __name__ == "__main__":
    from indexer import main as index_main
    index = index_main("pdfs")
    retriever = create_retriever(index)
    query = "Your query here"
    results = retrieve_documents(retriever, query)
    for result in results:
        print(result)
