import json
import ollama
from typing import Dict, List, Tuple, Optional
import re
import requests
import time
import os
from ..utils.context_analyzer import ContextAnalyzer

class KnowledgeInjectionModerator:
    def __init__(self, knowledge_base_path: str = "data/knowledge_base/misogyny_knowledge_base.json"):
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.model = "llama3:8b"  # Updated to use llama3:8b
        self.context_analyzer = ContextAnalyzer()
        self.ollama_available = self._check_ollama_availability()
        
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and working"""
        try:
            import ollama
            # Try to list models to test connection
            models = ollama.list()
            print("✅ Ollama connection successful")
            return True
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
            print("🔄 System will use fallback mode (keyword matching)")
            return False
    
    def load_knowledge_base(self, path: str) -> Dict:
        """Load the knowledge base from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge base not found at {path}")
            return {}
    
    def create_knowledge_injection_prompt(self, message: str) -> str:
        """Create a comprehensive prompt with knowledge base injection"""
        
        # Build context from knowledge base
        context = self.build_context()
        
        prompt = f"""
You are an expert content moderator specializing in detecting misogynistic language. Use the following knowledge base to analyze the message:

{context}

MESSAGE TO ANALYZE: "{message}"

TASK: Analyze this message for misogynistic language using the knowledge base above.

INSTRUCTIONS:
1. Check if any words from the knowledge base appear in the message
2. Consider the context - some words can be offensive or acceptable depending on usage
3. Look for patterns that match the categories in the knowledge base
4. Consider power dynamics and intent vs impact

RESPOND WITH JSON ONLY:
{{
    "flagged": true/false,
    "confidence": 0.0-1.0,
    "detected_words": ["list", "of", "detected", "words"],
    "categories": ["list", "of", "categories"],
    "context_analysis": "explanation of why it's flagged or not",
    "alternatives": ["suggested", "replacement", "words"],
    "severity": "low/medium/high",
    "reasoning": "detailed explanation of the analysis"
}}

IMPORTANT: You MUST include the "alternatives" field with 3-5 suggested replacement words or phrases, even if the message is not flagged.

Focus on accuracy and provide detailed reasoning for your decision.
"""
        return prompt
    
    def build_context(self) -> str:
        """Build context string from knowledge base"""
        context_parts = []
        
        for category_name, category_data in self.knowledge_base.get("categories", {}).items():
            context_parts.append(f"CATEGORY: {category_name}")
            context_parts.append(f"Description: {category_data['description']}")
            context_parts.append(f"Words: {', '.join(category_data['words'])}")
            context_parts.append(f"Alternatives: {', '.join(category_data['alternatives'])}")
            
            # Add example contexts
            if 'context_examples' in category_data:
                context_parts.append("Offensive examples:")
                for example in category_data['context_examples'].get('offensive', []):
                    context_parts.append(f"  - {example}")
                context_parts.append("Acceptable examples:")
                for example in category_data['context_examples'].get('acceptable', []):
                    context_parts.append(f"  - {example}")
            context_parts.append("")
        
        # Add guidelines
        if 'guidelines' in self.knowledge_base:
            context_parts.append("GUIDELINES:")
            for guideline, description in self.knowledge_base['guidelines'].items():
                context_parts.append(f"- {description}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def parse_llama_response(self, response: str) -> Dict:
        """Parse the JSON response from Llama"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                print(f"Raw Llama response: {response}")
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Error parsing Llama response: {e}")
            return None  # Return None to trigger fallback
    
    def fallback_analysis(self, message: str) -> Dict:
        """Fallback analysis using simple keyword matching with contextual alternatives"""
        detected_words = []
        categories = []
        
        # More context-aware keyword matching
        message_lower = message.lower()
        
        # Only flag if words are used in problematic contexts
        problematic_patterns = {
            "derogatory_terms": ["bitch", "slut", "whore", "cunt"],
            "devaluing_language": ["bossy", "hysterical", "irrational", "dramatic"],
            "stereotypical_portrayals": ["run like a girl", "act like a lady", "man up"],
            "objectification": ["hot babe", "sexy", "doll"],
            "achievement_undermining": ["girlboss", "good girl", "diversity hire"],
            "infantilizing_language": ["little lady", "good girl", "sweetie"],
            "dismissive_language": ["crazy", "nuts", "psycho", "drama queen"]
        }
        
        # Check for problematic patterns
        for category, words in problematic_patterns.items():
            for word in words:
                if word.lower() in message_lower:
                    detected_words.append(word)
                    if category not in categories:
                        categories.append(category)
        
        # Don't flag common words like "girl", "beautiful", "pretty", "lady" unless in problematic context
        # Additional context check for common words
        if detected_words and len(detected_words) == 1:
            word = detected_words[0].lower()
            # Don't flag these words in simple greetings or compliments
            safe_words = ["girl", "beautiful", "pretty", "cute", "lady", "woman", "gorgeous", "stunning"]
            if word in safe_words and len(message.split()) <= 4:
                flagged = False
                detected_words = []
                categories = []
        
        flagged = len(detected_words) > 0
        
        # Generate contextual alternatives
        contextual_alternatives = self._generate_contextual_alternatives(message, detected_words)
        
        return {
            "flagged": flagged,
            "confidence": 0.7 if flagged else 0.9,
            "detected_words": detected_words,
            "categories": categories,
            "context_analysis": f"Detected {len(detected_words)} potentially problematic words",
            "alternatives": contextual_alternatives,
            "severity": "medium" if flagged else "low",
            "reasoning": "Fallback analysis using keyword matching"
        }
    
    def _generate_contextual_alternatives(self, message: str, detected_words: List[str]) -> List[str]:
        """Generate contextually intelligent alternatives using AI and context analysis"""
        alternatives = []
        
        for word in detected_words:
            # Analyze context around the detected word
            context_analysis = self.context_analyzer.analyze_context(message, word)
            
            print(f"🔍 Context Analysis for '{word}':")
            print(f"   Tone: {context_analysis['tone']}")
            print(f"   Context: {context_analysis['context']}")
            print(f"   Intent: {context_analysis['intent']}")
            
            # Try AI-enhanced alternatives first
            try:
                ai_alternatives = self.context_analyzer.generate_ai_enhanced_alternatives(
                    message, word, context_analysis
                )
                alternatives.extend(ai_alternatives)
                print(f"   AI Alternatives: {ai_alternatives}")
            except Exception as e:
                print(f"   AI alternatives failed: {e}")
                # Fallback to rule-based alternatives
                rule_alternatives = self.context_analyzer.get_contextual_alternatives(word, context_analysis)
                alternatives.extend(rule_alternatives)
                print(f"   Rule Alternatives: {rule_alternatives}")
        
        # Remove duplicates and limit
        unique_alternatives = list(dict.fromkeys(alternatives))  # Preserve order
        return unique_alternatives[:5]  # Limit to 5 alternatives
    
    def get_alternatives_for_word(self, word: str) -> List[str]:
        """Get specific alternatives for a detected word"""
        word_alternatives = {
            # Derogatory terms
            "slut": ["person", "woman", "individual", "someone"],
            "bitch": ["person", "woman", "individual", "someone"],
            "whore": ["person", "woman", "individual", "someone"],
            "cunt": ["person", "woman", "individual", "someone"],
            
            # Devaluing language
            "bossy": ["assertive", "confident", "decisive", "direct"],
            "abrasive": ["direct", "straightforward", "clear", "focused"],
            "emotional": ["passionate", "expressive", "enthusiastic", "caring"],
            "hysterical": ["upset", "concerned", "worried", "distressed"],
            "irrational": ["thoughtful", "considerate", "reasonable", "logical"],
            "dramatic": ["expressive", "enthusiastic", "passionate", "caring"],
            "difficult": ["focused", "determined", "thorough", "careful"],
            "demanding": ["thorough", "focused", "determined", "careful"],
            
            # Stereotypical portrayals (only problematic phrases)
            "run like a girl": ["run with determination", "run with skill"],
            "act like a lady": ["be confident", "be professional"],
            "man up": ["be strong", "be brave", "show courage"],
            
            # Objectification (only problematic terms)
            "hot babe": ["attractive person", "beautiful woman", "stunning individual"],
            "doll": ["person", "woman", "individual", "someone"],
            "sweetie": ["person", "colleague", "friend", "someone"],
            "honey": ["person", "colleague", "friend", "someone"],
            
            # Achievement undermining
            "girlboss": ["leader", "boss", "manager", "executive"],
            "good girl": ["colleague", "professional", "peer", "person"],
            "dear": ["colleague", "professional", "peer", "person"],
            "darling": ["colleague", "professional", "peer", "person"],
            "miss": ["colleague", "professional", "peer", "person"],
            "young lady": ["colleague", "professional", "peer", "person"],
            
            # Relationship defining
            "spinster": ["professional", "individual", "person", "colleague"],
            "barren": ["professional", "individual", "person", "colleague"],
            "housewife": ["professional", "individual", "person", "colleague"],
            "soccer mom": ["parent", "professional", "individual", "person"],
            "mama": ["parent", "professional", "individual", "person"],
            "mommy": ["parent", "professional", "individual", "person"],
            "wife": ["partner", "professional", "individual", "person"],
            "girlfriend": ["partner", "professional", "individual", "person"],
            "old maid": ["professional", "individual", "person", "colleague"],
            "unmarried": ["professional", "individual", "person", "colleague"],
            "childless": ["professional", "individual", "person", "colleague"],
            
            # Infantilizing language
            "little lady": ["colleague", "professional", "peer", "person"],
            "baby": ["person", "individual", "someone", "colleague"],
            "sweetheart": ["person", "colleague", "friend", "someone"],
            
            # Sexualization
            "smile": ["be professional", "be confident", "be yourself"],
            "dress appropriately": ["be professional", "be confident", "be yourself"],
            "wear something nice": ["be professional", "be confident", "be yourself"],
            
            # Dismissive language
            "crazy": ["passionate", "concerned", "thoughtful", "caring"],
            "nuts": ["passionate", "concerned", "thoughtful", "caring"],
            "psycho": ["passionate", "concerned", "thoughtful", "caring"],
            "overreacting": ["concerned", "thoughtful", "caring", "expressive"],
            "making a fuss": ["concerned", "thoughtful", "caring", "expressive"],
            "being difficult": ["focused", "determined", "thorough", "careful"],
            "drama queen": ["expressive person", "passionate individual", "enthusiastic person", "caring individual"],
            "queen": ["person", "individual", "someone", "woman"]
        }
        
        return word_alternatives.get(word.lower(), ["person", "individual", "someone"])
    
    def analyze_message(self, message: str, user_id: str = "default_user") -> Dict:
        """Analyze a message using Knowledge Injection with Llama 3"""
        # Check if Ollama is available
        if not self.ollama_available:
            print("🔄 Using fallback mode (Ollama not available)")
            return self.fallback_analysis(message)
        
        try:
            # Try Llama 3 analysis first
            result = self._analyze_with_llama(message)
            if result:
                return result
            else:
                # Fallback to keyword matching if Llama 3 fails
                print("⚠️ Llama 3 analysis failed, using fallback")
                return self.fallback_analysis(message)
        except Exception as e:
            print(f"Analysis failed: {e}")
            # Fallback to keyword matching
            print("⚠️ Falling back to keyword matching")
            return self.fallback_analysis(message)
    
    def get_alternatives(self, categories: List[str]) -> List[str]:
        """Get alternative words for detected categories"""
        alternatives = []
        for category in categories:
            if category in self.knowledge_base.get("categories", {}):
                alternatives.extend(self.knowledge_base["categories"][category].get("alternatives", []))
        return list(set(alternatives))  # Remove duplicates
    
    def get_training_content(self, category: str = None) -> Dict:
        """Get training content for users"""
        if category and category in self.knowledge_base.get("categories", {}):
            return {
                "category": category,
                "description": self.knowledge_base["categories"][category]["description"],
                "impact": self.knowledge_base.get("training_materials", {}).get("impact_explanation", "")
            }
        else:
            return {
                "general_impact": self.knowledge_base.get("training_materials", {}).get("impact_explanation", ""),
                "workplace_impact": self.knowledge_base.get("training_materials", {}).get("workplace_impact", ""),
                "psychological_impact": self.knowledge_base.get("training_materials", {}).get("psychological_impact", "")
            } 

    def _analyze_with_llama(self, message: str) -> Dict:
        """Test direct Llama 3 analysis with different prompting strategies"""
        
        # Strategy 1: Academic analysis prompt
        academic_prompt = f"""
You are a content moderation expert. Analyze this message for potentially problematic language patterns.

Message: "{message}"

Consider:
- Context and intent
- Power dynamics
- Gender stereotypes
- Harmful language patterns

Respond with JSON only:
{{
    "flagged": true/false,
    "detected_words": ["word1", "word2"],
    "categories": ["category1", "category2"],
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "alternatives": ["suggested", "replacement", "words"]
}}
"""
        
        # Strategy 2: Research analysis prompt
        research_prompt = f"""
As a researcher studying communication patterns, analyze this message:

"{message}"

Identify any language that might:
- Reinforce gender stereotypes
- Use derogatory terms
- Employ problematic patterns

Return JSON:
{{
    "flagged": boolean,
    "detected_words": [list],
    "categories": [list],
    "confidence": float,
    "reasoning": "string",
    "alternatives": [list]
}}
"""
        
        # Strategy 3: Neutral analysis prompt
        neutral_prompt = f"""
Analyze this message for content patterns:

"{message}"

Return analysis in JSON format:
{{
    "flagged": true/false,
    "detected_words": [],
    "categories": [],
    "confidence": 0.0,
    "reasoning": "",
    "alternatives": []
}}
"""
        
        strategies = [
            ("Academic", academic_prompt),
            ("Research", research_prompt),
            ("Neutral", neutral_prompt)
        ]
        
        for strategy_name, prompt in strategies:
            try:
                print(f"Testing {strategy_name} strategy...")
                response = ollama.chat(model='llama3', messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ])
                
                # Try to extract JSON
                content = response['message']['content']
                print(f"Response: {content}")
                
                # Look for JSON in response
                try:
                    # Find JSON in the response
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        result = json.loads(json_str)
                        
                        # Use context-aware alternatives
                        detected_words = result.get('detected_words', [])
                        
                        # Override overly aggressive Llama 3 responses for safe words
                        safe_words = ["girl", "beautiful", "pretty", "cute", "lady", "woman", "gorgeous", "stunning"]
                        if detected_words and len(detected_words) == 1:
                            word = detected_words[0].lower()
                            if word in safe_words and len(message.split()) <= 4:
                                # Override Llama 3's overly aggressive response
                                result['flagged'] = False
                                result['detected_words'] = []
                                result['categories'] = []
                                result['confidence'] = 0.9
                                result['reasoning'] = "Safe word used in appropriate context"
                                result['alternatives'] = []
                                print(f"✅ {strategy_name} strategy worked! (Overridden for safe word)")
                                return result
                        
                        result['alternatives'] = self._generate_contextual_alternatives(message, detected_words)
                        
                        print(f"✅ {strategy_name} strategy worked!")
                        return result
                except json.JSONDecodeError:
                    print(f"❌ {strategy_name} strategy failed to parse JSON")
                    continue
                    
            except Exception as e:
                print(f"❌ {strategy_name} strategy error: {e}")
                continue
        
        print("❌ All Llama 3 strategies failed")
        return None 
    
    def _generate_alternatives_for_detected_words(self, detected_words: List[str]) -> List[str]:
        """Generate alternatives for detected words"""
        alternatives = []
        for word in detected_words:
            word_alternatives = self.get_alternatives_for_word(word)
            alternatives.extend(word_alternatives)
        return list(set(alternatives))[:5]  # Remove duplicates and limit to 5

 