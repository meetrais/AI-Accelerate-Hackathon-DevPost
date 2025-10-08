"""
Database models and connection management
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Enum as SQLEnum, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import enum

Base = declarative_base()


class BookingType(str, enum.Enum):
    """Booking types"""
    FLIGHT = "flight"
    HOTEL = "hotel"
    ACTIVITY = "activity"
    PACKAGE = "package"


class BookingStatus(str, enum.Enum):
    """Booking status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, enum.Enum):
    """Payment status"""
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(BookingType), nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    
    # Booking details (JSON for flexibility)
    details = Column(JSON, nullable=False)
    
    # Pricing
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Confirmation
    confirmation_number = Column(String, unique=True)
    provider_booking_id = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment method (tokenized)
    payment_method_token = Column(String)
    payment_method_type = Column(String)
    last_four = Column(String)
    
    # Transaction details
    transaction_id = Column(String, unique=True)
    receipt_url = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
    refunded_at = Column(DateTime)
    
    # Relationships
    booking = relationship("Booking", back_populates="payment")


class AgentState(Base):
    """Agent state tracking"""
    __tablename__ = "agent_states"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, unique=True, nullable=False)
    agent_type = Column(String, nullable=False)
    status = Column(String, default="idle")  # idle, busy, error
    current_task = Column(JSON)
    capabilities = Column(JSON)
    load = Column(Float, default=0.0)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database connection management
def get_database_url():
    """Get database URL from environment"""
    return os.getenv(
        'POSTGRES_URL',
        'postgresql://travel_user:travel_pass@localhost:5432/travel_assistant'
    )


def create_db_engine():
    """Create database engine"""
    return create_engine(get_database_url(), echo=False)


def get_session():
    """Get database session"""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize database tables"""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    print("✓ Database tables created")


if __name__ == "__main__":
    init_database()
