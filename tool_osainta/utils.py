from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def initQdrantCollection():
    client = QdrantClient("localhost", port=6333)  # Adjust the parameters based on your Qdrant setup

    collection_name = "osainta_collection"

    # Check if the collection exists
    collections = client.get_collections()
    collection_exists = any(c.name == collection_name for c in collections.collections)

    # Create the collection if it does not exist
    if not collection_exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=4, distance=Distance.DOT),
        )
        print(f"Collection '{collection_name}' created.")
    else:
        print(f"Collection '{collection_name}' already exists.")