"""
Base MCP Server implementation
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from shared.protocols import MCPTool, MCPToolCall, MCPToolResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseMCPServer(ABC):
    """Abstract base class for MCP servers"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()
        logger.info(f"✓ Initialized MCP Server: {name} v{version}")
    
    @abstractmethod
    def _register_tools(self):
        """Register available tools - must be implemented by subclasses"""
        pass
    
    def register_tool(self, tool: MCPTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"  Registered tool: {tool.name}")
    
    def list_tools(self) -> List[MCPTool]:
        """List all available tools"""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool"""
        return self.tools.get(tool_name)
    
    async def handle_tool_call(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Handle a tool call"""
        try:
            tool = self.get_tool(tool_call.tool_name)
            if not tool:
                return MCPToolResult(
                    success=False,
                    error=f"Tool '{tool_call.tool_name}' not found"
                )
            
            # Validate arguments against schema
            # (In production, use jsonschema validation)
            
            # Call the tool implementation
            result = await self._execute_tool(
                tool_call.tool_name,
                tool_call.arguments,
                tool_call.context
            )
            
            return MCPToolResult(success=True, result=result)
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_call.tool_name}: {e}")
            return MCPToolResult(
                success=False,
                error=str(e)
            )
    
    @abstractmethod
    async def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a tool - must be implemented by subclasses"""
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": self.name,
            "version": self.version,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in self.tools.values()
            ]
        }
