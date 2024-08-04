import logging

### PYMONGO
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/') 
db = client['osaintadb'] 

### QDRANT
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

GEMINI_TEXT_EMBEDDING_SIZE = 768
QDRANT_EMBEDDING_COLLECTION_NAME = "osainta_collection"



def initQdrantCollection():
    client = QdrantClient("localhost", port=6333)  # Adjust the parameters based on your Qdrant setup

    # Check if the collection exists
    collections = client.get_collections()
    collection_exists = any(c.name == QDRANT_EMBEDDING_COLLECTION_NAME for c in collections.collections)

    # Create the collection if it does not exist
    if not collection_exists:
        client.create_collection(
            collection_name=QDRANT_EMBEDDING_COLLECTION_NAME,
            vectors_config=VectorParams(size=GEMINI_TEXT_EMBEDDING_SIZE, distance=Distance.DOT),
        )
        logging.info(f"QDrant Collection '{QDRANT_EMBEDDING_COLLECTION_NAME}' created.")
    else:
        logging.info(f"QDrant Collection '{QDRANT_EMBEDDING_COLLECTION_NAME}' already exists.")
    return client

q_client = initQdrantCollection()

