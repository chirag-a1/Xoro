# backend/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
import re

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

# Association table for watchlist
watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('stock_symbol', db.String(20), primary_key=True)
)

class User(db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    portfolio = db.relationship('Portfolio', back_populates='user', uselist=False, cascade="all, delete-orphan")
    trades = db.relationship('Trade', backref='user', lazy=True, cascade="all, delete-orphan")
    # Watchlist relationship - removed for now to fix the error
    # watchlist_stocks = db.relationship('Stock', secondary=watchlist, lazy='subquery',
    #                                    backref=db.backref('watchlisted_by', lazy=True))
    
    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength."""
        return len(password) >= 6
    
    def __repr__(self):
        return f'<User {self.username}>'

class Portfolio(db.Model):
    """Portfolio model to track user's cash and holdings."""
    __tablename__ = 'portfolio'
    
    id = db.Column(db.Integer, primary_key=True)
    cash = db.Column(db.Float, nullable=False, default=100000.00)  # Starting virtual cash
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Relationships
    user = db.relationship('User', back_populates='portfolio')
    holdings = db.relationship('Stock', back_populates='portfolio', cascade="all, delete-orphan")
    
    def get_total_value(self):
        """Calculate total portfolio value."""
        total = self.cash
        for holding in self.holdings:
            # This would need current price from market data
            total += holding.quantity * holding.average_price
        return total
    
    def to_dict(self):
        """Convert portfolio to dictionary."""
        return {
            'id': self.id,
            'balance': self.cash,
            'total_value': self.get_total_value(),
            'holdings': [holding.to_dict() for holding in self.holdings]
        }
    
    def __repr__(self):
        return f'<Portfolio User ID: {self.user_id}, Cash: ${self.cash:.2f}>'

class Stock(db.Model):
    """Stock holding within a user's portfolio."""
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    
    # Relationship
    portfolio = db.relationship('Portfolio', back_populates='holdings')
    
    # Ensure unique stock per portfolio
    __table_args__ = (db.UniqueConstraint('portfolio_id', 'symbol', name='_portfolio_symbol_uc'),)
    
    def get_current_value(self):
        """Get current value of holding."""
        return self.quantity * self.average_price
    
    def to_dict(self):
        """Convert stock to dictionary."""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'averagePrice': self.average_price,
            'currentPrice': self.average_price,  # Would be updated with real market data
            'totalValue': self.get_current_value()
        }
    
    @staticmethod
    def validate_symbol(symbol):
        """Validate stock symbol format."""
        return symbol and len(symbol) <= 10 and symbol.isalpha()
    
    def __repr__(self):
        return f'<Stock {self.symbol}: {self.quantity} shares @ ${self.average_price:.2f}>'

class Trade(db.Model):
    """Trade model to log all buy/sell transactions."""
    __tablename__ = 'trade'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    trade_type = db.Column(db.String(4), nullable=False)  # 'BUY' or 'SELL'
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_total_value(self):
        """Get total value of trade."""
        return self.quantity * self.price
    
    def to_dict(self):
        """Convert trade to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'trade_type': self.trade_type,
            'total_value': self.get_total_value(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @staticmethod
    def validate_trade_type(trade_type):
        """Validate trade type."""
        return trade_type in ['BUY', 'SELL']
    
    def __repr__(self):
        return f'<Trade {self.trade_type} {self.quantity} {self.symbol} @ ${self.price:.2f}>'