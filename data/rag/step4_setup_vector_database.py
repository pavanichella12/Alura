#!/usr/bin/env python3
"""
Step 4: Set up Vector Database for Misogyny Detection RAG
Using ChromaDB - the easiest and most beginner-friendly option
"""

import pandas as pd
import numpy as np
import chromadb
import pickle
import logging
import time
from typing import List, Dict, Any
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabaseSetup:
    def __init__(self, db_name="misogyny_detection_db"):
        """
        Initialize the vector database setup
        ChromaDB is the easiest option for beginners
        """
        logger.info("🗄️ Setting up Vector Database...")
        logger.info("📦 Using ChromaDB (easiest for beginners)")
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.Client()
            self.db_name = db_name
            self.collection_name = "misogyny_chunks"
            
            logger.info("✅ ChromaDB client initialized successfully!")
            logger.info(f"📊 Database name: {db_name}")
            logger.info(f"📚 Collection name: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing ChromaDB: {str(e)}")
            raise
    
    def load_embeddings_data(self, filename='embeddings_data.pkl'):
        """Load the embeddings data"""
        logger.info(f"📖 Loading embeddings from {filename}...")
        
        try:
            with open(filename, 'rb') as f:
                df = pickle.load(f)
            
            logger.info(f"✅ Loaded {len(df)} embeddings")
            logger.info(f"📊 Sample data:")
            logger.info(f"   - Columns: {list(df.columns)}")
            logger.info(f"   - First text: {df['text'].iloc[0][:50]}...")
            
            return df
        except Exception as e:
            logger.error(f"❌ Error loading embeddings: {str(e)}")
            return None
    
    def create_collection(self):
        """Create a new collection in ChromaDB"""
        logger.info(f"📚 Creating collection: {self.collection_name}")
        
        try:
            # Create or get collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Misogyny detection chunks with embeddings"}
            )
            
            logger.info("✅ Collection created successfully!")
            logger.info(f"📊 Collection info:")
            logger.info(f"   - Name: {self.collection.name}")
            logger.info(f"   - Count: {self.collection.count()}")
            
            return self.collection
            
        except Exception as e:
            logger.error(f"❌ Error creating collection: {str(e)}")
            # Try to get existing collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info("✅ Using existing collection")
                return self.collection
            except:
                raise
    
    def prepare_data_for_chromadb(self, df, batch_size=1000):
        """
        Prepare data for ChromaDB insertion
        ChromaDB needs: ids, embeddings, documents, metadatas
        """
        logger.info("🔄 Preparing data for ChromaDB...")
        
        # Prepare data in batches
        all_ids = []
        all_embeddings = []
        all_documents = []
        all_metadatas = []
        
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches}")
            
            # Prepare batch data
            batch_ids = [f"chunk_{idx}" for idx in batch_df.index]
            batch_embeddings = batch_df['embedding'].tolist()
            batch_documents = batch_df['text'].tolist()
            batch_metadatas = []
            
            for _, row in batch_df.iterrows():
                # Handle NaN values in label column
                label_value = row['label']
                if pd.isna(label_value):
                    label_value = 0  # Default to non-misogyny if NaN
                
                metadata = {
                    'label': int(label_value),
                    'source': str(row['source']),
                    'category': str(row.get('category', 'unknown')),
                    'chunk_length': int(row.get('chunk_length', 0)),
                    'is_misogyny': int(label_value)
                }
                batch_metadatas.append(metadata)
            
            # Add to main lists
            all_ids.extend(batch_ids)
            all_embeddings.extend(batch_embeddings)
            all_documents.extend(batch_documents)
            all_metadatas.extend(batch_metadatas)
            
            if batch_num % 10 == 0:
                logger.info(f"   ✅ Completed {batch_num}/{total_batches} batches")
        
        logger.info(f"✅ Prepared {len(all_ids)} items for ChromaDB")
        
        return {
            'ids': all_ids,
            'embeddings': all_embeddings,
            'documents': all_documents,
            'metadatas': all_metadatas
        }
    
    def insert_data_into_chromadb(self, data):
        """Insert data into ChromaDB collection"""
        logger.info("💾 Inserting data into ChromaDB...")
        
        try:
            # Insert data in batches to avoid memory issues
            batch_size = 1000
            total_items = len(data['ids'])
            total_batches = (total_items + batch_size - 1) // batch_size
            
            for i in range(0, total_items, batch_size):
                batch_num = (i // batch_size) + 1
                
                # Get batch data
                batch_ids = data['ids'][i:i + batch_size]
                batch_embeddings = data['embeddings'][i:i + batch_size]
                batch_documents = data['documents'][i:i + batch_size]
                batch_metadatas = data['metadatas'][i:i + batch_size]
                
                logger.info(f"📦 Inserting batch {batch_num}/{total_batches} ({len(batch_ids)} items)")
                
                # Insert batch
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                
                if batch_num % 10 == 0:
                    logger.info(f"   ✅ Completed {batch_num}/{total_batches} batches")
            
            logger.info("✅ All data inserted successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error inserting data: {str(e)}")
            raise
    
    def test_vector_search(self):
        """Test the vector database with sample queries"""
        logger.info("🧪 Testing vector search functionality...")
        
        # Sample test queries
        test_queries = [
            "Women are emotional creatures",
            "Women can't handle stress like men",
            "Women are great leaders",
            "This is a neutral statement about technology"
        ]
        
        # Create embeddings for test queries
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_embeddings = model.encode(test_queries)
        
        logger.info("🔍 Testing similarity search:")
        
        for i, (query, embedding) in enumerate(zip(test_queries, test_embeddings)):
            logger.info(f"\n📝 Test Query {i+1}: {query}")
            
            # Search for similar items
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=3,
                include=['documents', 'metadatas', 'distances']
            )
            
            logger.info(f"🔍 Top 3 similar results:")
            for j, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                logger.info(f"   {j+1}. Similarity: {1-distance:.3f}")
                logger.info(f"      Text: {doc[:80]}...")
                logger.info(f"      Label: {metadata['label']} (misogyny: {metadata['is_misogyny']})")
    
    def get_database_stats(self):
        """Get statistics about the database"""
        logger.info("📊 Database Statistics:")
        
        try:
            count = self.collection.count()
            logger.info(f"   - Total items: {count}")
            
            # Get sample items
            sample_results = self.collection.get(limit=5)
            logger.info(f"   - Sample items: {len(sample_results['ids'])}")
            
            # Count misogyny vs non-misogyny
            all_results = self.collection.get(limit=count)
            misogyny_count = sum(1 for metadata in all_results['metadatas'] 
                               if metadata.get('is_misogyny', 0) == 1)
            non_misogyny_count = count - misogyny_count
            
            logger.info(f"   - Misogyny examples: {misogyny_count}")
            logger.info(f"   - Non-misogyny examples: {non_misogyny_count}")
            logger.info(f"   - Misogyny ratio: {misogyny_count/count:.2%}")
            
            return {
                'total_items': count,
                'misogyny_count': misogyny_count,
                'non_misogyny_count': non_misogyny_count,
                'misogyny_ratio': misogyny_count/count
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return None
    
    def save_database_info(self, stats):
        """Save database information for future use"""
        logger.info("💾 Saving database information...")
        
        db_info = {
            'database_name': self.db_name,
            'collection_name': self.collection_name,
            'stats': stats,
            'setup_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('vector_database_info.json', 'w') as f:
            import json
            json.dump(db_info, f, indent=2)
        
        logger.info("✅ Database info saved to vector_database_info.json")

def demonstrate_vector_database():
    """
    Demonstrate how vector databases work with simple examples
    """
    logger.info("🎯 Vector Database Demonstration")
    logger.info("=" * 50)
    
    logger.info("📚 What is a Vector Database?")
    logger.info("   - Stores text + embeddings (numbers)")
    logger.info("   - Enables semantic similarity search")
    logger.info("   - Much faster than keyword search")
    
    logger.info("\n🔍 How Similarity Search Works:")
    logger.info("   1. User types: 'Women can't handle pressure'")
    logger.info("   2. Convert to embedding: [0.3, -0.7, 0.4, ...]")
    logger.info("   3. Find similar embeddings in database")
    logger.info("   4. Return: 'Women are emotional' (similar meaning!)")
    
    logger.info("\n⚡ Why Vector Database is Fast:")
    logger.info("   - Regular search: Check every word (slow)")
    logger.info("   - Vector search: Math on numbers (fast)")
    logger.info("   - Your 74K embeddings search in milliseconds!")

def main():
    """
    Main function - set up vector database for misogyny detection
    """
    logger.info("🎯 Step 4: Set up Vector Database for Misogyny Detection RAG")
    logger.info("=" * 70)
    
    # Demonstrate vector databases
    demonstrate_vector_database()
    
    # Create setup object
    setup = VectorDatabaseSetup()
    
    # Step 1: Load embeddings data
    df = setup.load_embeddings_data()
    if df is None:
        logger.error("❌ Could not load embeddings data. Please run Step 3 first.")
        return
    
    # Step 2: Create collection
    collection = setup.create_collection()
    
    # Step 3: Prepare data for ChromaDB
    data = setup.prepare_data_for_chromadb(df)
    
    # Step 4: Insert data into ChromaDB
    setup.insert_data_into_chromadb(data)
    
    # Step 5: Test vector search
    setup.test_vector_search()
    
    # Step 6: Get database statistics
    stats = setup.get_database_stats()
    
    # Step 7: Save database information
    setup.save_database_info(stats)
    
    # Summary
    logger.info("\n🎉 Vector Database Setup Complete!")
    logger.info("📊 What we accomplished:")
    logger.info(f"   - Created ChromaDB collection: {setup.collection_name}")
    logger.info(f"   - Inserted {stats['total_items']} embeddings")
    logger.info(f"   - Misogyny examples: {stats['misogyny_count']}")
    logger.info(f"   - Non-misogyny examples: {stats['non_misogyny_count']}")
    logger.info(f"   - Ready for similarity search!")
    
    logger.info("\n🚀 Next Step: Create the RAG Detection API")
    logger.info("This will combine everything into a working misogyny detection system")

if __name__ == "__main__":
    main() 