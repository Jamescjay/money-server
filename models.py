from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    accounts = db.relationship('Account', back_populates='user', cascade="all, delete")
    sent_transactions = db.relationship('Transaction', foreign_keys="[Transaction.sender_id]", back_populates='sender')
    received_transactions = db.relationship('Transaction', foreign_keys="[Transaction.receiver_id]", back_populates='receiver')
    compliance_documents = db.relationship('Compliance', back_populates='user', cascade="all, delete")
    notifications = db.relationship('Notification', back_populates='user', cascade="all, delete")
    otps = db.relationship('Otp', back_populates='user', cascade="all, delete")
    security_logs = db.relationship('Security', back_populates='user', cascade="all, delete")

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())  
    user = db.relationship('Users', back_populates='accounts')

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    transaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    sender = db.relationship('Users', foreign_keys=[sender_id], back_populates='sent_transactions')
    receiver = db.relationship('Users', foreign_keys=[receiver_id], back_populates='received_transactions')
    security_logs = db.relationship('Security', back_populates='transaction', cascade="all, delete")

class Compliance(db.Model):
    __tablename__ = 'compliances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)
    document_url = db.Column(db.String(255), nullable=False)  
    verification_status = db.Column(db.String(20), nullable=False, default="pending")
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('Users', back_populates='compliance_documents')

    __table_args__ = (
        db.CheckConstraint("document_type IN ('ID', 'Passport', 'Driver License')", name="check_document_type"),
        db.CheckConstraint("verification_status IN ('pending', 'verified', 'rejected')", name="check_verification_status"),
    )

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="unread") 
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    user = db.relationship('Users', back_populates='notifications')

class Otp(db.Model):
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False, unique=True)
    expiry_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5), nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='otps')

class Security(db.Model):
    __tablename__ = 'security'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete="CASCADE"), nullable=True)
    risk_score = db.Column(db.Float, nullable=False)
    fraud_flag = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(255), nullable=True)
    logged_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    user = db.relationship('Users', back_populates='security_logs')
    transaction = db.relationship('Transaction', back_populates='security_logs')