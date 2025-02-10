from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    sent_transactions = db.relationship('Transaction', foreign_keys='Transaction.sender_id', back_populates='sender')
    received_transactions = db.relationship('Transaction', foreign_keys='Transaction.receiver_id', back_populates='receiver')

    accounts = db.relationship('Account', back_populates='user', cascade="all, delete")

class Account(db.Model):
    __tablename__ =  "accounts"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    balance = db.Column(db.Float, default = 0.0, nullable = False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())  
    user = db.relationship('User', back_populates='accounts')

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    transaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_transactions')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_transactions')

class Compliance(db.Model):
    __tablename__ = 'compliances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    document_type = db.Column(db.String(20), nullable=False, 
                              check_constraints="document_type IN ('ID')")
    document_url = db.Column(db.String(255), nullable=False)  
    verification_status = db.Column(db.String(20), nullable=False, default="pending",
                                    check_constraints="verification_status IN ('pending', 'verified', 'rejected')")
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='compliance_documents')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="unread") 
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    user = db.relationship('User', back_populates='notifications')

class Otp(db.Model):
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='otps')

class Security(db.Model):
    __tablename__ = 'security'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete="CASCADE"), nullable=True)
    risk_score = db.Column(db.Float, nullable=False)
    fraud_flag = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(255), nullable=True)
    logged_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

    user = db.relationship('User', back_populates='security_logs')
    transaction = db.relationship('Transaction')    