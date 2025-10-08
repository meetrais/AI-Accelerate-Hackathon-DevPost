"""
Flight MCP Server - Mock implementation for demo
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
from .base_server import BaseMCPServer
from shared.protocols import MCPTool


class FlightMCPServer(BaseMCPServer):
    """MCP Server for flight data"""
    
    def __init__(self):
        super().__init__(name="flight-data-server", version="1.0.0")
    
    def _register_tools(self):
        """Register flight-related tools"""
        
        # Search flights tool
        self.register_tool(MCPTool(
            name="search_flights",
            description="Search for available flights",
            input_schema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport code"},
                    "destination": {"type": "string", "description": "Destination airport code"},
                    "date": {"type": "string", "description": "Departure date (YYYY-MM-DD)"},
                    "passengers": {"type": "integer", "description": "Number of passengers"}
                },
                "required": ["origin", "destination", "date", "passengers"]
            }
        ))
        
        # Get flight details tool
        self.register_tool(MCPTool(
            name="get_flight_details",
            description="Get detailed information about a specific flight",
            input_schema={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight ID"}
                },
                "required": ["flight_id"]
            }
        ))
        
        # Book flight tool
        self.register_tool(MCPTool(
            name="book_flight",
            description="Book a flight",
            input_schema={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string"},
                    "passenger_details": {"type": "object"}
                },
                "required": ["flight_id", "passenger_details"]
            }
        ))
    
    async def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute flight tools"""
        
        if tool_name == "search_flights":
            return await self._search_flights(arguments)
        elif tool_name == "get_flight_details":
            return await self._get_flight_details(arguments)
        elif tool_name == "book_flight":
            return await self._book_flight(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _search_flights(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock flight search"""
        origin = args["origin"]
        destination = args["destination"]
        date = args["date"]
        passengers = args["passengers"]
        
        # Generate mock flight results
        airlines = ["United Airlines", "Delta", "American Airlines", "JetBlue", "Southwest"]
        flights = []
        
        for i in range(5):
            departure_time = datetime.fromisoformat(date) + timedelta(hours=6 + i*3)
            arrival_time = departure_time + timedelta(hours=random.randint(2, 8))
            
            price_per_person = random.randint(200, 800)
            
            flight = {
                "flight_id": f"FL{random.randint(1000, 9999)}",
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(['UA', 'DL', 'AA', 'B6', 'WN'])}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "duration_minutes": int((arrival_time - departure_time).total_seconds() / 60),
                "stops": random.choice([0, 0, 0, 1]),  # Mostly direct flights
                "price": {
                    "amount": price_per_person * passengers,
                    "currency": "USD",
                    "per_person": price_per_person
                },
                "seats_available": random.randint(5, 50),
                "cabin_class": "Economy",
                "baggage": {
                    "carry_on": 1,
                    "checked": random.choice([0, 1, 2])
                }
            }
            flights.append(flight)
        
        # Sort by price
        flights.sort(key=lambda x: x["price"]["amount"])
        
        return flights
    
    async def _get_flight_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get flight details"""
        flight_id = args["flight_id"]
        
        # Mock detailed flight info
        return {
            "flight_id": flight_id,
            "airline": "United Airlines",
            "flight_number": "UA123",
            "aircraft": "Boeing 737-800",
            "origin": {
                "code": "SFO",
                "name": "San Francisco International Airport",
                "terminal": "3"
            },
            "destination": {
                "code": "NRT",
                "name": "Narita International Airport",
                "terminal": "1"
            },
            "departure_time": "2025-12-01T10:00:00",
            "arrival_time": "2025-12-02T14:00:00",
            "duration_minutes": 660,
            "stops": 0,
            "price": {
                "amount": 1200,
                "currency": "USD"
            },
            "amenities": ["WiFi", "In-flight entertainment", "Meals included"],
            "cancellation_policy": "Free cancellation up to 24 hours before departure"
        }
    
    async def _book_flight(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mock flight booking"""
        flight_id = args["flight_id"]
        passenger_details = args["passenger_details"]
        
        # Generate booking confirmation
        booking_ref = f"BOOK{random.randint(100000, 999999)}"
        
        return {
            "success": True,
            "booking_reference": booking_ref,
            "flight_id": flight_id,
            "status": "confirmed",
            "passengers": passenger_details,
            "confirmation_email_sent": True,
            "eticket_url": f"https://example.com/eticket/{booking_ref}"
        }


# Global instance
flight_server = FlightMCPServer()
