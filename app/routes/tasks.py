
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.utils.rbac import role_required
from app.models.tasks import Task
from app import db
from enum import Enum


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

    return jsonify({
        "message":"Task Created successfully","task":task.__repr__()}),201

@tasks_bp.route('/tasks',methods=['GET'])
@role_required('USER','MANAGER','ADMIN')
def view_task():
    from app.models.user import User
    current_user_id=int(get_jwt_identity())
    current_user=User.query.get(current_user_id)

    page=request.args.get("page",1,type=int)
    limit=request.args.get("limit",5,type=int)

    if page<1:
        page=1
    if limit<1:
        limit=5

    base_query=None

    if current_user.role=="ADMIN":
        base_query=Task.query

    elif current_user.role=="MANAGER":
        base_query=Task.query.filter_by(created_by=current_user.id)
    else:
        base_query=Task.query.filter_by(assigned_to=current_user.id)

    total_count=base_query.count()

    tasks=base_query.offset((page-1)* limit).limit(limit).all()



    return jsonify({
        "page":page,
        "limit":limit,
        "total_tasks":total_count,
        "total_pages":(total_count+limit-1)//limit,
        "offset":(page-1)*limit,
        "data":[
            {
            "id":t.id,
            "title":t.title,
            "status":t.status,
            "assigned_to":t.assigned_to,
            "created_by":t.created_by
            }for t in tasks
        ]
    }),200

@tasks_bp.route('/tasks/<int:task_id>/status',methods=['PATCH'])
@role_required('USER','MANAGER','ADMIN')
def update_task(task_id):
    data=request.get_json(silent=True)

    if not data or "status" not in data:
        return jsonify({
            "error":"Status required"
        }),400
    
    new_status=data['status'].upper()
    allowed_status=['PENDING','IN_PROGRESS','DONE']

    if new_status not in allowed_status:
        return jsonify({
            "error":"Invalid status value"
        }),400
    
    task=Task.query.get(task_id)

    if not task:
        return jsonify({
            "error":"Task not found"
        }),404
    
    task.status=new_status
    db.session.commit()

    return jsonify({
        "message":"Task Status Updated",
        "task_id":task_id,
        "new_status":new_status
    }),200

@tasks_bp.route('/tasks/<task_id>/assign', methods=["PUT"])
@role_required("MANAGER","ADMIN")
def assign_task(task_id):
    data=request.get_json(silent=True)

    if not data or "user_id" not in data:
        return jsonify({
            "error":"user_id required"
        }),400
    
    task=Task.query.get(task_id)
    if not task:
        return jsonify({
            "error":"Task not found"
        }),404
    
    from app.models.user import User
    user=User.query.get(data['user_id'])

    if not user:
        return jsonify({
            "error":"User not found"
        }),404
    
    task.assigned_to=user.id
    db.session.commit()

    return jsonify({
        "message":"Task Assigned successfully",
        "task_id":task.id,
        "assigned_to":task.assigned_to
    }),200
    


