#!/usr/bin/env python3
"""
RAG Integration Module
Integrates your RAG system with the content moderation app
"""

try:
    from .simple_rag_detector import SimpleRAGDetector
    RAG_AVAILABLE = True
    print("✅ RAG system imported successfully")
except ImportError as e:
    print(f"⚠️ RAG system not available: {e}")
    RAG_AVAILABLE = False

class RAGIntegration:
    """Integrates your RAG system with the content moderation app"""
    
    def __init__(self):
        self.rag_detector = None
        if RAG_AVAILABLE:
            try:
                self.rag_detector = SimpleRAGDetector()
                print("✅ RAG system loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load RAG system: {e}")
                self.rag_detector = None
    
    def analyze_with_rag(self, message: str) -> dict:
        """Analyze message using your RAG system"""
        if not self.rag_detector:
            return None
        
        try:
            result = self.rag_detector.check_message(message, threshold=0.3)
            
            # Transform RAG result to match our format
            return {
                "flagged": result.get("is_misogynistic", False),
                "confidence": result.get("confidence", 0.0),
                "detected_words": result.get("problematic_terms", []),
                "categories": ["misogynistic_language"] if result.get("is_misogynistic", False) else [],
                "context_analysis": " | ".join(result.get("explanations", [])),
                "alternatives": result.get("suggestions", []),
                "severity": "high" if result.get("confidence", 0.0) > 0.7 else "medium",
                "reasoning": "Analysis by RAG system",
                "source": "rag"
            }
        except Exception as e:
            print(f"❌ RAG analysis failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if RAG system is available"""
        return self.rag_detector is not None

# Test the integration
if __name__ == "__main__":
    rag = RAGIntegration()
    if rag.is_available():
        result = rag.analyze_with_rag("Women are too emotional for leadership")
        print(f"RAG Result: {result}")
    else:
        print("RAG system not available") 