"""
Flight Booking Agent
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from mcp_servers.flight_server import flight_server
from shared.protocols import MCPToolCall


class FlightAgent(BaseAgent):
    """Agent for flight search and booking"""
    
    def __init__(self, agent_id: str = "flight_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="flight",
            capabilities=["search_flights", "book_flight", "get_flight_details"]
        )
        self.mcp_server = flight_server
    
    def _register_handlers(self):
        """Register flight-specific handlers"""
        self.register_handler("search_flights", self.search_flights)
        self.register_handler("book_flight", self.book_flight)
        self.register_handler("get_flight_details", self.get_flight_details)
    
    async def search_flights(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for flights"""
        tool_call = MCPToolCall(
            tool_name="search_flights",
            arguments=parameters,
            context=context
        )
        
        result = await self.mcp_server.handle_tool_call(tool_call)
        
        if result.success:
            return {
                "flights": result.result,
                "count": len(result.result)
            }
        else:
            return {
                "error": result.error,
                "flights": []
            }
    
    async def book_flight(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Book a flight"""
        tool_call = MCPToolCall(
            tool_name="book_flight",
            arguments=parameters,
            context=context
        )
        
        result = await self.mcp_server.handle_tool_call(tool_call)
        
        if result.success:
            return result.result
        else:
            return {
                "success": False,
                "error": result.error
            }
    
    async def get_flight_details(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get flight details"""
        tool_call = MCPToolCall(
            tool_name="get_flight_details",
            arguments=parameters,
            context=context
        )
        
        result = await self.mcp_server.handle_tool_call(tool_call)
        
        if result.success:
            return result.result
        else:
            return {
                "error": result.error
            }


# Global instance
flight_agent = FlightAgent()
