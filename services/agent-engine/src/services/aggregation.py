"""Result Aggregation Service for combining agent outputs"""

from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Standardized analysis result format"""
    analysis_id: str
    overall_score: float
    confidence: float
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    categories: Dict[str, float]
    audit_trail: Dict[str, Any]
    execution_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "analysis_id": self.analysis_id,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "categories": self.categories,
            "audit_trail": self.audit_trail,
            "execution_time": self.execution_time
        }


class ResultAggregator:
    """Service for aggregating multiple agent results into final analysis"""
    
    def __init__(self):
        self.default_weights = {
            "compliance": 0.4,
            "quality": 0.3,
            "identity": 0.2,
            "risk": 0.1
        }
    
    async def aggregate(
        self, 
        agent_results: Dict[str, Any], 
        aggregation_rules: Dict[str, Any],
        thresholds: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Aggregate individual agent results into final analysis
        
        This is a stub implementation. Will be fully implemented in R2-T4.
        
        Args:
            agent_results: Dictionary of agent outputs keyed by agent name
            aggregation_rules: Rules for combining scores
            thresholds: Pass/fail/review thresholds
            
        Returns:
            Aggregated AnalysisResult
        """
        logger.info(f"Aggregating results from {len(agent_results)} agents")
        
        # Extract valid results (exclude errors)
        valid_results = {
            name: result 
            for name, result in agent_results.items() 
            if isinstance(result, dict) and "error" not in result
        }
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(valid_results, aggregation_rules)
        
        # Calculate confidence
        confidence = self._calculate_confidence(valid_results)
        
        # Aggregate violations
        all_violations = self._aggregate_violations(valid_results)
        
        # Aggregate recommendations
        all_recommendations = self._aggregate_recommendations(valid_results)
        
        # Calculate category scores
        categories = self._calculate_category_scores(valid_results)
        
        # Calculate total execution time
        execution_time = sum(
            result.get("execution_time", 0) 
            for result in valid_results.values()
        )
        
        # Build audit trail
        audit_trail = self._build_audit_trail(agent_results, aggregation_rules)
        
        return AnalysisResult(
            analysis_id=f"analysis-{datetime.now().isoformat()}",
            overall_score=overall_score,
            confidence=confidence,
            violations=all_violations,
            recommendations=all_recommendations,
            categories=categories,
            audit_trail=audit_trail,
            execution_time=execution_time
        )
    
    def _calculate_overall_score(
        self, 
        results: Dict[str, Any], 
        rules: Dict[str, Any]
    ) -> float:
        """Calculate weighted overall score from agent results"""
        
        if not results:
            return 0.0
        
        # Get weights from rules or use defaults
        weights = rules.get("weights", {})
        
        total_weight = 0
        weighted_sum = 0
        
        for agent_name, result in results.items():
            score = result.get("score", 0)
            
            # Determine weight for this agent
            agent_type = self._get_agent_type(agent_name)
            weight = weights.get(agent_type, self.default_weights.get(agent_type, 1.0))
            
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            # Simple average if no weights
            scores = [r.get("score", 0) for r in results.values()]
            overall_score = sum(scores) / len(scores) if scores else 0
        
        return round(overall_score, 2)
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate aggregate confidence score"""
        
        if not results:
            return 0.0
        
        confidences = [
            result.get("confidence", 0.5) 
            for result in results.values()
        ]
        
        # Weighted average based on individual confidences
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            
            # Adjust for consistency between agents
            variance = self._calculate_variance(confidences)
            consistency_factor = max(0.7, 1.0 - variance * 0.5)
            
            return round(avg_confidence * consistency_factor, 3)
        
        return 0.5
    
    def _aggregate_violations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine and deduplicate violations from all agents"""
        
        all_violations = []
        seen_violations = set()
        
        for agent_name, result in results.items():
            violations = result.get("violations", [])
            
            for violation in violations:
                # Create unique key for deduplication
                violation_key = (
                    violation.get("regulation", ""),
                    violation.get("section", ""),
                    violation.get("description", "")
                )
                
                if violation_key not in seen_violations:
                    seen_violations.add(violation_key)
                    
                    # Add agent source
                    violation_with_source = {
                        **violation,
                        "detected_by": agent_name,
                        "confidence": result.get("confidence", 0.5)
                    }
                    all_violations.append(violation_with_source)
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_violations.sort(
            key=lambda v: severity_order.get(v.get("severity", "low"), 99)
        )
        
        return all_violations
    
    def _aggregate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine and prioritize recommendations from all agents"""
        
        all_recommendations = []
        seen_recommendations = set()
        
        for agent_name, result in results.items():
            recommendations = result.get("recommendations", [])
            
            for rec in recommendations:
                # Create unique key
                rec_key = (rec.get("category", ""), rec.get("action", ""))
                
                if rec_key not in seen_recommendations:
                    seen_recommendations.add(rec_key)
                    
                    # Add source
                    rec_with_source = {
                        **rec,
                        "suggested_by": agent_name
                    }
                    all_recommendations.append(rec_with_source)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_recommendations.sort(
            key=lambda r: priority_order.get(r.get("priority", "low"), 99)
        )
        
        return all_recommendations
    
    def _calculate_category_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for each category"""
        
        categories = {}
        
        # Map agent types to categories
        category_mapping = {
            "compliance": "compliance",
            "quality": "quality",
            "identity": "identity_verification",
            "risk": "risk_assessment",
            "content": "content_quality"
        }
        
        for agent_name, result in results.items():
            agent_type = self._get_agent_type(agent_name)
            category = category_mapping.get(agent_type, "other")
            
            score = result.get("score", 0)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(score)
        
        # Average scores per category
        category_scores = {}
        for category, scores in categories.items():
            if scores:
                category_scores[category] = round(sum(scores) / len(scores), 2)
        
        return category_scores
    
    def _build_audit_trail(
        self, 
        agent_results: Dict[str, Any],
        aggregation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build audit trail for the aggregation process"""
        
        successful_agents = [
            name for name, result in agent_results.items()
            if "error" not in result
        ]
        
        failed_agents = [
            {
                "name": name,
                "error": result.get("error", "Unknown error")
            }
            for name, result in agent_results.items()
            if "error" in result
        ]
        
        return {
            "aggregation_method": aggregation_rules.get("method", "weighted_average"),
            "agents_executed": len(agent_results),
            "agents_successful": len(successful_agents),
            "agents_failed": len(failed_agents),
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "aggregation_timestamp": datetime.now().isoformat(),
            "rules_version": aggregation_rules.get("version", 1)
        }
    
    def _get_agent_type(self, agent_name: str) -> str:
        """Extract agent type from agent name"""
        
        # Simple heuristic - in production would use agent metadata
        if "compliance" in agent_name.lower():
            return "compliance"
        elif "quality" in agent_name.lower():
            return "quality"
        elif "identity" in agent_name.lower():
            return "identity"
        elif "risk" in agent_name.lower():
            return "risk"
        else:
            return "specialist"
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance
    
    def apply_thresholds(
        self, 
        result: AnalysisResult,
        thresholds: Dict[str, Any]
    ) -> str:
        """
        Apply thresholds to determine pass/fail/review status
        
        Args:
            result: The aggregated analysis result
            thresholds: Threshold configuration
            
        Returns:
            Status string: "pass", "fail", or "review"
        """
        
        score = result.overall_score
        
        # Get threshold values
        pass_threshold = thresholds.get("pass", 85)
        fail_threshold = thresholds.get("fail", 60)
        
        # Check critical violations
        critical_violations = [
            v for v in result.violations 
            if v.get("severity") == "critical"
        ]
        
        if critical_violations:
            return "fail"
        
        # Apply score thresholds
        if score >= pass_threshold:
            return "pass"
        elif score < fail_threshold:
            return "fail"
        else:
            return "review"