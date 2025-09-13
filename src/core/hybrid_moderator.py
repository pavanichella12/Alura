#!/usr/bin/env python3
"""
Hybrid Content Moderator
Combines Knowledge Injection (Llama 3) with RAG system for enhanced accuracy
"""

from typing import Dict, Optional
from .knowledge_injection_moderator import KnowledgeInjectionModerator
from ..rag_system.rag_integration import RAGIntegration

class HybridModerator:
    """
    Hybrid moderator that combines:
    1. Knowledge Injection (Llama 3 + prompt engineering)
    2. RAG System (vector embeddings + similarity search)
    """
    
    def __init__(self):
        """Initialize both systems"""
        print("🔧 Initializing Hybrid Moderator...")
        
        # Initialize Knowledge Injection system
        self.knowledge_injection = KnowledgeInjectionModerator()
        print("✅ Knowledge Injection system ready")
        
        # Initialize RAG system
        self.rag_system = RAGIntegration()
        if self.rag_system.is_available():
            print("✅ RAG system ready")
        else:
            print("⚠️ RAG system not available - using Knowledge Injection only")
    
    def analyze_message(self, message: str, user_id: str = "default_user") -> Dict:
        """
        Analyze message using both systems and combine results
        
        Returns:
            Dict with combined analysis results
        """
        print(f"🔍 Hybrid analysis of: {message[:50]}...")
        
        # Get results from both systems
        ki_result = self._analyze_with_knowledge_injection(message, user_id)
        rag_result = self._analyze_with_rag(message, user_id)
        
        # Combine results intelligently
        combined_result = self._combine_results(ki_result, rag_result, message)
        
        print(f"✅ Hybrid analysis complete: {'🚫 BLOCKED' if combined_result['flagged'] else '✅ APPROVED'}")
        return combined_result
    
    def _analyze_with_knowledge_injection(self, message: str, user_id: str) -> Dict:
        """Analyze using Knowledge Injection (Llama 3)"""
        try:
            result = self.knowledge_injection.analyze_message(message, user_id)
            result['source'] = 'knowledge_injection'
            return result
        except Exception as e:
            print(f"❌ Knowledge Injection failed: {e}")
            return {
                'flagged': False,
                'confidence': 0.0,
                'detected_words': [],
                'categories': [],
                'context_analysis': 'Knowledge Injection failed',
                'alternatives': [],
                'severity': 'low',
                'reasoning': f'Knowledge Injection error: {e}',
                'source': 'knowledge_injection'
            }
    
    def _analyze_with_rag(self, message: str, user_id: str) -> Optional[Dict]:
        """Analyze using RAG system"""
        if not self.rag_system.is_available():
            return None
        
        try:
            result = self.rag_system.analyze_with_rag(message)
            return result
        except Exception as e:
            print(f"❌ RAG analysis failed: {e}")
            return None
    
    def _combine_results(self, ki_result: Dict, rag_result: Optional[Dict], message: str) -> Dict:
        """Intelligently combine results from both systems"""
        
        # If only one system worked, use that result
        if ki_result and not rag_result:
            print("✅ Using Knowledge Injection result only")
            return ki_result
        
        if rag_result and not ki_result:
            print("✅ Using RAG result only")
            return rag_result
        
        # If neither worked, use fallback
        if not ki_result and not rag_result:
            print("⚠️ Both systems failed, using fallback")
            return {
                'flagged': False,
                'confidence': 0.0,
                'detected_words': [],
                'categories': [],
                'context_analysis': 'Both systems failed',
                'alternatives': [],
                'severity': 'low',
                'reasoning': 'Fallback due to system failures',
                'source': 'fallback'
            }
        
        # Both systems worked - combine intelligently
        print("🔄 Combining results from both systems")
        
        # Determine final flagged status
        ki_flagged = ki_result.get("flagged", False)
        rag_flagged = rag_result.get("flagged", False)
        
        # If both agree, use that result with higher confidence
        if ki_flagged == rag_flagged:
            final_flagged = ki_flagged
            ki_confidence = ki_result.get("confidence", 0.0)
            rag_confidence = rag_result.get("confidence", 0.0)
            confidence = max(ki_confidence, rag_confidence)
            detection_method = "hybrid_agreement"
        else:
            # They disagree - use the more confident system
            ki_confidence = ki_result.get("confidence", 0.0)
            rag_confidence = rag_result.get("confidence", 0.0)
            
            if ki_confidence > rag_confidence:
                final_flagged = ki_flagged
                confidence = ki_confidence
                detection_method = "knowledge_injection_higher_confidence"
            else:
                final_flagged = rag_flagged
                confidence = rag_confidence
                detection_method = "rag_higher_confidence"
        
        # Combine detected words
        detected_words = list(set(
            ki_result.get("detected_words", []) + 
            rag_result.get("detected_words", [])
        ))
        
        # Combine categories
        categories = list(set(
            ki_result.get("categories", []) + 
            rag_result.get("categories", [])
        ))
        
        # Combine alternatives (take best from both)
        alternatives = []
        ki_alternatives = ki_result.get("alternatives", [])
        rag_alternatives = rag_result.get("alternatives", [])
        
        # Add Knowledge Injection alternatives first (more contextual)
        alternatives.extend(ki_alternatives)
        
        # Add RAG alternatives if not already present
        for alt in rag_alternatives:
            if alt not in alternatives:
                alternatives.append(alt)
        
        # Limit alternatives to 5
        alternatives = alternatives[:5]
        
        # Combine reasoning
        ki_reasoning = ki_result.get("reasoning", "")
        rag_reasoning = rag_result.get("reasoning", "")
        
        if ki_reasoning and rag_reasoning:
            combined_reasoning = f"Knowledge Injection: {ki_reasoning} | RAG: {rag_reasoning}"
        elif ki_reasoning:
            combined_reasoning = ki_reasoning
        else:
            combined_reasoning = rag_reasoning
        
        # Determine severity
        if final_flagged:
            severity = "high" if confidence > 0.8 else "medium"
        else:
            severity = "low"
        
        return {
            "flagged": final_flagged,
            "confidence": confidence,
            "detected_words": detected_words,
            "categories": categories,
            "context_analysis": f"Combined analysis using {detection_method}",
            "alternatives": alternatives,
            "severity": severity,
            "reasoning": combined_reasoning,
            "detection_method": detection_method,
            "knowledge_injection_result": ki_result,
            "rag_result": rag_result
        }

# Test the hybrid system
if __name__ == "__main__":
    moderator = HybridModerator()
    
    test_messages = [
        "Women are too emotional for leadership",
        "That slut is annoying",
        "She's a great leader",
        "Girls can't handle pressure"
    ]
    
    for message in test_messages:
        print(f"\n🧪 Testing: '{message}'")
        result = moderator.analyze_message(message)
        print(f"   Flagged: {result['flagged']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Method: {result.get('detection_method', 'unknown')}")
        print(f"   Words: {result['detected_words']}") 