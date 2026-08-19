from flask import Blueprint, jsonify, request
from backend.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not username or not email or not password:
        return jsonify({'status': 'error', 'message': 'Username, email and password are required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'status': 'error', 'message': 'Username or email already exists'}), 409

    user = User(
        username=username,
        email=email,
        password_hash=password, # In production this would be hashed with bcrypt
        role='commuter'
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    user = User.query.filter_by(username=username).first()
    if not user or user.password_hash != password:
        # Check email login
        user = User.query.filter_by(email=username).first()
        if not user or user.password_hash != password:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'token': f"token-for-{user.username}",
        'user': user.to_dict()
    })

@auth_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    username = request.args.get('username', 'commuter')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    })
