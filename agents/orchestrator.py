"""
Orchestrator Agent - Coordinates multi-step workflows
"""
from typing import Dict, Any, List, Optional
import asyncio
import uuid
from datetime import datetime
from .base_agent import BaseAgent
from shared.redis_client import redis_client
from shared.database import get_session, Booking, User
import logging

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a step in a workflow"""
    def __init__(self, agent_id: str, action: str, parameters: Dict[str, Any]):
        self.agent_id = agent_id
        self.action = action
        self.parameters = parameters
        self.result = None
        self.status = "pending"  # pending, completed, failed


class Workflow:
    """Represents a multi-step workflow"""
    def __init__(self, workflow_id: str, workflow_type: str):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.steps: List[WorkflowStep] = []
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.completed_steps = []
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow"""
        self.steps.append(step)
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next pending step"""
        for step in self.steps:
            if step.status == "pending":
                return step
        return None


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent for coordinating complex workflows"""
    
    def __init__(self, agent_id: str = "orchestrator"):
        super().__init__(
            agent_id=agent_id,
            agent_type="orchestrator",
            capabilities=["create_workflow", "execute_workflow", "rollback_workflow"]
        )
        self.active_workflows: Dict[str, Workflow] = {}
    
    def _register_handlers(self):
        """Register orchestrator handlers"""
        self.register_handler("book_complete_trip", self.book_complete_trip)
        self.register_handler("book_flight_only", self.book_flight_only)
    
    async def book_complete_trip(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Book a complete trip (flight + hotel + payment)"""
        try:
            workflow_id = str(uuid.uuid4())
            workflow = Workflow(workflow_id, "complete_trip")
            
            # Step 1: Search and select flight
            workflow.add_step(WorkflowStep(
                agent_id="flight_agent",
                action="search_flights",
                parameters={
                    "origin": parameters["origin"],
                    "destination": parameters["destination"],
                    "date": parameters["departure_date"],
                    "passengers": parameters["passengers"]
                }
            ))
            
            # Step 2: Process payment
            workflow.add_step(WorkflowStep(
                agent_id="payment_agent",
                action="process_payment",
                parameters={
                    "amount": parameters["total_amount"],
                    "currency": "USD",
                    "payment_method": parameters["payment_method"],
                    "metadata": {
                        "workflow_id": workflow_id,
                        "booking_type": "complete_trip"
                    }
                }
            ))
            
            # Step 3: Book flight
            workflow.add_step(WorkflowStep(
                agent_id="flight_agent",
                action="book_flight",
                parameters={
                    "flight_id": parameters.get("selected_flight_id"),
                    "passenger_details": parameters["passenger_details"]
                }
            ))
            
            # Execute workflow
            result = await self.execute_workflow(workflow)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in book_complete_trip: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def book_flight_only(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Book flight only workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            workflow = Workflow(workflow_id, "flight_only")
            
            # Step 1: Search flights
            workflow.add_step(WorkflowStep(
                agent_id="flight_agent",
                action="search_flights",
                parameters={
                    "origin": parameters["origin"],
                    "destination": parameters["destination"],
                    "date": parameters["date"],
                    "passengers": parameters["passengers"]
                }
            ))
            
            result = await self.execute_workflow(workflow)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in book_flight_only: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a workflow step by step"""
        self.active_workflows[workflow.workflow_id] = workflow
        workflow.status = "executing"
        
        logger.info(f"🚀 Executing workflow: {workflow.workflow_id} ({workflow.workflow_type})")
        
        try:
            for i, step in enumerate(workflow.steps):
                logger.info(f"  Step {i+1}/{len(workflow.steps)}: {step.action} via {step.agent_id}")
                
                # Send message to agent
                message_id = await self.send_message(
                    to_agent=step.agent_id,
                    action=step.action,
                    parameters=step.parameters,
                    context={"workflow_id": workflow.workflow_id}
                )
                
                # Wait for response (simplified - in production use proper async waiting)
                await asyncio.sleep(1)
                
                # Mock response (in production, wait for actual A2A response)
                step.status = "completed"
                step.result = {"success": True, "message_id": message_id}
                workflow.completed_steps.append(step)
                
                logger.info(f"  ✓ Step {i+1} completed")
            
            workflow.status = "completed"
            
            logger.info(f"✓ Workflow completed: {workflow.workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow.workflow_id,
                "status": "completed",
                "steps_completed": len(workflow.completed_steps),
                "results": [step.result for step in workflow.completed_steps]
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            workflow.status = "failed"
            
            # Rollback completed steps
            await self.rollback_workflow(workflow)
            
            return {
                "success": False,
                "workflow_id": workflow.workflow_id,
                "error": str(e),
                "rollback_completed": True
            }
    
    async def rollback_workflow(self, workflow: Workflow):
        """Rollback completed steps in reverse order"""
        logger.info(f"🔄 Rolling back workflow: {workflow.workflow_id}")
        
        for step in reversed(workflow.completed_steps):
            logger.info(f"  Rolling back: {step.action}")
            
            # Implement rollback logic based on step type
            if step.action == "process_payment":
                # Refund payment
                await self.send_message(
                    to_agent="payment_agent",
                    action="refund_payment",
                    parameters={"payment_id": step.result.get("payment_id")},
                    context={"workflow_id": workflow.workflow_id, "rollback": True}
                )
            elif step.action == "book_flight":
                # Cancel flight booking
                logger.info(f"  Would cancel flight booking: {step.result}")
        
        logger.info(f"✓ Rollback completed for workflow: {workflow.workflow_id}")


# Global instance
orchestrator = OrchestratorAgent()
