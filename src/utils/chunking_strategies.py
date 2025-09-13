#!/usr/bin/env python3
"""
Chunking Strategies for Misogyny Detection RAG
This file demonstrates different chunking techniques and recommends the best approach
"""

import pandas as pd
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import List, Dict, Tuple

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ChunkingStrategies:
    def __init__(self):
        """Initialize chunking strategies"""
        self.strategies = {
            'fixed_size': self.fixed_size_chunking,
            'sentence_based': self.sentence_based_chunking,
            'paragraph_based': self.paragraph_based_chunking,
            'semantic': self.semantic_chunking,
            'hybrid': self.hybrid_chunking
        }
    
    def fixed_size_chunking(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        """
        Fixed-size chunking: Cut text into pieces of exactly chunk_size characters
        
        Best for: Short, uniform texts
        Your data: Good for short messages, but may cut words
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at word boundary
            if end < len(text):
                for i in range(end, max(start, end - 50), -1):
                    if text[i] in ' .!?,':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def sentence_based_chunking(self, text: str, max_length: int = 300) -> List[str]:
        """
        Sentence-based chunking: Cut at sentence boundaries
        
        Best for: Natural language, maintaining context
        Your data: Good for academic and social media content
        """
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
    
    def paragraph_based_chunking(self, text: str, max_length: int = 400) -> List[str]:
        """
        Paragraph-based chunking: Cut at paragraph breaks
        
        Best for: Long documents, maintaining topic context
        Your data: Good for longer academic texts
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_length:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def semantic_chunking(self, text: str, max_length: int = 250) -> List[str]:
        """
        Semantic chunking: Cut based on meaning and topics
        
        Best for: Complex texts, maintaining semantic coherence
        Your data: Good for detecting misogyny patterns
        """
        # Simple semantic chunking based on keywords
        misogyny_keywords = [
            'women', 'woman', 'girl', 'female', 'bitch', 'slut', 'whore',
            'emotional', 'hysterical', 'bossy', 'aggressive', 'feminine',
            'mother', 'wife', 'girlfriend', 'daughter', 'sister'
        ]
        
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if sentence contains misogyny-related content
            has_misogyny_content = any(keyword.lower() in sentence.lower() 
                                     for keyword in misogyny_keywords)
            
            if has_misogyny_content and len(current_chunk) > 0:
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
    
    def hybrid_chunking(self, text: str) -> List[str]:
        """
        Hybrid chunking: Combine multiple strategies based on text characteristics
        
        Best for: Mixed content like your dataset
        Your data: PERFECT for your misogyny detection RAG
        """
        # Clean the text first
        text = self.clean_text(text)
        
        if len(text) <= 150:
            # Short text: use as-is
            return [text]
        elif len(text) <= 500:
            # Medium text: sentence-based with overlap
            return self.sentence_based_chunking(text, max_length=300)
        else:
            # Long text: semantic + sentence-based
            semantic_chunks = self.semantic_chunking(text, max_length=250)
            
            # Further split long semantic chunks
            final_chunks = []
            for chunk in semantic_chunks:
                if len(chunk) > 300:
                    # Split long semantic chunks
                    sentence_chunks = self.sentence_based_chunking(chunk, max_length=250)
                    final_chunks.extend(sentence_chunks)
                else:
                    final_chunks.append(chunk)
            
            return final_chunks
    
    def clean_text(self, text: str) -> str:
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
    
    def analyze_text_characteristics(self, text: str) -> Dict:
        """Analyze text to recommend best chunking strategy"""
        text = self.clean_text(text)
        
        analysis = {
            'length': len(text),
            'sentences': len(sent_tokenize(text)),
            'words': len(word_tokenize(text)),
            'avg_sentence_length': len(word_tokenize(text)) / max(len(sent_tokenize(text)), 1),
            'has_misogyny_keywords': self.has_misogyny_keywords(text),
            'recommended_strategy': self.recommend_strategy(text)
        }
        
        return analysis
    
    def has_misogyny_keywords(self, text: str) -> bool:
        """Check if text contains misogyny-related keywords"""
        misogyny_keywords = [
            'women', 'woman', 'girl', 'female', 'bitch', 'slut', 'whore',
            'emotional', 'hysterical', 'bossy', 'aggressive'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in misogyny_keywords)
    
    def recommend_strategy(self, text: str) -> str:
        """Recommend the best chunking strategy for a given text"""
        length = len(text)
        
        if length <= 150:
            return 'fixed_size'  # Short texts: use as-is
        elif length <= 500:
            return 'sentence_based'  # Medium texts: sentence boundaries
        elif length <= 1000:
            return 'semantic'  # Longer texts: semantic chunking
        else:
            return 'hybrid'  # Very long texts: hybrid approach
    
    def compare_strategies(self, text: str) -> Dict:
        """Compare different chunking strategies on the same text"""
        results = {}
        
        for strategy_name, strategy_func in self.strategies.items():
            try:
                chunks = strategy_func(text)
                results[strategy_name] = {
                    'num_chunks': len(chunks),
                    'avg_chunk_length': sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0,
                    'chunks': chunks[:3]  # Show first 3 chunks
                }
            except Exception as e:
                results[strategy_name] = {'error': str(e)}
        
        return results

def demonstrate_chunking():
    """Demonstrate different chunking strategies with examples"""
    
    # Example texts from your dataset
    examples = [
        # Short text (good for fixed-size)
        "Women are emotional creatures who can't handle stress.",
        
        # Medium text (good for sentence-based)
        "Women are emotional and can't handle leadership roles. They get too stressed out and make bad decisions. Men are naturally better leaders because they think logically.",
        
        # Long text (good for semantic/hybrid)
        "Women are emotional creatures who can't handle stress like men do. They get hysterical over small things and can't make rational decisions when under pressure. This is why they shouldn't be in leadership positions. Men are naturally more logical and can handle difficult situations better. Women should stick to nurturing roles where their emotional nature is an asset rather than a liability.",
        
        # Very long text (needs hybrid)
        "The idea that women are emotional and therefore unfit for leadership is a deeply ingrained stereotype that has been used to justify gender discrimination for centuries. Women are often described as 'hysterical' or 'emotional' when they express legitimate concerns or frustration, while men who display the same emotions are seen as 'passionate' or 'determined'. This double standard perpetuates harmful gender roles and limits women's opportunities in the workplace. Research has shown that emotional intelligence, which women often excel at, is actually a valuable leadership trait. The stereotype that women are too emotional for leadership is not only false but also harmful to both women and organizations that miss out on talented female leaders."
    ]
    
    chunker = ChunkingStrategies()
    
    print("🎯 Chunking Strategy Demonstration")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i} (Length: {len(example)} characters):")
        print(f"Text: {example[:100]}...")
        
        # Analyze the text
        analysis = chunker.analyze_text_characteristics(example)
        print(f"📊 Analysis:")
        print(f"   - Length: {analysis['length']} characters")
        print(f"   - Sentences: {analysis['sentences']}")
        print(f"   - Has misogyny keywords: {analysis['has_misogyny_keywords']}")
        print(f"   - Recommended strategy: {analysis['recommended_strategy']}")
        
        # Compare strategies
        comparison = chunker.compare_strategies(example)
        print(f"🔍 Strategy Comparison:")
        for strategy, result in comparison.items():
            if 'error' not in result:
                print(f"   - {strategy}: {result['num_chunks']} chunks, "
                      f"avg {result['avg_chunk_length']:.1f} chars")
            else:
                print(f"   - {strategy}: Error - {result['error']}")

def recommend_for_misogyny_detection():
    """Recommend the best chunking strategy for misogyny detection RAG"""
    
    print("\n🎯 RECOMMENDATION FOR YOUR MISOGYNY DETECTION RAG")
    print("=" * 60)
    
    print("\n📊 Your Data Characteristics:")
    print("   - Average length: 143 characters")
    print("   - Range: 1 - 18,148 characters")
    print("   - Sources: Social media, academic, manual annotations")
    print("   - Content: Mixed (short tweets to long articles)")
    
    print("\n🏆 RECOMMENDED STRATEGY: HYBRID CHUNKING")
    print("\nWhy Hybrid is Best for Your Use Case:")
    print("✅ Handles mixed text lengths (short tweets to long articles)")
    print("✅ Maintains context for misogyny detection")
    print("✅ Uses semantic awareness for better accuracy")
    print("✅ Adapts strategy based on text characteristics")
    print("✅ Good for RAG similarity search")
    
    print("\n🔧 Implementation Strategy:")
    print("1. Short texts (≤150 chars): Use as-is")
    print("2. Medium texts (150-500 chars): Sentence-based chunking")
    print("3. Long texts (500+ chars): Semantic + sentence-based")
    print("4. Very long texts (1000+ chars): Hybrid approach")
    
    print("\n📈 Expected Results:")
    print("   - Better misogyny detection accuracy")
    print("   - Faster similarity search")
    print("   - More relevant alternative suggestions")
    print("   - Improved context understanding")

if __name__ == "__main__":
    demonstrate_chunking()
    recommend_for_misogyny_detection() 