#!/usr/bin/env python3
"""
Context-Aware Alternative Generator
Provides intelligent, tone-appropriate alternatives based on context
"""

import re
from typing import Dict, List, Tuple
import ollama

class ContextAnalyzer:
    """Analyzes message context and provides intelligent alternatives"""
    
    def __init__(self):
        self.tone_indicators = {
            'negative': ['such', 'so', 'very', 'really', 'totally', 'completely', 'absolutely'],
            'positive': ['great', 'amazing', 'wonderful', 'fantastic', 'awesome'],
            'casual': ['hey', 'yo', 'dude', 'bro', 'man', 'girl', 'babe'],
            'formal': ['sir', 'madam', 'ma\'am', 'please', 'thank you'],
            'playful': ['haha', 'lol', 'omg', 'wow', 'cool', 'nice'],
            'aggressive': ['stupid', 'idiot', 'moron', 'hate', 'terrible', 'awful']
        }
        
        self.context_patterns = {
            'insult': r'\b(such|so|very|really|totally|completely|absolutely)\s+\w+\b',
            'compliment': r'\b(great|amazing|wonderful|fantastic|awesome)\s+\w+\b',
            'casual_greeting': r'\b(hey|yo|hi|hello)\s+\w+\b',
            'professional': r'\b(professional|colleague|team|work|office)\b',
            'friendly': r'\b(friend|buddy|pal|mate)\b'
        }
    
    def analyze_context(self, message: str, detected_word: str) -> Dict:
        """Analyze the context around a detected word"""
        message_lower = message.lower()
        word_lower = detected_word.lower()
        
        # Find the word position
        word_pos = message_lower.find(word_lower)
        if word_pos == -1:
            return {'tone': 'neutral', 'context': 'unknown', 'intent': 'unclear'}
        
        # Analyze surrounding context
        context_start = max(0, word_pos - 50)
        context_end = min(len(message), word_pos + len(word_lower) + 50)
        context = message_lower[context_start:context_end]
        
        # Determine tone
        tone = self._determine_tone(context)
        
        # Determine context type
        context_type = self._determine_context_type(context, word_lower)
        
        # Determine intent
        intent = self._determine_intent(context, word_lower)
        
        return {
            'tone': tone,
            'context': context_type,
            'intent': intent,
            'surrounding_text': context
        }
    
    def _determine_tone(self, context: str) -> str:
        """Determine the overall tone of the context"""
        tone_scores = {}
        
        for tone, indicators in self.tone_indicators.items():
            score = sum(1 for indicator in indicators if indicator in context)
            tone_scores[tone] = score
        
        # Find the dominant tone
        if tone_scores:
            dominant_tone = max(tone_scores, key=tone_scores.get)
            if tone_scores[dominant_tone] > 0:
                return dominant_tone
        
        return 'neutral'
    
    def _determine_context_type(self, context: str, word: str) -> str:
        """Determine the type of context"""
        if any(pattern in context for pattern in ['work', 'office', 'professional', 'colleague']):
            return 'professional'
        elif any(pattern in context for pattern in ['friend', 'buddy', 'pal', 'mate']):
            return 'friendly'
        elif any(pattern in context for pattern in ['hey', 'yo', 'hi', 'hello']):
            return 'casual'
        elif any(pattern in context for pattern in ['such', 'so', 'very', 'really']):
            return 'emphatic'
        else:
            return 'general'
    
    def _determine_intent(self, context: str, word: str) -> str:
        """Determine the intent behind using the word"""
        if any(word in context for word in ['hate', 'terrible', 'awful', 'stupid']):
            return 'insult'
        elif any(word in context for word in ['love', 'great', 'amazing', 'wonderful']):
            return 'compliment'
        elif any(word in context for word in ['haha', 'lol', 'omg', 'wow']):
            return 'playful'
        else:
            return 'neutral'
    
    def get_contextual_alternatives(self, word: str, context_analysis: Dict) -> List[str]:
        """Get contextually appropriate alternatives"""
        
        # Define alternatives by context and tone
        alternatives_by_context = {
            'bitch': {
                'professional': {
                    'negative': ['difficult colleague', 'challenging person', 'demanding individual'],
                    'neutral': ['assertive person', 'strong personality', 'direct individual'],
                    'positive': ['determined professional', 'focused colleague', 'driven individual']
                },
                'friendly': {
                    'negative': ['jerk', 'bully', 'mean person', 'difficult friend'],
                    'neutral': ['drama queen', 'diva', 'sassy one', 'bossy friend'],
                    'positive': ['badass', 'fierce friend', 'bold personality', 'strong-willed']
                },
                'casual': {
                    'negative': ['jerk', 'bully', 'brat', 'mean person'],
                    'neutral': ['drama queen', 'diva', 'sassy one', 'queen bee'],
                    'positive': ['badass', 'fierce', 'bold', 'independent']
                },
                'general': {
                    'negative': ['difficult person', 'challenging individual', 'demanding person'],
                    'neutral': ['assertive person', 'strong personality', 'direct individual'],
                    'positive': ['determined person', 'focused individual', 'driven person']
                }
            },
            'slut': {
                'professional': {
                    'negative': ['unprofessional person', 'inappropriate colleague', 'promiscuous individual'],
                    'neutral': ['social person', 'outgoing individual', 'networker'],
                    'positive': ['sociable professional', 'people person', 'social butterfly']
                },
                'friendly': {
                    'negative': ['player', 'flirt', 'promiscuous person', 'cheater'],
                    'neutral': ['social person', 'outgoing friend', 'people person'],
                    'positive': ['sociable friend', 'networker', 'popular person', 'social butterfly']
                },
                'casual': {
                    'negative': ['player', 'flirt', 'hoe', 'thot', 'easy'],
                    'neutral': ['social person', 'outgoing individual', 'people person'],
                    'positive': ['sociable person', 'networker', 'popular individual', 'baddie']
                },
                'general': {
                    'negative': ['inappropriate person', 'unprofessional individual', 'promiscuous person'],
                    'neutral': ['social person', 'outgoing individual', 'people person'],
                    'positive': ['sociable person', 'networker', 'popular individual']
                }
            },
            'whore': {
                'professional': {
                    'negative': ['unprofessional person', 'inappropriate colleague', 'promiscuous individual'],
                    'neutral': ['social person', 'outgoing individual', 'networker'],
                    'positive': ['sociable professional', 'people person', 'social butterfly']
                },
                'friendly': {
                    'negative': ['player', 'flirt', 'promiscuous person', 'cheater'],
                    'neutral': ['social person', 'outgoing friend', 'people person'],
                    'positive': ['sociable friend', 'networker', 'popular person', 'social butterfly']
                },
                'casual': {
                    'negative': ['player', 'flirt', 'hoe', 'thot', 'easy'],
                    'neutral': ['social person', 'outgoing individual', 'people person'],
                    'positive': ['sociable person', 'networker', 'popular individual', 'baddie']
                },
                'general': {
                    'negative': ['inappropriate person', 'unprofessional individual', 'promiscuous person'],
                    'neutral': ['social person', 'outgoing individual', 'people person'],
                    'positive': ['sociable person', 'networker', 'popular individual']
                }
            },
            'emotional': {
                'professional': {
                    'negative': ['reactive', 'overly sensitive', 'easily upset', 'unstable'],
                    'neutral': ['expressive', 'passionate', 'caring', 'sensitive'],
                    'positive': ['empathetic', 'compassionate', 'understanding', 'intuitive']
                },
                'friendly': {
                    'negative': ['dramatic', 'overly sensitive', 'easily upset', 'unstable'],
                    'neutral': ['expressive', 'passionate', 'caring', 'sensitive'],
                    'positive': ['empathetic', 'compassionate', 'understanding', 'intuitive']
                },
                'casual': {
                    'negative': ['dramatic', 'overly sensitive', 'easily upset', 'unstable'],
                    'neutral': ['expressive', 'passionate', 'caring', 'sensitive'],
                    'positive': ['empathetic', 'compassionate', 'understanding', 'intuitive']
                },
                'general': {
                    'negative': ['reactive', 'overly sensitive', 'easily upset', 'unstable'],
                    'neutral': ['expressive', 'passionate', 'caring', 'sensitive'],
                    'positive': ['empathetic', 'compassionate', 'understanding', 'intuitive']
                }
            },
            'hysterical': {
                'professional': {
                    'negative': ['overreacting', 'being dramatic', 'overly concerned'],
                    'neutral': ['upset', 'concerned', 'worried'],
                    'positive': ['passionate', 'caring', 'invested']
                },
                'friendly': {
                    'negative': ['overreacting', 'being dramatic', 'freaking out'],
                    'neutral': ['upset', 'concerned', 'worried'],
                    'positive': ['passionate', 'caring', 'invested']
                },
                'casual': {
                    'negative': ['overreacting', 'being dramatic', 'freaking out'],
                    'neutral': ['upset', 'concerned', 'worried'],
                    'positive': ['passionate', 'caring', 'invested']
                },
                'general': {
                    'negative': ['overreacting', 'being dramatic', 'overly concerned'],
                    'neutral': ['upset', 'concerned', 'worried'],
                    'positive': ['passionate', 'caring', 'invested']
                }
            }
        }
        
        # Get alternatives for the specific word and context
        word_alternatives = alternatives_by_context.get(word.lower(), {})
        context_alternatives = word_alternatives.get(context_analysis['context'], {})
        tone_alternatives = context_alternatives.get(context_analysis['tone'], [])
        
        # Fallback alternatives if no specific context found
        if not tone_alternatives:
            tone_alternatives = context_alternatives.get('neutral', [])
        
        if not tone_alternatives:
            tone_alternatives = ['person', 'individual', 'someone']  # Generic fallback
        
        return tone_alternatives[:5]  # Return top 5 alternatives
    
    def generate_ai_enhanced_alternatives(self, message: str, detected_word: str, context_analysis: Dict) -> List[str]:
        """Use AI to generate even more contextually appropriate alternatives"""
        
        prompt = f"""
You are an expert at providing contextually appropriate word alternatives for content moderation.

Original message: "{message}"
Detected word: "{detected_word}"
Context analysis: {context_analysis}

Based on the context, provide 3-5 alternative words or phrases that:

1. **Match the tone and intent** of the original message
2. **Are appropriate for the context** (professional/friendly/casual)
3. **Convey similar meaning** but without being problematic
4. **Are specific and meaningful**, not generic like "person" or "individual"
5. **Consider the speaker's intent** - if they're being negative, provide milder negative alternatives; if positive, provide empowering alternatives

**Context Guidelines:**
- Professional context: Use formal, workplace-appropriate terms
- Friendly context: Use casual but respectful terms
- Casual context: Use slang or informal terms that aren't offensive
- Negative tone: Provide milder alternatives that still convey the sentiment
- Positive tone: Provide empowering or neutral alternatives

**Examples:**
- "bitch" in professional context → "difficult colleague", "challenging person"
- "bitch" in friendly context → "drama queen", "sassy friend", "diva"
- "slut" in casual context → "player", "flirt", "social butterfly"
- "emotional" in negative context → "reactive", "overly sensitive"
- "emotional" in positive context → "empathetic", "compassionate"

Respond with only a JSON array of alternatives:
["alternative1", "alternative2", "alternative3"]
"""
        
        try:
            response = ollama.chat(model='llama3', messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            content = response['message']['content']
            
            # Try to extract JSON from response
            import json
            import re
            
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                alternatives = json.loads(json_match.group())
                return alternatives[:5]
            
        except Exception as e:
            print(f"AI alternative generation failed: {e}")
        
        # Fallback to rule-based alternatives
        return self.get_contextual_alternatives(detected_word, context_analysis) 