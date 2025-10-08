"""
Payment Agent with AP2 Protocol
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from .base_agent import BaseAgent
from shared.protocols import AP2PaymentRequest, AP2PaymentResponse, PaymentStatus, PaymentAmount, PaymentMethod
from shared.database import get_session, Payment, Booking
import logging

logger = logging.getLogger(__name__)


class PaymentAgent(BaseAgent):
    """Agent for payment processing using AP2 protocol"""
    
    def __init__(self, agent_id: str = "payment_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="payment",
            capabilities=["process_payment", "refund_payment", "validate_payment_method"]
        )
    
    def _register_handlers(self):
        """Register payment-specific handlers"""
        self.register_handler("process_payment", self.process_payment)
        self.register_handler("refund_payment", self.refund_payment)
        self.register_handler("validate_payment_method", self.validate_payment_method)
    
    async def process_payment(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process payment using AP2 protocol"""
        try:
            # Build AP2 payment request
            payment_request = AP2PaymentRequest(
                action="payment_process",
                amount=PaymentAmount(
                    value=parameters["amount"],
                    currency=parameters.get("currency", "USD")
                ),
                payment_method=PaymentMethod(
                    type=parameters["payment_method"]["type"],
                    token=parameters["payment_method"]["token"],
                    last_four=parameters["payment_method"].get("last_four"),
                    brand=parameters["payment_method"].get("brand")
                ),
                merchant={
                    "id": "travel_assistant",
                    "descriptor": "Travel Booking"
                },
                metadata=parameters.get("metadata", {})
            )
            
            logger.info(f"Processing AP2 payment: {payment_request.payment_id}")
            
            # Mock payment processing (in production, integrate with Stripe/PayPal)
            # Simulate payment processing
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
            
            # Create payment response
            payment_response = AP2PaymentResponse(
                payment_id=payment_request.payment_id,
                status=PaymentStatus.COMPLETED,
                transaction_id=transaction_id,
                amount=payment_request.amount,
                receipt_url=f"https://example.com/receipt/{transaction_id}"
            )
            
            # Save to database (only if booking_id provided)
            booking_id = parameters.get("metadata", {}).get("booking_id")
            if booking_id:
                session = get_session()
                try:
                    payment = Payment(
                        id=payment_request.payment_id,
                        booking_id=booking_id,
                        amount=payment_request.amount.value,
                        currency=payment_request.amount.currency,
                        status="paid",
                        payment_method_token=payment_request.payment_method.token,
                        payment_method_type=payment_request.payment_method.type,
                        last_four=payment_request.payment_method.last_four,
                        transaction_id=transaction_id,
                        receipt_url=payment_response.receipt_url,
                        paid_at=datetime.utcnow()
                    )
                    session.add(payment)
                    session.commit()
                    logger.info(f"✓ Payment saved to database: {payment_request.payment_id}")
                finally:
                    session.close()
            else:
                logger.info(f"✓ Payment processed (not persisted - no booking_id): {payment_request.payment_id}")
            
            return payment_response.model_dump()
            
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return {
                "payment_id": parameters.get("payment_id", str(uuid.uuid4())),
                "status": "failed",
                "error": str(e)
            }
    
    async def refund_payment(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process refund using AP2 protocol"""
        try:
            payment_id = parameters["payment_id"]
            amount = parameters.get("amount")  # Partial refund if specified
            
            logger.info(f"Processing refund for payment: {payment_id}")
            
            # Mock refund processing
            refund_id = f"rfnd_{uuid.uuid4().hex[:16]}"
            
            # Update database
            session = get_session()
            try:
                payment = session.query(Payment).filter_by(id=payment_id).first()
                if payment:
                    payment.status = "refunded"
                    payment.refunded_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"✓ Payment refunded: {payment_id}")
            finally:
                session.close()
            
            return {
                "success": True,
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": amount,
                "status": "refunded"
            }
            
        except Exception as e:
            logger.error(f"Refund error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_payment_method(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate payment method"""
        # Mock validation
        payment_method = parameters.get("payment_method", {})
        
        # Basic validation
        if not payment_method.get("token"):
            return {
                "valid": False,
                "error": "Payment method token is required"
            }
        
        return {
            "valid": True,
            "payment_method_type": payment_method.get("type", "card"),
            "last_four": payment_method.get("last_four")
        }


# Global instance
payment_agent = PaymentAgent()
