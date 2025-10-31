"""
RAG (Retrieval Augmented Generation) system for nephrology reference materials
"""
import os
import pdfplumber
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict
import math
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from logger import system_logger


class RAGSystem:
    """RAG system for processing and querying nephrology reference materials"""
    
    def __init__(self, pdf_path: str, collection_name: str = "nephrology_knowledge"):
        self.pdf_path = pdf_path
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = None
        # Simple LRU cache for query -> formatted context
        self._query_cache: OrderedDict[str, str] = OrderedDict()
        self._max_cache_size: int = 128
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or retrieve ChromaDB collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            system_logger.logger.info(f"Loaded existing collection: {self.collection_name}")
            # Ensure collection is populated; if empty, process the PDF
            try:
                if self.collection.count() == 0 and os.path.exists(self.pdf_path):
                    system_logger.logger.info("Collection is empty. Processing PDF to populate ChromaDB...")
                    self.process_pdf()
            except Exception as e:
                system_logger.log_error("RAGSystem", e, "Checking/processing empty collection")
        except:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Nephrology reference knowledge base"}
            )
            system_logger.logger.info(f"Created new collection: {self.collection_name}")
            # Process PDF if collection is new
            if os.path.exists(self.pdf_path):
                self.process_pdf()
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF file"""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        text_content = []
        system_logger.logger.info(f"Processing PDF: {self.pdf_path}")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {page_num} ---\n{text}")
                        if page_num % 50 == 0:
                            system_logger.logger.info(f"Processed {page_num} pages...")
            
            full_text = "\n\n".join(text_content)
            system_logger.logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
        
        except Exception as e:
            system_logger.log_error("RAGSystem", e, "Extracting text from PDF")
            raise
    
    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into chunks with metadata"""
        chunks = self.text_splitter.split_text(text)
        
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_docs.append({
                "text": chunk,
                "chunk_id": i,
                "source": os.path.basename(self.pdf_path)
            })
        
        system_logger.logger.info(f"Created {len(chunk_docs)} text chunks")
        return chunk_docs
    
    def process_pdf(self):
        """Process PDF and create vector embeddings"""
        if self.collection.count() > 0:
            system_logger.logger.info("Collection already has data. Skipping PDF processing.")
            return
        
        system_logger.logger.info("Starting PDF processing...")
        
        # Extract text
        full_text = self.extract_text_from_pdf()
        
        # Chunk text
        chunks = self.chunk_text(full_text)
        
        # Prepare data lists
        texts = [chunk["text"] for chunk in chunks]
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in chunks]
        metadatas = [
            {
                "source": chunk["source"],
                "chunk_id": str(chunk["chunk_id"]) 
            }
            for chunk in chunks
        ]

        # Batch settings to avoid ChromaDB max batch size errors
        add_batch_size = 1000  # well below typical Chroma limits
        encode_batch_size = 64  # embedding model mini-batch size

        total = len(texts)
        added = 0
        for start in range(0, total, add_batch_size):
            end = min(start + add_batch_size, total)
            batch_texts = texts[start:end]
            batch_ids = ids[start:end]
            batch_metadatas = metadatas[start:end]

            # Encode embeddings in sub-batches for memory efficiency
            batch_embeddings: list = []
            for e_start in range(0, len(batch_texts), encode_batch_size):
                e_end = min(e_start + encode_batch_size, len(batch_texts))
                sub_texts = batch_texts[e_start:e_end]
                sub_embeds = self.embedding_model.encode(
                    sub_texts,
                    batch_size=encode_batch_size,
                    show_progress_bar=False
                )
                batch_embeddings.extend(sub_embeds.tolist())

            # Add to collection
            self.collection.add(
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            added += (end - start)
            system_logger.logger.info(f"Added {added}/{total} chunks to ChromaDB collection...")

        system_logger.logger.info(f"Completed adding {total} chunks to ChromaDB collection")
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant chunks from knowledge base"""
        try:
            # Generate query embedding
            query_embedding_list = self.embedding_model.encode([query])[0].tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding_list],
                n_results=n_results
            )
            
            # Format results
            retrieved_chunks = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    chunk_info = {
                        "text": doc,
                        "source": results['metadatas'][0][i].get('source', 'Unknown'),
                        "chunk_id": results['metadatas'][0][i].get('chunk_id', 'Unknown'),
                        "distance": results['distances'][0][i] if results.get('distances') else None
                    }
                    retrieved_chunks.append(chunk_info)

            # Secondary rerank using cosine similarity within Python (more stable across backends)
            if retrieved_chunks:
                # Encode chunk texts in small batches for efficiency
                texts = [c["text"] for c in retrieved_chunks]
                embed_batch_size = 64
                chunk_embeds: List[List[float]] = []
                for s in range(0, len(texts), embed_batch_size):
                    e = min(s + embed_batch_size, len(texts))
                    sub = texts[s:e]
                    sub_emb = self.embedding_model.encode(sub, batch_size=embed_batch_size, show_progress_bar=False)
                    chunk_embeds.extend([v.tolist() for v in sub_emb])

                def cosine(a: List[float], b: List[float]) -> float:
                    dot = sum(x*y for x, y in zip(a, b))
                    na = math.sqrt(sum(x*x for x in a))
                    nb = math.sqrt(sum(y*y for y in b))
                    if na == 0 or nb == 0:
                        return 0.0
                    return dot / (na * nb)

                scores = [cosine(chunk_embeds[i], query_embedding_list) for i in range(len(retrieved_chunks))]
                # Attach scores and sort
                for i, sc in enumerate(scores):
                    retrieved_chunks[i]["score"] = sc
                retrieved_chunks.sort(key=lambda c: c.get("score", 0.0), reverse=True)
            
            system_logger.log_rag_retrieval(
                query,
                len(retrieved_chunks),
                [chunk["source"] for chunk in retrieved_chunks]
            )
            
            return retrieved_chunks
        
        except Exception as e:
            system_logger.log_error("RAGSystem", e, f"Retrieving chunks for query: {query}")
            return []
    
    def format_context_for_llm(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks as context for LLM"""
        if not chunks:
            return "No relevant information found in reference materials."
        
        context = "Reference Material Citations:\n\n"
        for i, chunk in enumerate(chunks, 1):
            context += f"[Source {i}: {chunk.get('source', 'Nephrology Reference')}]\n"
            context += f"{chunk['text']}\n\n"
        
        return context
    
    def get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """Get formatted context for a query with simple LRU caching"""
        # Return from cache if available
        cached = self._query_cache.get(query)
        if cached is not None:
            # Move to end (recently used)
            self._query_cache.move_to_end(query)
            return cached

        chunks = self.retrieve_relevant_chunks(query, n_results)
        formatted = self.format_context_for_llm(chunks)
        
        # Update cache with eviction policy
        self._query_cache[query] = formatted
        if len(self._query_cache) > self._max_cache_size:
            self._query_cache.popitem(last=False)
        return formatted


if __name__ == "__main__":
    # Test RAG system
    pdf_path = "data/comprehensive-clinical-nephrology.pdf"
    if os.path.exists(pdf_path):
        rag = RAGSystem(pdf_path)
        print("RAG system initialized successfully!")
        
        # Test query
        test_query = "What is chronic kidney disease?"
        print(f"\nTesting query: {test_query}")
        context = rag.get_relevant_context(test_query)
        print(f"\nRetrieved context:\n{context[:500]}...")
    else:
        print(f"PDF file not found at {pdf_path}")

