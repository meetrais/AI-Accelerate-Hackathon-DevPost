"""
Protocol definitions for A2A and AP2
"""
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ============================================================================
# A2A Protocol (Agent-to-Agent)
# ============================================================================

class MessageType(str, Enum):
    """A2A Message types"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    NOTIFICATION = "notification"


class A2AMessage(BaseModel):
    """Standard A2A message format"""
    protocol: str = Field(default="a2a/v1", description="Protocol version")
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = Field(..., description="Source agent ID")
    to_agent: str = Field(..., description="Target agent ID")
    message_type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(..., description="Message payload")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Shared context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class A2ARequest(A2AMessage):
    """A2A Request message"""
    message_type: MessageType = MessageType.REQUEST
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class A2AResponse(A2AMessage):
    """A2A Response message"""
    message_type: MessageType = MessageType.RESPONSE
    success: bool = Field(..., description="Whether request succeeded")
    result: Optional[Dict[str, Any]] = Field(default=None)
    error: Optional[str] = Field(default=None)


# ============================================================================
# AP2 Protocol (Agent Payment Protocol)
# ============================================================================

class PaymentMethodType(str, Enum):
    """Payment method types"""
    CARD = "card"
    DIGITAL_WALLET = "digital_wallet"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(BaseModel):
    """Payment method details"""
    type: PaymentMethodType
    token: str = Field(..., description="Tokenized payment method")
    last_four: Optional[str] = Field(default=None, description="Last 4 digits")
    brand: Optional[str] = Field(default=None, description="Card brand or wallet type")
    billing_address: Optional[Dict[str, str]] = Field(default=None)


class PaymentAmount(BaseModel):
    """Payment amount"""
    value: float = Field(..., gt=0, description="Amount value")
    currency: str = Field(default="USD", description="Currency code")
    
    def to_cents(self) -> int:
        """Convert to cents for payment processing"""
        return int(self.value * 100)


class AP2PaymentRequest(BaseModel):
    """AP2 Payment request"""
    protocol: str = Field(default="ap2/v1", description="Protocol version")
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str = Field(..., description="payment_process or payment_refund")
    amount: PaymentAmount
    payment_method: PaymentMethod
    merchant: Dict[str, str] = Field(..., description="Merchant information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AP2PaymentResponse(BaseModel):
    """AP2 Payment response"""
    protocol: str = Field(default="ap2/v1")
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = Field(default=None)
    amount: PaymentAmount
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    receipt_url: Optional[str] = Field(default=None)
    error: Optional[str] = Field(default=None)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# MCP Protocol Types
# ============================================================================

class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str


class MCPToolCall(BaseModel):
    """MCP Tool call request"""
    tool_name: str
    arguments: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class MCPToolResult(BaseModel):
    """MCP Tool call result"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
