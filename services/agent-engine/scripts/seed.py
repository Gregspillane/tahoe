#!/usr/bin/env python3
"""
Seed script for agent-engine database
Creates sample data for development and testing
"""

import asyncio
import json
import uuid
from datetime import datetime
from prisma import Prisma
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def seed_database():
    """Seed the database with initial data"""
    
    db = Prisma()
    await db.connect()
    
    try:
        print("🌱 Starting database seed...")
        
        # Check if data already exists
        existing_portfolio = await db.portfolio.find_first(
            where={"name": "Test Portfolio"}
        )
        if existing_portfolio:
            print("⚠️  Data already exists. Clearing existing data...")
            # Clear in correct order due to foreign keys
            await db.analysis.delete_many()
            await db.scorecardagent.delete_many()
            await db.scorecard.delete_many()
            await db.portfolio.delete_many()
            await db.agenttemplate.delete_many()
            await db.modelprovider.delete_many()
            await db.tool.delete_many()
            print("✅ Cleared existing data")
        
        # Create a test portfolio
        print("Creating portfolio...")
        portfolio = await db.portfolio.create(
            data={
                "organizationId": "test-org-001",
                "name": "Test Portfolio",
                "description": "Development test portfolio",
                "configuration": json.dumps({
                    "max_analyses_per_day": 1000,
                    "enable_real_time": True,
                    "default_language": "en",
                    "features": {
                        "compliance_checking": True,
                        "quality_assessment": True,
                        "risk_evaluation": True
                    }
                }),
                "isActive": True
            }
        )
        print(f"✅ Created portfolio: {portfolio.name}")
        
        # Create agent templates
        print("\nCreating agent templates...")
        
        # Compliance Analyst Agent
        compliance_agent = await db.agenttemplate.create(
            data={
                "name": "compliance_analyst",
                "description": "Analyzes interactions for regulatory compliance",
                "type": "specialist",
                "model": "gemini-2.0-flash",
                "modelConfig": json.dumps({
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "top_p": 0.95
                }),
                "capabilities": ["compliance", "fdcpa", "tcpa", "regulatory"],
                "tools": ["regulatory_database", "violation_detector"],
                "triggerRules": json.dumps({
                    "content_type": ["call", "email", "chat"],
                    "required_topics": ["debt", "collection", "payment"],
                    "regulatory_indicators": ["fdcpa", "tcpa", "reg_f"]
                }),
                "systemPrompt": "You are a compliance specialist analyzing interactions for regulatory violations.",
                "userPrompt": "Analyze the following interaction for compliance issues:\n{interaction}",
                "isActive": True
            }
        )
        print(f"✅ Created agent: {compliance_agent.name}")
        
        # Quality Assessment Agent
        quality_agent = await db.agenttemplate.create(
            data={
                "name": "quality_assessor",
                "description": "Evaluates interaction quality and professionalism",
                "type": "specialist",
                "model": "gemini-2.0-flash",
                "modelConfig": json.dumps({
                    "temperature": 0.5,
                    "max_tokens": 1500,
                    "top_p": 0.95
                }),
                "capabilities": ["quality", "professionalism", "communication"],
                "tools": ["sentiment_analyzer", "tone_detector"],
                "triggerRules": json.dumps({
                    "content_type": ["call", "email", "chat"],
                    "always_active": True
                }),
                "systemPrompt": "You are a quality assessment specialist evaluating professional communication.",
                "userPrompt": "Evaluate the quality of this interaction:\n{interaction}",
                "isActive": True
            }
        )
        print(f"✅ Created agent: {quality_agent.name}")
        
        # Content Analyzer Agent
        content_agent = await db.agenttemplate.create(
            data={
                "name": "content_analyzer",
                "description": "Extracts topics and metadata from interactions",
                "type": "specialist",
                "model": "gemini-2.0-flash",
                "modelConfig": json.dumps({
                    "temperature": 0.2,
                    "max_tokens": 1000,
                    "top_p": 0.9
                }),
                "capabilities": ["topic_extraction", "entity_detection", "summarization"],
                "tools": ["nlp_toolkit", "entity_extractor"],
                "triggerRules": json.dumps({
                    "content_type": ["call", "email", "chat"],
                    "always_active": True
                }),
                "systemPrompt": "You are a content analysis specialist extracting key information.",
                "userPrompt": "Extract key topics and entities from:\n{interaction}",
                "isActive": True
            }
        )
        print(f"✅ Created agent: {content_agent.name}")
        
        # Create scorecards
        print("\nCreating scorecards...")
        
        # Standard Compliance Scorecard
        compliance_scorecard = await db.scorecard.create(
            data={
                "name": "Standard Compliance Check",
                "description": "Comprehensive compliance evaluation",
                "portfolioId": portfolio.id,
                "requirements": json.dumps({
                    "categories": {
                        "fdcpa_compliance": {
                            "weight": 0.4,
                            "required": True,
                            "threshold": 85
                        },
                        "communication_quality": {
                            "weight": 0.3,
                            "required": True,
                            "threshold": 70
                        },
                        "information_accuracy": {
                            "weight": 0.3,
                            "required": True,
                            "threshold": 90
                        }
                    }
                }),
                "thresholds": json.dumps({
                    "pass": 85,
                    "review": 70,
                    "fail": 60
                }),
                "aggregationRules": json.dumps({
                    "method": "weighted_average",
                    "min_agents_required": 2
                }),
                "isActive": True
            }
        )
        print(f"✅ Created scorecard: {compliance_scorecard.name}")
        
        # Quality Assurance Scorecard
        qa_scorecard = await db.scorecard.create(
            data={
                "name": "Quality Assurance Review",
                "description": "Interaction quality and professionalism check",
                "portfolioId": portfolio.id,
                "requirements": json.dumps({
                    "dimensions": {
                        "professionalism": {
                            "weight": 0.35,
                            "threshold": 80
                        },
                        "clarity": {
                            "weight": 0.35,
                            "threshold": 75
                        },
                        "empathy": {
                            "weight": 0.3,
                            "threshold": 70
                        }
                    }
                }),
                "thresholds": json.dumps({
                    "excellent": 90,
                    "good": 75,
                    "needs_improvement": 60
                }),
                "aggregationRules": json.dumps({
                    "method": "weighted_average",
                    "boost_for_excellence": 1.1
                }),
                "isActive": True
            }
        )
        print(f"✅ Created scorecard: {qa_scorecard.name}")
        
        # Map agents to scorecards
        print("\nMapping agents to scorecards...")
        
        # Compliance scorecard agents
        await db.scorecardagent.create(
            data={
                "scorecardId": compliance_scorecard.id,
                "agentId": compliance_agent.id,
                "weight": 2.0,
                "isRequired": True,
                "executionOrder": 1
            }
        )
        
        await db.scorecardagent.create(
            data={
                "scorecardId": compliance_scorecard.id,
                "agentId": content_agent.id,
                "weight": 1.0,
                "isRequired": True,
                "executionOrder": 0
            }
        )
        
        # QA scorecard agents
        await db.scorecardagent.create(
            data={
                "scorecardId": qa_scorecard.id,
                "agentId": quality_agent.id,
                "weight": 2.0,
                "isRequired": True,
                "executionOrder": 1
            }
        )
        
        await db.scorecardagent.create(
            data={
                "scorecardId": qa_scorecard.id,
                "agentId": content_agent.id,
                "weight": 1.0,
                "isRequired": False,
                "executionOrder": 0
            }
        )
        
        print("✅ Mapped agents to scorecards")
        
        # Create model providers
        print("\nCreating model provider configurations...")
        
        gemini_provider = await db.modelprovider.create(
            data={
                "name": "gemini",
                "baseUrl": "https://generativelanguage.googleapis.com",
                "apiKeyEnvVar": "GOOGLE_API_KEY",
                "models": json.dumps({
                    "gemini-2.0-flash": {
                        "max_tokens": 4000,
                        "supports_tools": True,
                        "supports_vision": True
                    },
                    "gemini-1.5-pro": {
                        "max_tokens": 8000,
                        "supports_tools": True,
                        "supports_vision": True
                    }
                }),
                "isActive": True
            }
        )
        print(f"✅ Created provider: {gemini_provider.name}")
        
        openai_provider = await db.modelprovider.create(
            data={
                "name": "openai",
                "baseUrl": "https://api.openai.com/v1",
                "apiKeyEnvVar": "OPENAI_API_KEY",
                "models": json.dumps({
                    "gpt-4-turbo": {
                        "max_tokens": 4000,
                        "supports_tools": True,
                        "supports_vision": True
                    },
                    "gpt-4o": {
                        "max_tokens": 4000,
                        "supports_tools": True,
                        "supports_vision": True
                    }
                }),
                "isActive": False  # Disabled by default
            }
        )
        print(f"✅ Created provider: {openai_provider.name}")
        
        # Create tools
        print("\nCreating tool configurations...")
        
        await db.tool.create(
            data={
                "name": "regulatory_database",
                "description": "Access to regulatory compliance database",
                "type": "database",
                "configuration": json.dumps({
                    "connection": "internal",
                    "tables": ["fdcpa_rules", "tcpa_rules", "reg_f_rules"]
                }),
                "isActive": True
            }
        )
        
        await db.tool.create(
            data={
                "name": "sentiment_analyzer",
                "description": "Analyzes emotional tone and sentiment",
                "type": "function",
                "configuration": json.dumps({
                    "model": "sentiment-bert",
                    "threshold": 0.7
                }),
                "isActive": True
            }
        )
        
        print("✅ Created tool configurations")
        
        # Create a sample analysis (completed)
        print("\nCreating sample analysis...")
        
        analysis = await db.analysis.create(
            data={
                "interactionId": "sample-interaction-001",
                "portfolioId": portfolio.id,
                "scorecardId": compliance_scorecard.id,
                "status": "complete",
                "overallScore": 87.5,
                "confidence": 0.92,
                "results": json.dumps({
                    "categories": {
                        "fdcpa_compliance": {"score": 90, "violations": []},
                        "communication_quality": {"score": 85, "issues": ["minor tone issue"]},
                        "information_accuracy": {"score": 88, "verified": True}
                    }
                }),
                "agentOutputs": json.dumps({
                    "compliance_analyst": {
                        "score": 90,
                        "findings": ["No FDCPA violations detected"],
                        "execution_time": 2.3
                    },
                    "content_analyzer": {
                        "topics": ["payment", "account status"],
                        "entities": ["customer_name", "account_number"],
                        "execution_time": 1.1
                    }
                }),
                "violations": [],
                "recommendations": [],
                "metadata": json.dumps({
                    "interaction_type": "call",
                    "duration": 180,
                    "language": "en"
                }),
                "executionTime": 3.4,
                "traceId": str(uuid.uuid4()),
                "completedAt": datetime.now()
            }
        )
        print(f"✅ Created sample analysis: {analysis.id}")
        
        print("\n🎉 Database seeding complete!")
        print(f"\nCreated:")
        print(f"  - 1 Portfolio")
        print(f"  - 3 Agent Templates")
        print(f"  - 2 Scorecards")
        print(f"  - 4 Agent-Scorecard Mappings")
        print(f"  - 2 Model Providers")
        print(f"  - 2 Tools")
        print(f"  - 1 Sample Analysis")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_database())