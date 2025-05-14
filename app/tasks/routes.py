from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Task, User
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    tasks = Task.query.filter_by(user_id=user.id).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'status': task.status
    } for task in tasks])

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    data = request.get_json()

    new_task = Task(
        title=data['title'],
        status=data.get('status', 'pending'),
        user_id=user.id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'msg': 'Task created'})

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    task = Task.query.get_or_404(task_id)

    if task.user_id != user.id:
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.status = data.get('status', task.status)
    db.session.commit()

    return jsonify({'msg': 'Task updated'})

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        return jsonify({'msg': 'Unauthorized'}), 403
    db.session.delete(task)
    db.session.commit()
    return jsonify({'msg': 'Task deleted'})

@tasks_bp.route('/incomplete', methods=['GET'])
@jwt_required()
def incomplete_tasks():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    tasks = Task.query.filter_by(user_id=user.id, status='pending').count()
    return jsonify({'incomplete_tasks': tasks})