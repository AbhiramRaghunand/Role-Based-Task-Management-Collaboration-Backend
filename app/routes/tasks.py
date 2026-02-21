
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.utils.rbac import role_required
from app.models.tasks import Task
from app.models.audit import TaskAudit
from app import db
from enum import Enum
from app.utils.response import success_response,error_response
from app.utils.audit import log_task_action
from datetime import datetime


tasks_bp=Blueprint('tasks',__name__)

@tasks_bp.route('/tasks',methods=['POST'])
@role_required('MANAGER','ADMIN')
def create_task():
    data=request.get_json(silent=True)
    current_user_id=int(get_jwt_identity())
    if not data or "title" not in data:
        return error_response(message="Title is required",status_code=400)
    
    task=Task(
        title=data["title"],
        description=data.get("description"),
        created_by=current_user_id
    )
    from app import db
    db.session.add(task)
    db.session.flush()
    log_task_action(task.id,"CREATE",current_user_id)
    db.session.commit()

    return success_response(
        message="Task created successfully",
        data={"task_id":task.id},
        status_code=201
    )

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
        base_query=Task.query.filter_by(is_deleted=False)

    elif current_user.role=="MANAGER":
        base_query=Task.query.filter_by(created_by=current_user.id,is_deleted=False)
    else:
        base_query=Task.query.filter_by(assigned_to=current_user.id,is_deleted=False)

    #status filter
    status=request.args.get("status")
    if status:
        status=status.upper()
        allowed_status=['PENDING','IN_PROGRESS','DONE']
        if status not in allowed_status:
            return error_response("Invalid status filter",400)
        base_query=base_query.filter_by(status=status)

    #Sorting
    sort_field=request.args.get('sort','created_at',type=str)
    order=request.args.get('order','desc',type=str)

    #allowed fields
    allowed_sort_fields=['created_at','title','status']
    if sort_field not in allowed_sort_fields:
        return error_response("Invalid sort field",400)
    
    if order not in ["asc","desc"]:
        return error_response("Invalid sort order",400)
    
    #get column
    column=getattr(Task,sort_field)

    if order=='desc':
        column=column.desc()
    else:
        column=column.asc()

    base_query=base_query.order_by(column)

    #count before pagination
    total_count=base_query.count()

    #pagination
    tasks=base_query.offset((page-1)* limit).limit(limit).all()



    return success_response(
        message="Task fetched successfully",
        data={
            "page":page,
            "limit":limit,
            "total_tasks":total_count,
            "total_pages":(total_count+limit-1)//limit,
            "offset":(page-1)*limit,
            "tasks":[
                {
                "id":t.id,
                "title":t.title,
                "status":t.status,
                "assigned_to":t.assigned_to,
                "created_by":t.created_by
                }for t in tasks
            ]
        },
        status_code=200
    )

@tasks_bp.route('/tasks/<int:task_id>/status',methods=['PATCH'])
@role_required('USER','MANAGER','ADMIN')
def update_task(task_id):
    data=request.get_json(silent=True)

    current_user_id=int(get_jwt_identity())

    if not data or "status" not in data:
        return error_response(
            message="Status required",
            status_code=400
        )
    
    new_status=data['status'].upper()
    allowed_status=['PENDING','IN_PROGRESS','DONE']

    if new_status not in allowed_status:
        return error_response(
            message="Invalid status value",
            status_code=400
        )
    
    task=Task.query.filter_by(id=task_id,is_deleted=False)

    if not task:
        return error_response(
            message="Task not found",
            status_code=404
        )
    
    task.status=new_status
    log_task_action(task_id,"UPDATE_STATUS",current_user_id)
    db.session.commit()

    return success_response(
        message="Task status updated successfully",
        data={"task_id":task_id,"new_status":new_status},
        status_code=200
    )

@tasks_bp.route('/tasks/<task_id>/assign', methods=["PUT"])
@role_required("MANAGER","ADMIN")
def assign_task(task_id):
    data=request.get_json(silent=True)
    current_user_id=int(get_jwt_identity())
    if not data or "user_id" not in data:
        return error_response(
            message="User_id required",
            status_code=400
        )
    
    task=Task.query.filter_by(id=task_id,is_deleted=False)
    if not task:
        return error_response(
            message="Task not found",
            status_code=404
        )
    
    from app.models.user import User
    user=User.query.get(data['user_id'])

    if not user:
        return error_response(
            message="User not found",
            status_code=404
        )
    
    task.assigned_to=user.id
    log_task_action(task_id,"ASSIGN",current_user_id)
    db.session.commit()

    return success_response(
        message="Task assigned successfully",
        data={"task_id":task_id,"assigned_to":task.assigned_to},
        status_code=200
    )

@tasks_bp.route('/tasks/<task_id>/delete',methods=['DELETE'])
@role_required("MANAGER","ADMIN")
def delete_task(task_id):

    from app.models.user import User
    current_user_id=int(get_jwt_identity())
    current_user=User.query.get(current_user_id)

    task=Task.query.filter_by(id=task_id,is_deleted=False).first()

    if current_user.role=="MANAGER" and task.created_by!=current_user.id:
        return error_response("Not allowed to delete this task",403)
    
    if not task:
        return error_response("Task not found",404)
    
    task.is_deleted=True
    task.deleted_at=datetime.now()
    log_task_action(task_id,"DELETE",current_user_id)
    db.session.commit()

    return success_response(
        message="Task deleted successfully ",
        data={"task_id":task.id},
        status_code=200
    )


@tasks_bp.route("/tasks/<int:task_id>/restore",methods=["PATCH"])
@role_required("ADMIN")
def restore(task_id):
    current_user_id=int(get_jwt_identity())
    task=Task.query.filter_by(id=task_id,is_deleted=True).first()

    if not task:
        return error_response("Task not found",404)
    
    
    task.is_deleted=False
    task.deleted_at=None
    log_task_action(task_id,"RESTORE",current_user_id)
    db.session.commit()

    return success_response(
        message="Task restored successfully",
        data={"task_id":task_id},
        status_code=200
    )

@tasks_bp.route('/tasks/<int:task_id>/audit',methods=['GET'])
@role_required("ADMIN")
def veiw_audit(task_id):

    task=Task.query.filter_by(id=task_id).first()
    if not task:
        return error_response("Task not found",404)
    
    audits=TaskAudit.query.filter_by(task_id=task_id).order_by(TaskAudit.timestamp.desc()).all()

    audit_data=[
        {
            "action":audit.action,
            "performed_by":audit.performed_by,
            "timestamp":audit.timestamp
        }
        for audit in audits
    ]

    return success_response(
        message="Audit history fetched successfully",
        data={
            "task_id":task_id,
            "audit_logs":audit_data
        },
        status_code=200
    )



