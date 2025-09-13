#!/usr/bin/env python3
"""
Simple RAG Detector - No API, No Server, Just Import and Use!
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRAGDetector:
    """
    Simple RAG-based misogyny detector
    Just import this class and use it directly in your app!
    """
    
    def __init__(self):
        """Initialize the detector"""
        logger.info("🎯 Loading Simple RAG Detector...")
        
        try:
            # Load the embedding model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded")
            
            # Connect to ChromaDB
            self.client = chromadb.Client()
            try:
                self.collection = self.client.get_collection("misogyny_chunks")
                logger.info("✅ Connected to database")
            except:
                logger.warning("⚠️ Database not found. Creating demo collection...")
                self.collection = self.client.create_collection("misogyny_chunks_demo")
                logger.info("✅ Created demo collection")
            
            # Load alternative suggestions
            self.alternatives = self._load_alternatives()
            logger.info("✅ Alternatives loaded")
            
            logger.info("🎉 Simple RAG Detector ready!")
            
        except Exception as e:
            logger.error(f"❌ Error loading detector: {str(e)}")
            raise
    
    def _load_alternatives(self):
        """Load alternative word suggestions"""
        return {
            "bitches": ["women", "people", "individuals"],
            "sluts": ["women", "people", "individuals"],
            "whores": ["women", "people", "individuals"],
            "emotional": ["expressive", "passionate", "caring"],
            "hysterical": ["upset", "concerned", "worried"],
            "bossy": ["assertive", "confident", "decisive"],
            "abrasive": ["direct", "straightforward", "clear"],
            "girlboss": ["entrepreneur", "business leader", "executive"],
            "good girl": ["capable", "skilled", "professional"],
            "women": ["people", "individuals", "professionals"],
            "girls": ["women", "professionals", "individuals"],
            "ladies": ["women", "professionals", "individuals"]
        }
    
    def check_message(self, text: str, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Check if a message contains misogynistic language
        
        Args:
            text: The message to check
            threshold: Confidence threshold (0.0 to 1.0)
            
        Returns:
            Dictionary with results:
            {
                'is_misogynistic': True/False,
                'confidence': 0.8,
                'explanations': ['This contains...'],
                'suggestions': ['Try using...'],
                'problematic_terms': ['emotional']
            }
        """
        logger.info(f"🔍 Checking: {text[:50]}...")
        
        try:
            # Generate embedding
            embedding = self.model.encode([text])[0]
            
            # Search database
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Analyze results
            analysis = self._analyze_results(text, results, threshold)
            
            # Generate explanations and suggestions
            analysis.update(self._generate_explanations(text, analysis))
            
            logger.info(f"✅ Check complete: {'🚫 BLOCKED' if analysis['is_misogynistic'] else '✅ APPROVED'}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error checking message: {str(e)}")
            return {
                'is_misogynistic': False,
                'confidence': 0.0,
                'error': str(e),
                'explanations': ['Error occurred during analysis'],
                'suggestions': [],
                'problematic_terms': []
            }
    
    def _analyze_results(self, text: str, results: Dict, threshold: float) -> Dict:
        """Analyze search results"""
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Calculate similarities
        similarities = [1 - dist for dist in distances]
        
        # Count misogyny vs non-misogyny
        misogyny_count = 0
        non_misogyny_count = 0
        misogyny_similarities = []
        non_misogyny_similarities = []
        
        for i, (doc, metadata, similarity) in enumerate(zip(documents, metadatas, similarities)):
            if metadata.get('is_misogyny', 0) == 1:
                misogyny_count += 1
                misogyny_similarities.append(similarity)
            else:
                non_misogyny_count += 1
                non_misogyny_similarities.append(similarity)
        
        # Calculate averages
        avg_misogyny = np.mean(misogyny_similarities) if misogyny_similarities else 0
        avg_non_misogyny = np.mean(non_misogyny_similarities) if non_misogyny_similarities else 0
        
        # Determine result
        is_misogynistic = False
        confidence = 0.0
        
        if misogyny_count > non_misogyny_count:
            if avg_misogyny > threshold:
                is_misogynistic = True
                confidence = avg_misogyny
        elif non_misogyny_count > misogyny_count:
            confidence = avg_non_misogyny
        else:
            if avg_misogyny > avg_non_misogyny:
                if avg_misogyny > threshold:
                    is_misogynistic = True
                    confidence = avg_misogyny
            else:
                confidence = avg_non_misogyny
        
        return {
            'is_misogynistic': is_misogynistic,
            'confidence': confidence,
            'threshold': threshold
        }
    
    def _generate_explanations(self, text: str, analysis: Dict) -> Dict:
        """Generate explanations and suggestions"""
        explanations = []
        suggestions = []
        problematic_terms = []
        
        if analysis['is_misogynistic']:
            explanations.append("This text contains language that reinforces harmful stereotypes about women.")
            
            # Find problematic terms
            text_lower = text.lower()
            for term in self.alternatives.keys():
                if term in text_lower:
                    problematic_terms.append(term)
                    suggestions.extend(self.alternatives[term])
            
            if problematic_terms:
                explanations.append(f"Problematic terms: {', '.join(problematic_terms)}")
        else:
            explanations.append("This text appears respectful and doesn't contain misogynistic language.")
        
        return {
            'explanations': explanations,
            'suggestions': list(set(suggestions)),  # Remove duplicates
            'problematic_terms': problematic_terms
        }

# Example usage
def main():
    """Example of how to use the simple detector"""
    print("🧪 Testing Simple RAG Detector...")
    
    # Create detector
    detector = SimpleRAGDetector()
    
    # Test messages
    test_messages = [
        "Hello, how are you?",
        "Women are too emotional for leadership",
        "She's such a bossy woman",
        "This is a neutral statement about technology",
        "I respect women and their capabilities"
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        
        # Check the message
        result = detector.check_message(message)
        
        if result['is_misogynistic']:
            print("🚫 BLOCKED - Misogynistic content detected!")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Explanations: {result['explanations']}")
            print(f"Suggestions: {result['suggestions']}")
            print(f"Problematic terms: {result['problematic_terms']}")
        else:
            print("✅ APPROVED - Message is fine")
            print(f"Confidence: {result['confidence']:.3f}")

if __name__ == "__main__":
    main() 