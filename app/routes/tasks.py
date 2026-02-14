
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.utils.rbac import role_required
from app.models.tasks import Task


tasks_bp=Blueprint('tasks',__name__)

@tasks_bp.route('/tasks',methods=['POST'])
@role_required('MANAGER','ADMIN')
def create_task():
    data=request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify({"error":"Title is required"}),400
    
    task=Task(
        title=data["title"],
        description=data.get("description"),
        created_by=int(get_jwt_identity())
    )
    from app import db
    db.session.add(task)
    db.session.commit()

    return jsonify({"message":"Task Created successfully","task":task.__repr__()}),201

@tasks_bp.route('/tasks',methods=['GET'])
@role_required('USER','MANAGER','ADMIN')
def view_task():
    tasks=Task.query.all()

    return jsonify({
        "message":"Task details",
        "tasks": [task.__repr__() for task in tasks]
    }),200
