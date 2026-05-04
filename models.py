"""
Database Models for Land Registration System
Using SQLAlchemy ORM with SQLite
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for both Land Owners and Buyers"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default='buyer')  # 'owner' or 'buyer'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owned_lands = db.relationship('Land', backref='owner', lazy=True, foreign_keys='Land.owner_id')
    sent_offers = db.relationship('Offer', backref='buyer', lazy=True, foreign_keys='Offer.buyer_id')
    received_offers = db.relationship('Offer', backref='seller', lazy=True, foreign_keys='Offer.seller_id')
    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Land(db.Model):
    """Land property model"""
    
    __tablename__ = 'lands'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    size_sqft = db.Column(db.Float, nullable=False)  # Size in square feet
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True, index=True)
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('LandDocument', backref='land', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('LandImage', backref='land', lazy=True, cascade='all, delete-orphan')
    offers = db.relationship('Offer', backref='land', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='land', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_owner: bool = True) -> dict:
        """Convert land to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'size_sqft': self.size_sqft,
            'price': self.price,
            'is_available': self.is_available,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'images': [img.to_dict() for img in self.images],
            'documents': [doc.to_dict() for doc in self.documents]
        }
        
        if include_owner:
            data['owner'] = self.owner.to_dict() if self.owner else None
        
        return data


class LandDocument(db.Model):
    """Documents for land ownership (PDF, images, etc.)"""
    
    __tablename__ = 'land_documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_id = db.Column(db.String(36), db.ForeignKey('lands.id'), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False)  # 'titleDeeds', 'surveyReport', 'taxDocument'
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_fraud_detected = db.Column(db.Boolean, default=False)
    fraud_confidence = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    
    def to_dict(self) -> dict:
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'land_id': self.land_id,
            'document_type': self.document_type,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at.isoformat(),
            'is_verified': self.is_verified,
            'is_fraud_detected': self.is_fraud_detected,
            'fraud_confidence': self.fraud_confidence
        }


class LandImage(db.Model):
    """Images for land listings"""
    
    __tablename__ = 'land_images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_id = db.Column(db.String(36), db.ForeignKey('lands.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert image to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'is_primary': self.is_primary,
            'uploaded_at': self.uploaded_at.isoformat()
        }


class Offer(db.Model):
    """Negotiation offers from buyers to sellers"""
    
    __tablename__ = 'offers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_id = db.Column(db.String(36), db.ForeignKey('lands.id'), nullable=False, index=True)
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    offered_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, withdrawn
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert offer to dictionary"""
        return {
            'id': self.id,
            'land_id': self.land_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'offered_price': self.offered_price,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Message(db.Model):
    """Real-time chat messages for negotiations"""
    
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.String(36), nullable=False, index=True)
    land_id = db.Column(db.String(36), nullable=False, index=True)
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'land_id': self.land_id,
            'message_text': self.message_text,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class Transaction(db.Model):
    """Completed land transactions recorded in blockchain"""
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    land_id = db.Column(db.String(36), db.ForeignKey('lands.id'), nullable=False, index=True)
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    final_amount = db.Column(db.Float, nullable=False)
    blockchain_hash = db.Column(db.String(64))  # Hash of the transaction in blockchain
    blockchain_index = db.Column(db.Integer)  # Block index in blockchain
    status = db.Column(db.String(20), default='completed')  # completed, pending, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'land_id': self.land_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'final_amount': self.final_amount,
            'blockchain_hash': self.blockchain_hash,
            'blockchain_index': self.blockchain_index,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Recommendation(db.Model):
    """AI-based land recommendations for buyers"""
    
    __tablename__ = 'recommendations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    land_id = db.Column(db.String(36), db.ForeignKey('lands.id'), nullable=False, index=True)
    score = db.Column(db.Float)  # Recommendation score (0.0 to 1.0)
    reason = db.Column(db.Text)  # Why it was recommended
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self) -> dict:
        """Convert recommendation to dictionary"""
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'land_id': self.land_id,
            'score': self.score,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }
