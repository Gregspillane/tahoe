#!/usr/bin/env python3
"""
Basic CRUD tests for database operations
"""

import asyncio
import json
from prisma import Prisma
from datetime import datetime
import uuid


async def test_crud_operations():
    """Test basic CRUD operations on all tables"""
    
    db = Prisma()
    await db.connect()
    
    print("🧪 Running database CRUD tests...\n")
    
    try:
        # Test 1: Read Portfolio
        print("Test 1: Reading portfolios...")
        portfolios = await db.portfolio.find_many()
        assert len(portfolios) > 0, "Should have at least one portfolio"
        portfolio = portfolios[0]
        print(f"✅ Found {len(portfolios)} portfolio(s)")
        print(f"   Portfolio: {portfolio.name} (ID: {portfolio.id})")
        
        # Test 2: Read Agent Templates
        print("\nTest 2: Reading agent templates...")
        agents = await db.agenttemplate.find_many(
            where={"isActive": True}
        )
        assert len(agents) >= 3, "Should have at least 3 agent templates"
        print(f"✅ Found {len(agents)} active agent(s)")
        for agent in agents:
            print(f"   - {agent.name}: {agent.description}")
        
        # Test 3: Read Scorecards with Agents
        print("\nTest 3: Reading scorecards with mapped agents...")
        scorecards = await db.scorecard.find_many(
            include={
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            }
        )
        assert len(scorecards) >= 2, "Should have at least 2 scorecards"
        print(f"✅ Found {len(scorecards)} scorecard(s)")
        for scorecard in scorecards:
            agent_count = len(scorecard.scorecardAgents)
            print(f"   - {scorecard.name}: {agent_count} agent(s) mapped")
        
        # Test 4: Create a new Analysis
        print("\nTest 4: Creating new analysis...")
        new_analysis = await db.analysis.create(
            data={
                "interactionId": f"test-interaction-{uuid.uuid4().hex[:8]}",
                "portfolioId": portfolio.id,
                "scorecardId": scorecards[0].id,
                "status": "pending",
                "metadata": json.dumps({"test": True, "timestamp": datetime.now().isoformat()})
            }
        )
        print(f"✅ Created analysis: {new_analysis.id}")
        print(f"   Interaction ID: {new_analysis.interactionId}")
        print(f"   Status: {new_analysis.status}")
        
        # Test 5: Update the Analysis
        print("\nTest 5: Updating analysis...")
        updated_analysis = await db.analysis.update(
            where={"id": new_analysis.id},
            data={
                "status": "processing",
                "overallScore": 85.5,
                "confidence": 0.9
            }
        )
        assert updated_analysis.status == "processing", "Status should be updated"
        assert updated_analysis.overallScore == 85.5, "Score should be updated"
        print(f"✅ Updated analysis status to: {updated_analysis.status}")
        print(f"   Score: {updated_analysis.overallScore}, Confidence: {updated_analysis.confidence}")
        
        # Test 6: Query with filters
        print("\nTest 6: Querying with filters...")
        pending_analyses = await db.analysis.find_many(
            where={"status": {"in": ["pending", "processing"]}},
            order={"createdAt": "desc"},
            take=5
        )
        print(f"✅ Found {len(pending_analyses)} pending/processing analyses")
        
        # Test 7: Read Model Providers
        print("\nTest 7: Reading model providers...")
        providers = await db.modelprovider.find_many()
        assert len(providers) >= 2, "Should have at least 2 model providers"
        print(f"✅ Found {len(providers)} model provider(s)")
        for provider in providers:
            status = "active" if provider.isActive else "inactive"
            print(f"   - {provider.name}: {status}")
        
        # Test 8: Read Tools
        print("\nTest 8: Reading tools...")
        tools = await db.tool.find_many(
            where={"isActive": True}
        )
        print(f"✅ Found {len(tools)} active tool(s)")
        for tool in tools:
            print(f"   - {tool.name} ({tool.type})")
        
        # Test 9: Complex query with relationships
        print("\nTest 9: Complex query with relationships...")
        full_analysis = await db.analysis.find_first(
            where={"status": "complete"},
            include={
                "portfolio": True,
                "scorecard": {
                    "include": {
                        "scorecardAgents": {
                            "include": {"agent": True}
                        }
                    }
                }
            }
        )
        if full_analysis:
            print(f"✅ Found complete analysis with full relationships")
            print(f"   Portfolio: {full_analysis.portfolio.name}")
            print(f"   Scorecard: {full_analysis.scorecard.name}")
            print(f"   Agents used: {len(full_analysis.scorecard.scorecardAgents)}")
        else:
            print("ℹ️  No complete analysis found (this is OK for initial tests)")
        
        # Test 10: Delete the test analysis
        print("\nTest 10: Deleting test analysis...")
        deleted = await db.analysis.delete(
            where={"id": new_analysis.id}
        )
        print(f"✅ Deleted analysis: {deleted.id}")
        
        # Verify deletion
        deleted_check = await db.analysis.find_unique(
            where={"id": new_analysis.id}
        )
        assert deleted_check is None, "Analysis should be deleted"
        print("   Verified: Analysis successfully deleted")
        
        print("\n✨ All database CRUD tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        await db.disconnect()


async def test_database_connection():
    """Test basic database connectivity"""
    
    db = Prisma()
    
    print("🔌 Testing database connection...")
    
    try:
        await db.connect()
        print("✅ Successfully connected to database")
        
        # Simple health check query
        count = await db.agenttemplate.count()
        print(f"✅ Database is responsive (found {count} agent templates)")
        
        await db.disconnect()
        print("✅ Successfully disconnected from database")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("=" * 60)
    print("DATABASE TEST SUITE")
    print("=" * 60)
    
    # Test connection first
    if not await test_database_connection():
        print("\n⚠️  Cannot proceed without database connection")
        return
    
    print("\n" + "-" * 60 + "\n")
    
    # Run CRUD tests
    await test_crud_operations()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())