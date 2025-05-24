from flask import Blueprint, request, jsonify
from .. import db, bcrypt
from ..models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_jwt_extended import decode_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.username, expires_delta=timedelta(days=1))
        return jsonify({'access_token': access_token})
    return jsonify({'msg': 'Invalid credentials'}), 401

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    # Buat reset token dengan expiry pendek
    reset_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=15))
    
    return jsonify({'reset_token': reset_token}), 200

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    token = data.get('reset_token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([token, new_password, confirm_password]):
        return jsonify({'msg': 'All fields are required'}), 400

    if new_password != confirm_password:
        return jsonify({'msg': 'Passwords do not match'}), 400

    try:
        decoded = decode_token(token)
        username = decoded['sub']
    except Exception as e:
        return jsonify({'msg': 'Invalid or expired token'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_pw
    db.session.commit()

    return jsonify({'msg': 'Password updated successfully'}), 200