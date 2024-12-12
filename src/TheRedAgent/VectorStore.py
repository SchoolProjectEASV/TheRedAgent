from qdrant_client import QdrantClient, models
import ollama
import logging

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.indices.vector_store import VectorStoreIndex, VectorIndexRetriever
from pathlib import Path
import hashlib
from PDFProcessor import PDFProcessor

logger = logging.getLogger(__name__)


class VectorStoreComponent:
    """Encapsulates the Qdrant Vector Store and related functionality."""

    def __init__(self, embedding_model_host="localhost", collection_name="PDFAbout"):
        self.embedding_model_host = embedding_model_host
        self.collection_name = collection_name

        self.embedding_client = ollama.Client(host=self.embedding_model_host)

        sample_embedding = self.embedding_client.embeddings(
            model="llama3.2", prompt="test"
        )["embedding"]
        self.vector_size = len(sample_embedding)
        print(f"Detected embedding size: {self.vector_size}")

        self.client = QdrantClient(path=str(Path("../../data").absolute()))
        self._initialize_collection()

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
        )

    def _initialize_collection(self):
        """Creates the Qdrant collection if it does not exist."""
        if self.collection_name not in [
            collection.name for collection in self.client.get_collections().collections
        ]:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size, distance=models.Distance.COSINE
                ),
            )
        else:
            logger.info(f"Collection '{self.collection_name}' already exists.")

    def add_text(self, text: str, doc_id: int = None):
        """Adds text to the vector store after generating embeddings, avoiding duplicates."""
        text_hash = hashlib.md5(text.encode()).hexdigest()

        existing_docs = self.list_all_documents()
        if any(doc["hash"] == text_hash for doc in existing_docs):
            logger.info(
                f"Text already exists in vector store (hash: {text_hash}). Skipping embedding."
            )
            return

        response = self.embedding_client.embeddings(model="llama3.2", prompt=text)
        embeddings = response["embedding"]

        doc_id = doc_id or int(text_hash, 16) % (10**9)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=embeddings,
                    payload={"text": text, "hash": text_hash},
                ),
            ],
        )
        logger.info(
            f"Added document ID {doc_id} with hash {text_hash} to the vector store."
        )

    def retrieve_relevant(self, query: str, limit: int = 5):
        """Retrieves relevant chunks from the vector store."""
        response = self.embedding_client.embeddings(model="llama3.2", prompt=query)
        query_vector = response["embedding"]

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )

        if not results:
            logger.info("No relevant chunks found for the query.")
            return [{"id": -1, "score": 0.0, "text": "No relevant information found."}]
        return [
            {"id": result.id, "score": result.score, "text": result.payload["text"]}
            for result in results
        ]

    def get_retriever(self, similarity_top_k: int = 5):
        """Return a retriever object for use with LlamaIndex."""
        index = VectorStoreIndex.from_vector_store(self.vector_store)
        return VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
        )

    def list_all_documents(self):
        """List all documents stored in the vector database."""
        points, _ = self.client.scroll(self.collection_name)
        return [
            {"text": point.payload["text"], "hash": point.payload.get("hash")}
            for point in points
        ]

    def close(self):
        """Closes the connection to the vector store."""
        if hasattr(self.client, "close"):
            self.client.close()
            logger.info("Closed connection to the Qdrant client.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pdf_path = "../../data/The-Complete-Guide-to-Trading.pdf"
    pdf_processor = PDFProcessor(pdf_path=pdf_path)

    full_text = pdf_processor.extract_text()
    text_chunks = pdf_processor.chunk_text(full_text)

    vector_store_component = VectorStoreComponent()

    for i, chunk in enumerate(text_chunks):
        vector_store_component.add_text(text=chunk, doc_id=i)

    query = "The best five advice to trading?"
    results = vector_store_component.retrieve_relevant(query=query)
    print("Relevant Results:")
    for result in results:
        print(result)

    all_docs = vector_store_component.list_all_documents()

    print("All Documents in the Vector Store:")
    print(all_docs)

    vector_store_component.close()
