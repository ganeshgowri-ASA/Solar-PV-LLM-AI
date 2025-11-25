"""Vector-based semantic retrieval using similarity search."""
from typing import List, Optional, Union
import numpy as np
from pathlib import Path
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer

from ..utils.data_models import Document, RetrievalResult

logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    Vector-based retriever using similarity search.

    Supports ChromaDB and FAISS as backend vector stores.
    """

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        store_type: str = "chromadb",
        store_path: Optional[Union[str, Path]] = None,
        collection_name: str = "documents",
    ):
        """
        Initialize vector retriever.

        Args:
            embedding_model: Name of sentence-transformers model
            store_type: Type of vector store ("chromadb" or "faiss")
            store_path: Path to store vector database
            collection_name: Name of the collection/index
        """
        self.embedding_model_name = embedding_model
        self.store_type = store_type
        self.store_path = Path(store_path) if store_path else Path("./data/vector_store")
        self.collection_name = collection_name

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)

        # Initialize vector store
        self.store = None
        self.collection = None
        self._init_vector_store()

    def _init_vector_store(self):
        """Initialize the vector store backend."""
        self.store_path.mkdir(parents=True, exist_ok=True)

        if self.store_type == "chromadb":
            if not CHROMADB_AVAILABLE:
                raise ImportError("chromadb is not installed. Install with: pip install chromadb")

            logger.info(f"Initializing ChromaDB at {self.store_path}")
            self.store = chromadb.PersistentClient(
                path=str(self.store_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.store.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

        elif self.store_type == "faiss":
            if not FAISS_AVAILABLE:
                raise ImportError("faiss is not installed. Install with: pip install faiss-cpu")

            logger.info(f"Initializing FAISS at {self.store_path}")
            # FAISS index will be loaded/created when documents are added
            self.index_path = self.store_path / f"{self.collection_name}.faiss"
            self.metadata_path = self.store_path / f"{self.collection_name}_metadata.npy"

            if self.index_path.exists():
                self.store = faiss.read_index(str(self.index_path))
                self.documents = list(np.load(str(self.metadata_path), allow_pickle=True))
            else:
                self.store = None
                self.documents = []

        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects to add
        """
        if not documents:
            return

        logger.info(f"Adding {len(documents)} documents to vector store")

        # Generate embeddings
        texts = [doc.content for doc in documents]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)

        if self.store_type == "chromadb":
            # Add to ChromaDB
            self.collection.add(
                ids=[doc.id for doc in documents],
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=[doc.metadata for doc in documents],
            )

        elif self.store_type == "faiss":
            # Add to FAISS
            embeddings = embeddings.astype('float32')

            if self.store is None:
                # Create new index
                dimension = embeddings.shape[1]
                self.store = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.store.add(embeddings)
            self.documents.extend(documents)

            # Save index and metadata
            faiss.write_index(self.store, str(self.index_path))
            np.save(str(self.metadata_path), np.array(self.documents, dtype=object))

        logger.info(f"Successfully added {len(documents)} documents")

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[dict] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k most similar documents for a query.

        Args:
            query: Query text
            top_k: Number of documents to retrieve
            filter_metadata: Optional metadata filters (ChromaDB only)

        Returns:
            List of RetrievalResult objects
        """
        logger.info(f"Retrieving top-{top_k} documents for query: {query[:100]}...")

        # Generate query embedding
        query_embedding = self.encoder.encode([query])[0]

        if self.store_type == "chromadb":
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=filter_metadata,
            )

            # Format results
            retrieval_results = []
            for i in range(len(results['ids'][0])):
                doc = Document(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                )
                score = float(results['distances'][0][i]) if results.get('distances') else 1.0
                # ChromaDB returns distance, convert to similarity (1 - distance for cosine)
                similarity = 1.0 - score if score <= 1.0 else 1.0 / (1.0 + score)

                retrieval_results.append(
                    RetrievalResult(
                        document=doc,
                        score=similarity,
                        rank=i + 1,
                        retrieval_method="vector_similarity"
                    )
                )

        elif self.store_type == "faiss":
            if self.store is None or self.store.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []

            # Query FAISS
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            faiss.normalize_L2(query_embedding)

            scores, indices = self.store.search(query_embedding, min(top_k, self.store.ntotal))

            # Format results
            retrieval_results = []
            for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue

                doc = self.documents[idx]
                retrieval_results.append(
                    RetrievalResult(
                        document=doc,
                        score=float(score),
                        rank=i + 1,
                        retrieval_method="vector_similarity"
                    )
                )

        logger.info(f"Retrieved {len(retrieval_results)} documents")
        return retrieval_results

    def get_document_count(self) -> int:
        """Get total number of documents in the vector store."""
        if self.store_type == "chromadb":
            return self.collection.count()
        elif self.store_type == "faiss":
            return self.store.ntotal if self.store else 0
        return 0
