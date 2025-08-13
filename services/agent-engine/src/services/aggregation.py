"""Result Aggregation Service for combining agent outputs"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import statistics
import json
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Standardized analysis result format matching MASTERPLAN lines 2911-2920"""
    analysis_id: str
    overall_score: float  # 0-100 score
    confidence: float  # 0-1 confidence level
    violations: List[Dict[str, Any]]  # Detected compliance violations
    recommendations: List[Dict[str, Any]]  # Suggested actions
    categories: Dict[str, Any]  # Per-agent results with scores and findings
    audit_trail: Dict[str, Any]  # Execution metadata and tracing
    execution_time: float  # Total execution time in seconds
    status: Optional[str] = None  # PASS/FAIL/REVIEW status
    
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
            "execution_time": self.execution_time,
            "status": self.status
        }


class ResultAggregator:
    """Service for aggregating multiple agent results into final analysis
    
    Processes TahoeAgent dict outputs and applies scorecard-specific
    aggregation rules and business thresholds.
    """
    
    def __init__(self):
        # Default weights if not specified in scorecard
        self.default_weights = {
            "compliance_specialist": 0.4,
            "quality_specialist": 0.3,
            "identity_specialist": 0.2,
            "risk_specialist": 0.1
        }
        
        # Severity levels for violations
        self.severity_levels = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "info": 0
        }
        
        # Priority levels for recommendations  
        self.priority_levels = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "optional": 0
        }
    
    async def aggregate(
        self, 
        agent_results: Dict[str, Any], 
        aggregation_rules: Dict[str, Any],
        thresholds: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Aggregate individual agent results into final analysis
        
        Processes TahoeAgent dict format with weighted scoring based on
        scorecard configuration.
        
        Args:
            agent_results: Dictionary of TahoeAgent outputs keyed by agent name
                          Each contains: agent_name, score, confidence, violations, etc.
            aggregation_rules: Scorecard aggregation rules including weights
            thresholds: Pass/fail/review thresholds from scorecard
            
        Returns:
            Aggregated AnalysisResult with overall scores and categorized findings
        """
        logger.info(f"Aggregating results from {len(agent_results)} agents")
        
        # Extract valid results (exclude errors)
        valid_results = {
            name: result 
            for name, result in agent_results.items() 
            if isinstance(result, dict) and "error" not in result
        }
        
        # Calculate overall score using scorecard weights
        overall_score, weight_details = self._calculate_weighted_score(
            valid_results, aggregation_rules
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(valid_results)
        
        # Aggregate violations
        all_violations = self._aggregate_violations(valid_results)
        
        # Aggregate recommendations
        all_recommendations = self._aggregate_recommendations(valid_results)
        
        # Build per-agent category results
        categories = self._build_category_results(valid_results)
        
        # Calculate total execution time
        execution_time = sum(
            result.get("execution_time", 0) 
            for result in valid_results.values()
        )
        
        # Apply business rules for critical violations
        overall_score = self._apply_business_rules(
            overall_score, all_violations, thresholds
        )
        
        # Determine pass/fail/review status
        status = self._determine_status(overall_score, all_violations, thresholds)
        
        # Build comprehensive audit trail
        audit_trail = self._build_audit_trail(
            agent_results, aggregation_rules, weight_details, status
        )
        
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            overall_score=overall_score,
            confidence=confidence,
            violations=all_violations,
            recommendations=all_recommendations,
            categories=categories,
            audit_trail=audit_trail,
            execution_time=execution_time,
            status=status
        )
    
    def _calculate_weighted_score(
        self, 
        results: Dict[str, Any], 
        rules: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate weighted overall score using scorecard agent weights
        
        Returns:
            Tuple of (overall_score, weight_details for audit)
        """
        
        if not results:
            return 0.0, {}
        
        # Extract weights from aggregation rules
        weights = rules.get("weights", {})
        
        # Track details for audit
        weight_details = {
            "method": rules.get("method", "weighted_average"),
            "agent_scores": {},
            "agent_weights": {},
            "weighted_contributions": {}
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for agent_name, result in results.items():
            # Extract score from TahoeAgent dict format
            score = self._extract_score(result)
            
            # Get weight for this agent from rules or defaults
            weight = weights.get(agent_name, self.default_weights.get(agent_name, 1.0))
            
            # Calculate weighted contribution
            contribution = score * weight
            weighted_sum += contribution
            total_weight += weight
            
            # Track for audit
            weight_details["agent_scores"][agent_name] = score
            weight_details["agent_weights"][agent_name] = weight
            weight_details["weighted_contributions"][agent_name] = round(contribution, 2)
        
        # Calculate final score
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            # Simple average if no weights
            scores = [self._extract_score(r) for r in results.values()]
            overall_score = sum(scores) / len(scores) if scores else 0
        
        weight_details["total_weight"] = round(total_weight, 2)
        weight_details["weighted_sum"] = round(weighted_sum, 2)
        weight_details["overall_score"] = round(overall_score, 2)
        
        return round(overall_score, 2), weight_details
    
    def _extract_score(self, agent_result: Dict[str, Any]) -> float:
        """Extract score from TahoeAgent result dict
        
        Handles various formats:
        - Direct 'score' field
        - Parsed from 'result' text
        - Default to 50 if not found
        """
        
        # Check for direct score field
        if "score" in agent_result:
            return float(agent_result["score"])
        
        # Try to extract from result text
        result_text = agent_result.get("result", "")
        if isinstance(result_text, str):
            # Look for patterns like "Score: 85" or "85%" or "8.5/10"
            import re
            
            # Pattern: Score: XX or Score XX
            score_match = re.search(r'[Ss]core[:\s]+(\d+(?:\.\d+)?)', result_text)
            if score_match:
                score = float(score_match.group(1))
                # Normalize if out of 10
                return score * 10 if score <= 10 else score
            
            # Pattern: XX%
            percent_match = re.search(r'(\d+(?:\.\d+)?)%', result_text)
            if percent_match:
                return float(percent_match.group(1))
            
            # Pattern: X.X/10
            ratio_match = re.search(r'(\d+(?:\.\d+)?)/10', result_text)
            if ratio_match:
                return float(ratio_match.group(1)) * 10
        
        # Default score if unable to extract
        return 50.0
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate aggregate confidence score from TahoeAgent results
        
        Uses mean confidence with adjustment for consistency between agents.
        """
        
        if not results:
            return 0.0
        
        # Extract confidences from TahoeAgent dict format
        confidences = []
        for result in results.values():
            # TahoeAgent always includes confidence field
            conf = result.get("confidence", 0.5)
            confidences.append(conf)
        
        if not confidences:
            return 0.5
        
        # Calculate mean confidence
        mean_confidence = statistics.mean(confidences)
        
        # Adjust for consistency between agents
        if len(confidences) > 1:
            # Use standard deviation to measure consistency
            stdev = statistics.stdev(confidences)
            # Higher consistency (lower stdev) increases confidence
            consistency_factor = max(0.8, 1.0 - stdev)
            adjusted_confidence = mean_confidence * consistency_factor
        else:
            adjusted_confidence = mean_confidence
        
        return round(adjusted_confidence, 3)
    
    def _aggregate_violations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine and deduplicate violations from TahoeAgent results
        
        Deduplicates by type and severity, maintains evidence from all agents.
        """
        
        violation_groups = {}  # Group violations by key
        
        for agent_name, result in results.items():
            # Extract violations from TahoeAgent dict
            violations = result.get("violations", [])
            
            # Also check findings for violations
            findings = result.get("findings", [])
            for finding in findings:
                if finding.get("type") == "violation":
                    violations.append(finding)
            
            for violation in violations:
                # Create deduplication key
                violation_key = (
                    violation.get("type", "unknown"),
                    violation.get("regulation", ""),
                    violation.get("section", ""),
                    violation.get("severity", "medium")
                )
                
                if violation_key not in violation_groups:
                    violation_groups[violation_key] = {
                        "type": violation.get("type", "compliance"),
                        "regulation": violation.get("regulation", "Unknown"),
                        "section": violation.get("section", ""),
                        "description": violation.get("description", ""),
                        "severity": violation.get("severity", "medium"),
                        "detected_by": [],
                        "evidence": [],
                        "confidence": []
                    }
                
                # Aggregate detection sources
                violation_groups[violation_key]["detected_by"].append(agent_name)
                violation_groups[violation_key]["confidence"].append(
                    result.get("confidence", 0.5)
                )
                
                # Aggregate evidence
                if "evidence" in violation:
                    violation_groups[violation_key]["evidence"].append({
                        "source": agent_name,
                        "details": violation["evidence"]
                    })
                
                # Update description if more detailed
                if len(violation.get("description", "")) > len(
                    violation_groups[violation_key]["description"]
                ):
                    violation_groups[violation_key]["description"] = violation["description"]
        
        # Convert to list and calculate aggregate confidence
        all_violations = []
        for violation_data in violation_groups.values():
            # Calculate mean confidence for this violation
            violation_data["aggregate_confidence"] = round(
                statistics.mean(violation_data["confidence"]), 3
            )
            # Remove individual confidences from final output
            del violation_data["confidence"]
            
            all_violations.append(violation_data)
        
        # Sort by severity (critical first) - use reverse=True for descending order
        all_violations.sort(
            key=lambda v: self.severity_levels.get(v.get("severity", "low"), 0),
            reverse=True
        )
        
        return all_violations
    
    def _aggregate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine and prioritize recommendations from TahoeAgent results
        
        Deduplicates similar recommendations and prioritizes by impact.
        """
        
        recommendation_groups = {}  # Group similar recommendations
        
        for agent_name, result in results.items():
            # Extract recommendations from TahoeAgent dict
            recommendations = result.get("recommendations", [])
            
            # Also check findings for recommendations
            findings = result.get("findings", [])
            for finding in findings:
                if finding.get("type") == "recommendation":
                    recommendations.append(finding)
            
            for rec in recommendations:
                # Create deduplication key
                rec_key = (
                    rec.get("category", "general"),
                    rec.get("action", rec.get("title", ""))
                )
                
                if rec_key not in recommendation_groups:
                    recommendation_groups[rec_key] = {
                        "category": rec.get("category", "general"),
                        "action": rec.get("action", rec.get("title", "")),
                        "description": rec.get("description", ""),
                        "priority": rec.get("priority", "medium"),
                        "impact": rec.get("impact", "moderate"),
                        "suggested_by": [],
                        "rationale": []
                    }
                
                # Aggregate suggestion sources
                recommendation_groups[rec_key]["suggested_by"].append(agent_name)
                
                # Aggregate rationales
                if "rationale" in rec:
                    recommendation_groups[rec_key]["rationale"].append({
                        "source": agent_name,
                        "reason": rec["rationale"]
                    })
                
                # Use highest priority if multiple agents suggest same action
                current_priority = self.priority_levels.get(
                    recommendation_groups[rec_key]["priority"], 2
                )
                new_priority = self.priority_levels.get(rec.get("priority", "medium"), 2)
                if new_priority > current_priority:
                    recommendation_groups[rec_key]["priority"] = rec["priority"]
        
        # Convert to list
        all_recommendations = list(recommendation_groups.values())
        
        # Sort by priority (critical first)
        all_recommendations.sort(
            key=lambda r: self.priority_levels.get(r.get("priority", "medium"), 99),
            reverse=True
        )
        
        return all_recommendations
    
    def _build_category_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build per-agent category results from TahoeAgent outputs
        
        Returns detailed results for each agent including scores, findings, and metadata.
        """
        
        categories = {}
        
        for agent_name, result in results.items():
            # Build category entry for this agent
            categories[agent_name] = {
                "score": self._extract_score(result),
                "confidence": result.get("confidence", 0.5),
                "agent_version": result.get("agent_version", "1.0"),
                "model_used": result.get("model_used", "unknown"),
                "execution_time": result.get("execution_time", 0),
                "findings_count": len(result.get("findings", [])),
                "violations_count": len(result.get("violations", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "key_findings": self._extract_key_findings(result)
            }
        
        return categories
    
    def _extract_key_findings(self, agent_result: Dict[str, Any]) -> List[str]:
        """Extract top key findings from agent result
        
        Returns list of key finding summaries.
        """
        
        findings = agent_result.get("findings", [])
        key_findings = []
        
        # Take top 3 findings
        for finding in findings[:3]:
            if isinstance(finding, dict):
                summary = finding.get("summary", finding.get("description", ""))
                if summary:
                    key_findings.append(summary)
            elif isinstance(finding, str):
                key_findings.append(finding)
        
        return key_findings
    
    def _build_audit_trail(
        self, 
        agent_results: Dict[str, Any],
        aggregation_rules: Dict[str, Any],
        weight_details: Dict[str, Any],
        status: str
    ) -> Dict[str, Any]:
        """Build comprehensive audit trail for the aggregation process
        
        Includes execution details, weight calculations, and rule applications.
        """
        
        successful_agents = [
            name for name, result in agent_results.items()
            if "error" not in result
        ]
        
        failed_agents = [
            {
                "name": name,
                "error": result.get("error", "Unknown error"),
                "trace_id": result.get("trace_id")
            }
            for name, result in agent_results.items()
            if "error" in result
        ]
        
        return {
            "aggregation_method": aggregation_rules.get("method", "weighted_average"),
            "aggregation_timestamp": datetime.now().isoformat(),
            "agents_executed": len(agent_results),
            "agents_successful": len(successful_agents),
            "agents_failed": len(failed_agents),
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "weight_calculation": weight_details,
            "rules_applied": {
                "version": aggregation_rules.get("version", 1),
                "thresholds_used": aggregation_rules.get("thresholds", {}),
                "business_rules": aggregation_rules.get("business_rules", [])
            },
            "final_status": status,
            "trace_ids": [
                result.get("trace_id") 
                for result in agent_results.values() 
                if "trace_id" in result
            ]
        }
    
    def _apply_business_rules(
        self,
        score: float,
        violations: List[Dict[str, Any]],
        thresholds: Dict[str, Any]
    ) -> float:
        """Apply business rules to adjust score based on violations
        
        Critical violations cap the maximum possible score.
        """
        
        # Check for critical violations
        critical_violations = [
            v for v in violations 
            if v.get("severity") == "critical"
        ]
        
        if critical_violations:
            # Cap score for critical violations
            max_score_with_critical = thresholds.get("max_score_with_critical", 50)
            if score > max_score_with_critical:
                logger.info(
                    f"Capping score from {score} to {max_score_with_critical} "
                    f"due to {len(critical_violations)} critical violations"
                )
                score = max_score_with_critical
        
        # Check for high severity violations
        high_violations = [
            v for v in violations
            if v.get("severity") == "high"
        ]
        
        if len(high_violations) >= thresholds.get("high_violation_threshold", 3):
            # Apply penalty for multiple high violations
            penalty = thresholds.get("high_violation_penalty", 10)
            score = max(0, score - penalty)
            logger.info(
                f"Applied {penalty} point penalty for {len(high_violations)} high violations"
            )
        
        return round(score, 2)
    
    def _determine_status(
        self,
        score: float,
        violations: List[Dict[str, Any]],
        thresholds: Dict[str, Any]
    ) -> str:
        """Determine pass/fail/review status based on score and violations
        
        Uses scorecard thresholds to categorize the result.
        """
        
        # Check for automatic fail conditions
        critical_violations = [
            v for v in violations
            if v.get("severity") == "critical"
        ]
        
        if critical_violations and thresholds.get("critical_auto_fail", True):
            return "FAIL"
        
        # Apply score thresholds
        pass_threshold = thresholds.get("pass", 80)
        review_threshold = thresholds.get("review", 60)
        
        if score >= pass_threshold:
            return "PASS"
        elif score >= review_threshold:
            return "REVIEW"
        else:
            return "FAIL"
    
    
