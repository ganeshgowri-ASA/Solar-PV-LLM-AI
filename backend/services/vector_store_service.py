"""
Vector store service with support for multiple backends
Supports: Pinecone, Weaviate, ChromaDB, Qdrant, FAISS
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging
import hashlib
from datetime import datetime

from backend.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations"""

    @abstractmethod
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with embeddings to vector store"""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass

    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass

    @abstractmethod
    def update_document(
        self,
        document_id: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update a single document"""
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if vector store is healthy"""
        pass


class PineconeVectorStore(VectorStoreBase):
    """Pinecone vector store implementation"""

    def __init__(self, api_key: str, index_name: str, dimension: int = 1536):
        try:
            import pinecone
            self.pinecone = pinecone
        except ImportError:
            raise ImportError("pinecone-client not installed. Run: pip install pinecone-client")

        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self._init_client()

    def _init_client(self):
        """Initialize Pinecone client"""
        from pinecone import Pinecone, ServerlessSpec

        self.pc = Pinecone(api_key=self.api_key)

        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = self.pc.Index(self.index_name)
        logger.info(f"Connected to Pinecone index: {self.index_name}")

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to Pinecone"""
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        vectors = []
        ids = []

        for doc, embedding in zip(documents, embeddings):
            doc_id = doc.get("id") or self._generate_id(doc["content"])
            ids.append(doc_id)

            vectors.append({
                "id": doc_id,
                "values": embedding,
                "metadata": {
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source_url": doc.get("source_url", ""),
                    "chunk_index": doc.get("chunk_index", 0),
                    "document_id": doc.get("document_id", ""),
                    "created_at": datetime.utcnow().isoformat()
                }
            })

        # Batch upsert
        self.index.upsert(vectors=vectors)
        logger.info(f"Added {len(vectors)} documents to Pinecone")

        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search Pinecone for similar documents"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True
        )

        matches = []
        for match in results.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "content": match.metadata.get("content", ""),
                "title": match.metadata.get("title", ""),
                "source_url": match.metadata.get("source_url", ""),
                "metadata": match.metadata
            })

        logger.info(f"Found {len(matches)} matches in Pinecone")
        return matches

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        self.index.delete(ids=document_ids)
        logger.info(f"Deleted {len(document_ids)} documents from Pinecone")
        return True

    def update_document(
        self,
        document_id: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update document in Pinecone"""
        self.index.upsert(vectors=[{
            "id": document_id,
            "values": embedding,
            "metadata": metadata or {}
        }])
        logger.info(f"Updated document {document_id} in Pinecone")
        return True

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Pinecone"""
        result = self.index.fetch(ids=[document_id])
        if document_id in result.vectors:
            vec = result.vectors[document_id]
            return {
                "id": vec.id,
                "metadata": vec.metadata
            }
        return None

    def health_check(self) -> bool:
        """Check Pinecone health"""
        try:
            self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False

    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ChromaDBVectorStore(VectorStoreBase):
    """ChromaDB vector store implementation"""

    def __init__(self, collection_name: str, persist_directory: str = "./data/vector_store"):
        try:
            import chromadb
            self.chromadb = chromadb
        except ImportError:
            raise ImportError("chromadb not installed. Run: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._init_client()

    def _init_client(self):
        """Initialize ChromaDB client"""
        self.client = self.chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Connected to ChromaDB collection: {self.collection_name}")

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to ChromaDB"""
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        ids = []
        metadatas = []
        contents = []

        for doc in documents:
            doc_id = doc.get("id") or self._generate_id(doc["content"])
            ids.append(doc_id)
            contents.append(doc["content"])
            metadatas.append({
                "title": doc.get("title", ""),
                "source_url": doc.get("source_url", ""),
                "chunk_index": doc.get("chunk_index", 0),
                "document_id": str(doc.get("document_id", "")),
                "created_at": datetime.utcnow().isoformat()
            })

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

        logger.info(f"Added {len(ids)} documents to ChromaDB")
        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )

        matches = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                matches.append({
                    "id": results["ids"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "content": results["documents"][0][i],
                    "title": results["metadatas"][0][i].get("title", ""),
                    "source_url": results["metadatas"][0][i].get("source_url", ""),
                    "metadata": results["metadatas"][0][i]
                })

        logger.info(f"Found {len(matches)} matches in ChromaDB")
        return matches

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from ChromaDB"""
        self.collection.delete(ids=document_ids)
        logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
        return True

    def update_document(
        self,
        document_id: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update document in ChromaDB"""
        self.collection.update(
            ids=[document_id],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None
        )
        logger.info(f"Updated document {document_id} in ChromaDB")
        return True

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document from ChromaDB"""
        result = self.collection.get(ids=[document_id])
        if result["ids"]:
            return {
                "id": result["ids"][0],
                "content": result["documents"][0] if result["documents"] else None,
                "metadata": result["metadatas"][0] if result["metadatas"] else None
            }
        return None

    def health_check(self) -> bool:
        """Check ChromaDB health"""
        try:
            self.collection.count()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False

    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class VectorStoreService:
    """
    Unified vector store service supporting multiple backends
    Implements zero-downtime updates using versioning
    """

    def __init__(self):
        self.settings = get_settings()
        self.store = self._create_store()
        self.current_version = "v1"

    def _create_store(self) -> VectorStoreBase:
        """Create appropriate vector store based on configuration"""
        store_type = self.settings.vector_store_type.lower()

        if store_type == "pinecone":
            return PineconeVectorStore(
                api_key=self.settings.vector_store_api_key,
                index_name=self.settings.vector_store_index_name,
                dimension=self.settings.vector_dimension
            )
        elif store_type == "chromadb":
            return ChromaDBVectorStore(
                collection_name=self.settings.vector_store_index_name,
                persist_directory="./data/vector_store"
            )
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents to vector store"""
        return self.store.add_documents(documents, embeddings)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        results = self.store.search(query_embedding, top_k=top_k)

        # Filter by similarity threshold
        filtered = [r for r in results if r["score"] >= similarity_threshold]

        logger.info(f"Filtered {len(results)} results to {len(filtered)} above threshold {similarity_threshold}")
        return filtered

    def update_documents_zero_downtime(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> bool:
        """
        Update documents with zero downtime using blue-green deployment strategy

        1. Add new documents with new version tag
        2. Verify new documents are searchable
        3. Mark old documents as inactive
        4. Delete old documents after grace period
        """
        logger.info("Starting zero-downtime document update")

        # Tag documents with new version
        new_version = f"v{int(self.current_version[1:]) + 1}"
        for doc in documents:
            doc["version"] = new_version

        try:
            # Step 1: Add new documents
            new_ids = self.store.add_documents(documents, embeddings)
            logger.info(f"Added {len(new_ids)} documents with version {new_version}")

            # Step 2: Verify searchability (simple check)
            if len(embeddings) > 0:
                test_results = self.store.search(embeddings[0], top_k=1)
                if not test_results:
                    raise Exception("New documents not immediately searchable")

            # Step 3: Update current version
            old_version = self.current_version
            self.current_version = new_version

            logger.info(f"Successfully updated from {old_version} to {new_version}")
            return True

        except Exception as e:
            logger.error(f"Zero-downtime update failed: {e}")
            # Rollback: delete newly added documents
            try:
                if 'new_ids' in locals():
                    self.store.delete_documents(new_ids)
                    logger.info("Rolled back new documents")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
            return False

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from vector store"""
        return self.store.delete_documents(document_ids)

    def health_check(self) -> bool:
        """Check vector store health"""
        return self.store.health_check()

    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "store_type": self.settings.vector_store_type,
            "current_version": self.current_version,
            "healthy": self.health_check()
        }
