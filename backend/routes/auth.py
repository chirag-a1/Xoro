# backend/routes/auth.py

from datetime import timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models import db, bcrypt, User, Portfolio

auth_bp = Blueprint("auth", __name__)

def validate_json():
    """Validate and return JSON data from request."""
    if not request.is_json:
        return None, jsonify({"error": "Content-Type must be application/json"}), 400
    
    try:
        data = request.get_json(silent=True)
        if data is None:
            return None, jsonify({"error": "Invalid JSON format"}), 400
        return data, None, None
    except Exception as e:
        return None, jsonify({"error": "Invalid JSON format"}), 400

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present and not empty."""
    missing_fields = []
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data, error_response, status_code = validate_json()
    if error_response:
        return error_response, status_code
    
    # Validate required fields
    required_fields = ["username", "email", "password"]
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    # Extract and clean data
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    # Validate email format
    if not User.validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password strength
    if not User.validate_password(password):
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    # Validate username length
    if len(username) < 3 or len(username) > 20:
        return jsonify({"error": "Username must be between 3 and 20 characters"}), 400
    
    # Hash password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    try:
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create portfolio for user
        portfolio = Portfolio(user_id=user.id, cash=100000.00)
        db.session.add(portfolio)
        
        db.session.commit()
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=12),
            additional_claims={"username": user.username}
        )
        
        return jsonify({
            "success": True,
            "token": access_token,
            "user": user.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        if "username" in str(e):
            return jsonify({"error": "Username already exists"}), 409
        elif "email" in str(e):
            return jsonify({"error": "Email already exists"}), 409
        else:
            return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token."""
    data, error_response, status_code = validate_json()
    if error_response:
        return error_response, status_code

    # Validate required fields
    required_fields = ["username", "password"]
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    # Extract credentials
    identifier = data.get("username", "").strip()
    password = data.get("password", "")

    # Demo login check
    if identifier == "demo" and password == "demo123":
        # Create a demo user object for JWT
        demo_user = {
            'id': 1,
            'username': 'demo',
            'email': 'demo@example.com',
            'created_at': '2024-01-01T00:00:00Z'
        }

        # Create JWT token
        access_token = create_access_token(
            identity=str(1),
            expires_delta=timedelta(hours=12),
            additional_claims={"username": "demo"}
        )

        return jsonify({
            "success": True,
            "token": access_token,
            "user": demo_user
        }), 200

    # Find user by username or email
    user = User.query.filter_by(username=identifier).first()
    if user is None:
        user = User.query.filter_by(email=identifier.lower()).first()

    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    # Check password
    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=12),
        additional_claims={"username": user.username}
    )

    return jsonify({
        "success": True,
        "token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_jwt_identity()

        # Handle demo user
        if user_id == "1":
            demo_user = {
                'id': 1,
                'username': 'demo',
                'email': 'demo@example.com',
                'created_at': '2024-01-01T00:00:00Z'
            }
            return jsonify({
                "success": True,
                "user": demo_user
            }), 200

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "success": True,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        print(f"Get user error: {e}")
        return jsonify({"error": "Failed to get user information"}), 500

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh_token():
    """Refresh JWT token."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create new token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=12),
            additional_claims={"username": user.username}
        )
        
        return jsonify({
            "success": True,
            "token": access_token
        }), 200
        
    except Exception as e:
        print(f"Token refresh error: {e}")
        return jsonify({"error": "Failed to refresh token"}), 500

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user (client-side token removal)."""
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200