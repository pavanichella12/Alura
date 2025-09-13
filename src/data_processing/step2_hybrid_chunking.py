#!/usr/bin/env python3
"""
Step 2: Hybrid Chunking for Misogyny Detection RAG
Simple implementation that processes your 63K samples with the best chunking strategy
"""

import pandas as pd
import re
import nltk
from nltk.tokenize import sent_tokenize
import logging
from typing import List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class HybridChunker:
    def __init__(self):
        """Initialize the hybrid chunker"""
        logger.info("🚀 Starting Hybrid Chunking Process...")
        logger.info("This will process your 63K samples with the best strategy for each text")
        
        # Misogyny keywords for semantic awareness
        self.misogyny_keywords = [
            'women', 'woman', 'girl', 'female', 'bitch', 'slut', 'whore',
            'emotional', 'hysterical', 'bossy', 'aggressive', 'feminine',
            'mother', 'wife', 'girlfriend', 'daughter', 'sister'
        ]
    
    def load_data(self, filename='combined_misogyny_data.csv'):
        """Load the combined dataset"""
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
        """Clean text for better chunking"""
        if pd.isna(text) or text == '':
            return ''
        
        text = str(text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        
        # Clean hashtags but keep text
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def has_misogyny_content(self, text):
        """Check if text contains misogyny-related keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.misogyny_keywords)
    
    def chunk_short_text(self, text):
        """For short texts (≤150 chars): keep as-is"""
        return [text]
    
    def chunk_medium_text(self, text, max_length=300):
        """For medium texts (150-500 chars): sentence-based chunking"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_long_text(self, text, max_length=250):
        """For long texts (500+ chars): semantic + sentence-based"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if sentence contains misogyny content
            has_misogyny = self.has_misogyny_content(sentence)
            
            if has_misogyny and len(current_chunk) > 0:
                # Start new chunk for misogyny content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
            elif len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def hybrid_chunk(self, text):
        """
        Hybrid chunking: Choose strategy based on text length
        """
        # Clean the text first
        clean_text = self.clean_text(text)
        
        if not clean_text:
            return []
        
        length = len(clean_text)
        
        # Choose strategy based on length
        if length <= 150:
            logger.debug(f"Short text ({length} chars): using as-is")
            return self.chunk_short_text(clean_text)
        elif length <= 500:
            logger.debug(f"Medium text ({length} chars): sentence-based chunking")
            return self.chunk_medium_text(clean_text)
        else:
            logger.debug(f"Long text ({length} chars): semantic chunking")
            return self.chunk_long_text(clean_text)
    
    def process_dataset(self, df):
        """
        Process the entire dataset with hybrid chunking
        """
        logger.info("🧹 Processing dataset with hybrid chunking...")
        
        processed_chunks = []
        total_original = len(df)
        
        # Track statistics
        stats = {
            'short_texts': 0,
            'medium_texts': 0,
            'long_texts': 0,
            'total_chunks': 0
        }
        
        for idx, row in df.iterrows():
            # Clean and chunk the text
            chunks = self.hybrid_chunk(row['text'])
            
            # Update statistics
            length = len(self.clean_text(row['text']))
            if length <= 150:
                stats['short_texts'] += 1
            elif length <= 500:
                stats['medium_texts'] += 1
            else:
                stats['long_texts'] += 1
            
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
                    'is_misogyny': row['label'],
                    'original_length': length,
                    'chunk_strategy': self.get_strategy_name(length)
                })
                stats['total_chunks'] += 1
            
            # Show progress every 1000 samples
            if (idx + 1) % 1000 == 0:
                logger.info(f"📈 Processed {idx + 1}/{total_original} samples...")
        
        logger.info(f"✅ Processing complete!")
        logger.info(f"📊 Statistics:")
        logger.info(f"   - Short texts (≤150 chars): {stats['short_texts']}")
        logger.info(f"   - Medium texts (150-500 chars): {stats['medium_texts']}")
        logger.info(f"   - Long texts (500+ chars): {stats['long_texts']}")
        logger.info(f"   - Total chunks created: {stats['total_chunks']}")
        
        return pd.DataFrame(processed_chunks), stats
    
    def get_strategy_name(self, length):
        """Get the strategy name for a given text length"""
        if length <= 150:
            return 'short_as_is'
        elif length <= 500:
            return 'sentence_based'
        else:
            return 'semantic'
    
    def analyze_results(self, df, stats):
        """
        Analyze the chunking results
        """
        logger.info("📊 Analyzing chunking results...")
        
        # Basic statistics
        total_chunks = len(df)
        misogyny_chunks = len(df[df['label'] == 1])
        avg_length = df['chunk_length'].mean()
        
        logger.info(f"📈 Final Statistics:")
        logger.info(f"   - Total chunks: {total_chunks}")
        logger.info(f"   - Misogyny chunks: {misogyny_chunks}")
        logger.info(f"   - Non-misogyny chunks: {total_chunks - misogyny_chunks}")
        logger.info(f"   - Average chunk length: {avg_length:.1f} characters")
        
        # Strategy breakdown
        strategy_counts = df['chunk_strategy'].value_counts()
        logger.info(f"   - Strategy breakdown:")
        for strategy, count in strategy_counts.items():
            logger.info(f"     {strategy}: {count} chunks")
        
        # Show some examples
        logger.info(f"📝 Sample chunks:")
        for i, row in df.head(3).iterrows():
            logger.info(f"   Chunk {i+1} ({row['chunk_strategy']}): {row['text'][:80]}...")
        
        return {
            'total_chunks': total_chunks,
            'misogyny_chunks': misogyny_chunks,
            'avg_length': avg_length,
            'strategy_breakdown': strategy_counts.to_dict()
        }
    
    def save_results(self, df, filename='hybrid_chunked_data.csv'):
        """
        Save the chunked data for the next step
        """
        logger.info(f"💾 Saving chunked data to {filename}...")
        
        df.to_csv(filename, index=False)
        logger.info(f"✅ Saved {len(df)} chunks to {filename}")
        
        return filename

def main():
    """
    Main function - runs the hybrid chunking process
    """
    logger.info("🎯 Step 2: Hybrid Chunking for Misogyny Detection RAG")
    logger.info("=" * 60)
    
    # Create chunker
    chunker = HybridChunker()
    
    # Step 1: Load data
    df = chunker.load_data()
    if df is None:
        logger.error("❌ Could not load data. Please run Step 1 first.")
        return
    
    # Step 2: Process with hybrid chunking
    processed_df, stats = chunker.process_dataset(df)
    
    # Step 3: Analyze results
    analysis = chunker.analyze_results(processed_df, stats)
    
    # Step 4: Save results
    filename = chunker.save_results(processed_df)
    
    # Summary
    logger.info("\n🎉 Hybrid Chunking Complete!")
    logger.info("📊 What we accomplished:")
    logger.info(f"   - Processed {len(df)} original samples")
    logger.info(f"   - Created {len(processed_df)} optimized chunks")
    logger.info(f"   - Average chunk length: {analysis['avg_length']:.1f} characters")
    logger.info(f"   - Used adaptive strategy based on text length")
    logger.info(f"   - Ready for embedding generation!")
    
    logger.info("\n🚀 Next Step: Generate embeddings for these chunks")
    logger.info("This will convert text into numbers that RAG can search quickly")

if __name__ == "__main__":
    main() 