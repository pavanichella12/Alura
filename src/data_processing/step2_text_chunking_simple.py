#!/usr/bin/env python3
"""
Step 2: Text Chunking for Beginners
This script takes our combined dataset and prepares it for RAG by:
1. Cleaning the text (removing bad characters)
2. Splitting long texts into smaller pieces
3. Making sure each piece is good for searching
"""

import pandas as pd
import re
import logging
from typing import List, Dict

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self):
        """Initialize the text chunker"""
        logger.info("🚀 Starting Text Chunking Process...")
        logger.info("This will prepare our data for RAG by cleaning and splitting text")
    
    def load_combined_data(self, filename='combined_misogyny_data.csv'):
        """Load our combined dataset"""
        logger.info(f"📖 Loading data from {filename}...")
        
        try:
            df = pd.read_csv(filename)
            logger.info(f"✅ Loaded {len(df)} samples")
            logger.info(f"📊 Sample data:")
            logger.info(f"   - First text: {df['text'].iloc[0][:100]}...")
            logger.info(f"   - Labels: {df['label'].value_counts().to_dict()}")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            return None
    
    def clean_text(self, text):
        """
        Clean text by removing bad characters and normalizing
        This makes the text better for RAG
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Convert to string
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause problems
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        # Remove URLs (they don't help with misogyny detection)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove user mentions like @username
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Clean up extra spaces
        text = text.strip()
        
        return text
    
    def split_text_into_chunks(self, text, max_length=200, overlap=50):
        """
        Split long text into smaller chunks
        This helps RAG find relevant parts of long messages
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Take a chunk of max_length
            end = start + max_length
            
            # If this isn't the last chunk, try to break at a word boundary
            if end < len(text):
                # Look for a space or punctuation to break at
                for i in range(end, max(start, end - 50), -1):
                    if text[i] in ' .!?,':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position, with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_dataset(self, df):
        """
        Process the entire dataset: clean and chunk all texts
        """
        logger.info("🧹 Cleaning and chunking all texts...")
        
        processed_chunks = []
        total_original = len(df)
        
        for idx, row in df.iterrows():
            # Clean the text
            clean_text = self.clean_text(row['text'])
            
            if clean_text:  # Only process non-empty texts
                # Split into chunks if needed
                chunks = self.split_text_into_chunks(clean_text)
                
                # Create a record for each chunk
                for chunk_idx, chunk in enumerate(chunks):
                    processed_chunks.append({
                        'original_id': idx,
                        'chunk_id': f"{idx}_{chunk_idx}",
                        'text': chunk,
                        'label': row['label'],
                        'source': row['source'],
                        'category': row.get('category', 'unknown'),
                        'subcategory': row.get('subcategory', ''),
                        'chunk_length': len(chunk),
                        'is_misogyny': row['label']
                    })
            
            # Show progress every 1000 samples
            if (idx + 1) % 1000 == 0:
                logger.info(f"📈 Processed {idx + 1}/{total_original} samples...")
        
        logger.info(f"✅ Processing complete!")
        logger.info(f"📊 Original samples: {total_original}")
        logger.info(f"📊 Processed chunks: {len(processed_chunks)}")
        
        return pd.DataFrame(processed_chunks)
    
    def analyze_chunks(self, df):
        """
        Analyze the processed chunks to make sure they're good
        """
        logger.info("📊 Analyzing processed chunks...")
        
        # Basic statistics
        total_chunks = len(df)
        misogyny_chunks = len(df[df['label'] == 1])
        avg_length = df['chunk_length'].mean()
        min_length = df['chunk_length'].min()
        max_length = df['chunk_length'].max()
        
        logger.info(f"📈 Chunk Statistics:")
        logger.info(f"   - Total chunks: {total_chunks}")
        logger.info(f"   - Misogyny chunks: {misogyny_chunks}")
        logger.info(f"   - Non-misogyny chunks: {total_chunks - misogyny_chunks}")
        logger.info(f"   - Average length: {avg_length:.1f} characters")
        logger.info(f"   - Length range: {min_length} - {max_length} characters")
        
        # Show some examples
        logger.info(f"📝 Sample chunks:")
        for i, row in df.head(3).iterrows():
            logger.info(f"   Chunk {i+1}: {row['text'][:80]}...")
        
        return {
            'total_chunks': total_chunks,
            'misogyny_chunks': misogyny_chunks,
            'avg_length': avg_length,
            'min_length': min_length,
            'max_length': max_length
        }
    
    def save_processed_data(self, df, filename='processed_chunks.csv'):
        """
        Save the processed chunks for the next step
        """
        logger.info(f"💾 Saving processed chunks to {filename}...")
        
        df.to_csv(filename, index=False)
        logger.info(f"✅ Saved {len(df)} chunks to {filename}")
        
        return filename

def main():
    """
    Main function - runs the entire text chunking process
    """
    logger.info("🎯 Step 2: Text Chunking for RAG")
    logger.info("=" * 50)
    
    # Create chunker
    chunker = TextChunker()
    
    # Step 1: Load data
    df = chunker.load_combined_data()
    if df is None:
        logger.error("❌ Could not load data. Please run Step 1 first.")
        return
    
    # Step 2: Process the dataset
    processed_df = chunker.process_dataset(df)
    
    # Step 3: Analyze the results
    stats = chunker.analyze_chunks(processed_df)
    
    # Step 4: Save for next step
    filename = chunker.save_processed_data(processed_df)
    
    # Summary
    logger.info("\n🎉 Text Chunking Complete!")
    logger.info("📊 What we accomplished:")
    logger.info(f"   - Cleaned and chunked {len(df)} original samples")
    logger.info(f"   - Created {len(processed_df)} searchable chunks")
    logger.info(f"   - Average chunk length: {stats['avg_length']:.1f} characters")
    logger.info(f"   - Ready for embedding generation!")
    
    logger.info("\n🚀 Next Step: Generate embeddings for these chunks")
    logger.info("This will convert text into numbers that RAG can search quickly")

if __name__ == "__main__":
    main() 