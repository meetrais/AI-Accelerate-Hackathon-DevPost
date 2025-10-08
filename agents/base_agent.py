"""
Base Agent class for A2A communication
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import asyncio
import logging
from shared.protocols import A2AMessage, A2ARequest, A2AResponse, MessageType
from shared.message_queue import message_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for agents"""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: list):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = "idle"
        self.current_task = None
        self.message_handlers: Dict[str, Callable] = {}
        
        # Register default handlers
        self._register_handlers()
        
        logger.info(f"✓ Initialized {agent_type} agent: {agent_id}")
    
    @abstractmethod
    def _register_handlers(self):
        """Register message handlers - must be implemented by subclasses"""
        pass
    
    def register_handler(self, action: str, handler: Callable):
        """Register a handler for an action"""
        self.message_handlers[action] = handler
        logger.info(f"  Registered handler: {action}")
    
    async def send_message(self, to_agent: str, action: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """Send an A2A message to another agent"""
        request = A2ARequest(
            from_agent=self.agent_id,
            to_agent=to_agent,
            action=action,
            parameters=parameters,
            context=context,
            payload={"action": action, "parameters": parameters}
        )
        
        logger.info(f"→ {self.agent_id} sending {action} to {to_agent}")
        
        # Publish to message queue
        queue_name = f"agent_{to_agent}"
        message_queue.declare_queue(queue_name)
        message_queue.publish(queue_name, request)
        
        return request.message_id
    
    async def handle_message(self, message: A2AMessage):
        """Handle incoming A2A message"""
        try:
            if message.message_type == MessageType.REQUEST:
                request = A2ARequest(**message.model_dump())
                action = request.payload.get("action")
                
                logger.info(f"← {self.agent_id} received {action} from {request.from_agent}")
                
                if action in self.message_handlers:
                    self.status = "busy"
                    self.current_task = {"action": action, "message_id": request.message_id}
                    
                    # Execute handler
                    result = await self.message_handlers[action](request.payload.get("parameters", {}), request.context)
                    
                    # Send response
                    response = A2AResponse(
                        from_agent=self.agent_id,
                        to_agent=request.from_agent,
                        conversation_id=request.conversation_id,
                        success=True,
                        result=result,
                        payload={"result": result}
                    )
                    
                    queue_name = f"agent_{request.from_agent}"
                    message_queue.declare_queue(queue_name)
                    message_queue.publish(queue_name, response)
                    
                    self.status = "idle"
                    self.current_task = None
                    
                    logger.info(f"✓ {self.agent_id} completed {action}")
                else:
                    logger.warning(f"No handler for action: {action}")
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.status = "error"
    
    def start_listening(self):
        """Start listening for messages"""
        queue_name = f"agent_{self.agent_id}"
        message_queue.declare_queue(queue_name)
        
        logger.info(f"👂 {self.agent_id} listening on queue: {queue_name}")
        
        message_queue.consume(queue_name, lambda msg: asyncio.run(self.handle_message(msg)))
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "current_task": self.current_task
        }
