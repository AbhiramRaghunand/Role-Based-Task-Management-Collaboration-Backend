from app import db
from app.models.audit import TaskAudit

def log_task_action(task_id,action,user_id):
    audit=TaskAudit(
        task_id=task_id,
        action=action,
        performed_by=user_id
    )
    db.session.add(audit)