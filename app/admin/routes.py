from flask import Blueprint, request, jsonify
from .. import db, bcrypt
from ..models import User, Task
from ..decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@admin_bp.route('/user/<int:user_id>/password', methods=['PUT'])
@admin_required
def change_user_password(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    hashed_pw = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    user.password = hashed_pw
    db.session.commit()
    return jsonify({'msg': 'Password updated'})

@admin_bp.route('/user', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_pw, role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'User created by admin'})

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user.role == 'admin':
        return jsonify({'message': 'Tidak bisa menghapus admin lain'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
