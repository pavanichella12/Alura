#!/usr/bin/env python3
"""
Step 3: Create Embeddings for Misogyny Detection RAG
This converts text chunks into numbers that RAG can search quickly
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import time
from typing import List, Dict, Tuple
import pickle

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedding generator
        all-MiniLM-L6-v2 is a fast, good quality model for text similarity
        """
        logger.info("🚀 Starting Embedding Generation...")
        logger.info(f"📦 Loading model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("✅ Model loaded successfully!")
            logger.info(f"📊 Model info:")
            logger.info(f"   - Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            logger.info(f"   - Max sequence length: {self.model.max_seq_length}")
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            raise
    
    def load_chunked_data(self, filename='hybrid_chunked_data.csv'):
        """Load the chunked data"""
        logger.info(f"📖 Loading chunked data from {filename}...")
        
        try:
            df = pd.read_csv(filename)
            logger.info(f"✅ Loaded {len(df)} chunks")
            logger.info(f"📊 Sample chunks:")
            for i, row in df.head(3).iterrows():
                logger.info(f"   Chunk {i+1}: {row['text'][:80]}...")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            return None
    
    def generate_embeddings(self, texts: List[str], batch_size=32):
        """
        Generate embeddings for a list of texts
        Uses batching for efficiency
        """
        logger.info(f"🧮 Generating embeddings for {len(texts)} texts...")
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_texts)} texts)")
            
            try:
                # Generate embeddings for this batch
                batch_embeddings = self.model.encode(batch_texts, convert_to_tensor=False)
                all_embeddings.extend(batch_embeddings)
                
                # Show progress
                if batch_num % 10 == 0:
                    logger.info(f"   ✅ Completed {batch_num}/{total_batches} batches")
                    
            except Exception as e:
                logger.error(f"❌ Error in batch {batch_num}: {str(e)}")
                # Add zero embeddings for failed texts
                zero_embedding = np.zeros(self.model.get_sentence_embedding_dimension())
                all_embeddings.extend([zero_embedding] * len(batch_texts))
        
        logger.info(f"✅ Generated {len(all_embeddings)} embeddings")
        return np.array(all_embeddings)
    
    def process_dataset(self, df):
        """
        Process the entire dataset and generate embeddings
        """
        logger.info("🔄 Processing dataset and generating embeddings...")
        
        # Get all texts
        texts = df['text'].tolist()
        
        # Generate embeddings
        start_time = time.time()
        embeddings = self.generate_embeddings(texts)
        end_time = time.time()
        
        logger.info(f"⏱️ Embedding generation took {end_time - start_time:.2f} seconds")
        
        # Add embeddings to dataframe
        df['embedding'] = embeddings.tolist()
        
        return df
    
    def analyze_embeddings(self, df):
        """
        Analyze the generated embeddings
        """
        logger.info("📊 Analyzing embeddings...")
        
        # Basic statistics
        embedding_dim = len(df['embedding'].iloc[0])
        total_embeddings = len(df)
        
        # Calculate some similarity examples
        sample_embeddings = df['embedding'].head(5).tolist()
        sample_texts = df['text'].head(5).tolist()
        
        logger.info(f"📈 Embedding Statistics:")
        logger.info(f"   - Total embeddings: {total_embeddings}")
        logger.info(f"   - Embedding dimension: {embedding_dim}")
        logger.info(f"   - Data type: {type(sample_embeddings[0])}")
        
        # Show similarity examples
        logger.info(f"🔍 Similarity Examples:")
        for i in range(min(3, len(sample_embeddings))):
            for j in range(i + 1, min(4, len(sample_embeddings))):
                similarity = np.dot(sample_embeddings[i], sample_embeddings[j])
                logger.info(f"   Text {i+1} vs Text {j+1}: {similarity:.3f}")
                logger.info(f"     Text {i+1}: {sample_texts[i][:50]}...")
                logger.info(f"     Text {j+1}: {sample_texts[j][:50]}...")
        
        return {
            'total_embeddings': total_embeddings,
            'embedding_dimension': embedding_dim,
            'sample_similarities': similarity
        }
    
    def save_embeddings(self, df, filename='embeddings_data.csv'):
        """
        Save the data with embeddings
        Note: CSV files can't store arrays well, so we'll save as pickle
        """
        logger.info(f"💾 Saving embeddings...")
        
        # Save as pickle (better for arrays)
        pickle_filename = filename.replace('.csv', '.pkl')
        with open(pickle_filename, 'wb') as f:
            pickle.dump(df, f)
        
        logger.info(f"✅ Saved embeddings to {pickle_filename}")
        
        # Also save a CSV without embeddings for inspection
        df_no_embeddings = df.drop('embedding', axis=1)
        df_no_embeddings.to_csv(filename, index=False)
        logger.info(f"✅ Saved data without embeddings to {filename}")
        
        return pickle_filename
    
    def create_vector_database_info(self, df):
        """
        Create information for vector database setup
        """
        logger.info("🗄️ Creating vector database information...")
        
        # Sample embeddings for database setup
        sample_embeddings = df['embedding'].head(100).tolist()
        sample_texts = df['text'].head(100).tolist()
        sample_labels = df['label'].head(100).tolist()
        
        db_info = {
            'total_embeddings': len(df),
            'embedding_dimension': len(df['embedding'].iloc[0]),
            'sample_data': {
                'embeddings': sample_embeddings,
                'texts': sample_texts,
                'labels': sample_labels
            }
        }
        
        # Save database info
        with open('vector_db_info.pkl', 'wb') as f:
            pickle.dump(db_info, f)
        
        logger.info(f"✅ Vector database info saved")
        logger.info(f"📊 Database ready for {len(df)} embeddings")
        
        return db_info

def demonstrate_embeddings():
    """
    Demonstrate how embeddings work with simple examples
    """
    logger.info("🎯 Embedding Demonstration")
    logger.info("=" * 40)
    
    # Simple examples
    examples = [
        "Women are emotional creatures",
        "Women can't handle stress like men",
        "Women are great leaders",
        "Men are logical thinkers",
        "This is a neutral statement"
    ]
    
    logger.info("📝 Example texts:")
    for i, text in enumerate(examples, 1):
        logger.info(f"   {i}. {text}")
    
    # Generate embeddings
    generator = EmbeddingGenerator()
    embeddings = generator.generate_embeddings(examples)
    
    logger.info(f"\n🧮 Generated embeddings:")
    logger.info(f"   - Shape: {embeddings.shape}")
    logger.info(f"   - Each embedding has {embeddings.shape[1]} numbers")
    
    # Show similarity matrix
    logger.info(f"\n🔍 Similarity Matrix:")
    for i in range(len(examples)):
        for j in range(len(examples)):
            similarity = np.dot(embeddings[i], embeddings[j])
            logger.info(f"   Text {i+1} vs Text {j+1}: {similarity:.3f}")
    
    logger.info(f"\n💡 What this means:")
    logger.info(f"   - Higher numbers = more similar")
    logger.info(f"   - Lower numbers = less similar")
    logger.info(f"   - RAG uses this to find similar misogyny examples")

def main():
    """
    Main function - generate embeddings for the chunked data
    """
    logger.info("🎯 Step 3: Create Embeddings for Misogyny Detection RAG")
    logger.info("=" * 60)
    
    # Demonstrate embeddings first
    demonstrate_embeddings()
    
    # Create generator
    generator = EmbeddingGenerator()
    
    # Step 1: Load chunked data
    df = generator.load_chunked_data()
    if df is None:
        logger.error("❌ Could not load chunked data. Please run Step 2 first.")
        return
    
    # Step 2: Generate embeddings
    df_with_embeddings = generator.process_dataset(df)
    
    # Step 3: Analyze embeddings
    analysis = generator.analyze_embeddings(df_with_embeddings)
    
    # Step 4: Save embeddings
    filename = generator.save_embeddings(df_with_embeddings)
    
    # Step 5: Create vector database info
    db_info = generator.create_vector_database_info(df_with_embeddings)
    
    # Summary
    logger.info("\n🎉 Embedding Generation Complete!")
    logger.info("📊 What we accomplished:")
    logger.info(f"   - Generated {analysis['total_embeddings']} embeddings")
    logger.info(f"   - Each embedding has {analysis['embedding_dimension']} numbers")
    logger.info(f"   - Saved to {filename}")
    logger.info(f"   - Ready for vector database setup!")
    
    logger.info("\n🚀 Next Step: Set up vector database for similarity search")
    logger.info("This will allow RAG to quickly find similar misogyny examples")

if __name__ == "__main__":
    main() 