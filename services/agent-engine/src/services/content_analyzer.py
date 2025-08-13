"""Content Analyzer Service for interaction analysis"""

from typing import Dict, List, Any
import re
import logging

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Service for analyzing interaction content and extracting metadata"""
    
    def __init__(self):
        # Define keyword mappings for topic detection
        self.topic_keywords = {
            "payment": ["payment", "pay", "amount", "balance", "owe", "debt"],
            "collection": ["collection", "collect", "agency", "collector", "recovery"],
            "dispute": ["dispute", "disagree", "incorrect", "wrong", "error", "mistake"],
            "hardship": ["hardship", "difficult", "struggle", "unemployed", "medical", "disability"],
            "settlement": ["settle", "settlement", "offer", "negotiate", "deal"],
            "verification": ["verify", "proof", "validate", "documentation", "evidence"],
            "bankruptcy": ["bankruptcy", "chapter 7", "chapter 13", "discharge"],
            "legal": ["lawyer", "attorney", "sue", "court", "lawsuit", "legal"],
            "complaint": ["complaint", "complain", "report", "violation", "abuse"],
            "identity": ["identity", "fraud", "stolen", "not mine", "wrong person"]
        }
        
        # Define regulatory indicator patterns
        self.regulatory_patterns = {
            "fdcpa": [
                r"\bdebt\b", r"\bcollect", r"\bcollector\b", r"\bagency\b",
                r"\bowe\b", r"\bpayment\b", r"\bbalance\b"
            ],
            "tcpa": [
                r"\bcall\b", r"\bphone\b", r"\brobocall\b", r"\bautodialer\b",
                r"\bdo not call\b", r"\bstop calling\b", r"\btext message\b"
            ],
            "fcra": [
                r"\bcredit report\b", r"\bcredit score\b", r"\bdispute\b",
                r"\binaccurate\b", r"\breporting\b", r"\bcredit bureau\b"
            ],
            "reg_f": [
                r"\btime restriction\b", r"\b8am\b", r"\b9pm\b", r"\bworkplace\b",
                r"\bemail\b", r"\bsocial media\b", r"\belectronic communication\b"
            ]
        }
        
    def detect_language(self, interaction_data: Dict[str, Any]) -> str:
        """
        Detect the language of the interaction
        
        For now, returns 'en' as default. In production, would use language detection library.
        """
        # Simple implementation - could integrate with language detection library
        content = interaction_data.get("content", "").lower()
        
        # Basic language detection based on common words
        spanish_indicators = ["hola", "gracias", "por favor", "señor", "señora"]
        if any(word in content for word in spanish_indicators):
            return "es"
        
        return "en"
    
    async def extract_topics(self, interaction_data: Dict[str, Any]) -> List[str]:
        """
        Extract relevant topics from the interaction content
        
        Returns a list of detected topic categories
        """
        content = interaction_data.get("content", "").lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                detected_topics.append(topic)
        
        # Also check metadata for additional context
        metadata = interaction_data.get("metadata", {})
        if metadata.get("interaction_type") == "collection_call":
            if "collection" not in detected_topics:
                detected_topics.append("collection")
        
        logger.debug(f"Detected topics: {detected_topics}")
        return detected_topics
    
    async def detect_regulatory_context(self, interaction_data: Dict[str, Any]) -> List[str]:
        """
        Detect regulatory compliance indicators in the content
        
        Returns a list of applicable regulations
        """
        content = interaction_data.get("content", "").lower()
        detected_indicators = []
        
        for regulation, patterns in self.regulatory_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if regulation not in detected_indicators:
                        detected_indicators.append(regulation)
                    break
        
        # Check interaction type for additional context
        interaction_type = interaction_data.get("type", "")
        if interaction_type == "collection_call" and "fdcpa" not in detected_indicators:
            detected_indicators.append("fdcpa")
        
        logger.debug(f"Detected regulatory indicators: {detected_indicators}")
        return detected_indicators
    
    async def assess_complexity(self, interaction_data: Dict[str, Any]) -> float:
        """
        Assess the complexity of the interaction
        
        Returns a complexity score between 0 and 1
        """
        content = interaction_data.get("content", "")
        metadata = interaction_data.get("metadata", {})
        
        # Base complexity on content length
        content_length = len(content)
        if content_length < 500:
            length_score = 0.3
        elif content_length < 1500:
            length_score = 0.6
        else:
            length_score = 0.9
        
        # Adjust for other factors
        complexity_score = length_score
        
        # Increase complexity for longer duration
        duration = metadata.get("duration", 0)
        if duration > 600:  # More than 10 minutes
            complexity_score = min(1.0, complexity_score + 0.2)
        elif duration > 300:  # More than 5 minutes
            complexity_score = min(1.0, complexity_score + 0.1)
        
        # Increase complexity for multiple participants
        participants = metadata.get("participants", 1)
        if participants > 2:
            complexity_score = min(1.0, complexity_score + 0.1)
        
        # Increase complexity for certain topics
        topics = await self.extract_topics(interaction_data)
        complex_topics = ["legal", "bankruptcy", "complaint", "dispute"]
        if any(topic in complex_topics for topic in topics):
            complexity_score = min(1.0, complexity_score + 0.15)
        
        logger.debug(f"Assessed complexity score: {complexity_score}")
        return complexity_score
    
    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract named entities from content (names, amounts, dates, etc.)
        
        This is a simplified implementation. In production, would use NLP libraries.
        """
        entities = {
            "amounts": [],
            "dates": [],
            "phone_numbers": [],
            "account_numbers": []
        }
        
        # Extract dollar amounts
        amount_pattern = r'\$[\d,]+(?:\.\d{2})?'
        entities["amounts"] = re.findall(amount_pattern, content)
        
        # Extract dates (simple pattern)
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
        entities["dates"] = re.findall(date_pattern, content)
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        entities["phone_numbers"] = re.findall(phone_pattern, content)
        
        # Extract potential account numbers (digits with specific lengths)
        account_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        entities["account_numbers"] = re.findall(account_pattern, content)
        
        return entities
    
    def calculate_sentiment(self, content: str) -> Dict[str, float]:
        """
        Calculate sentiment scores for the content
        
        Returns sentiment scores for different aspects
        """
        # Simplified sentiment analysis
        negative_words = [
            "angry", "upset", "frustrated", "annoyed", "mad", "terrible",
            "horrible", "awful", "disgusting", "hate", "worst", "unacceptable"
        ]
        
        positive_words = [
            "thank", "appreciate", "helpful", "good", "great", "excellent",
            "wonderful", "pleased", "happy", "satisfied", "resolved"
        ]
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        negative_count = sum(1 for word in negative_words if word in content_lower)
        positive_count = sum(1 for word in positive_words if word in content_lower)
        
        # Calculate scores
        if word_count > 0:
            negativity = min(1.0, negative_count / (word_count * 0.05))
            positivity = min(1.0, positive_count / (word_count * 0.05))
        else:
            negativity = 0.0
            positivity = 0.0
        
        # Overall sentiment
        if negativity > positivity:
            overall = -negativity
        elif positivity > negativity:
            overall = positivity
        else:
            overall = 0.0
        
        return {
            "overall": overall,
            "negativity": negativity,
            "positivity": positivity,
            "neutrality": 1.0 - max(negativity, positivity)
        }