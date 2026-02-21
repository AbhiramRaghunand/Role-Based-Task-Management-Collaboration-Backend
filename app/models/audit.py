from app import db
from datetime import datetime

class TaskAudit(db.Model):
    __tablename__="task_audit"

    id=db.Column(db.Integer,primary_key=True)
    task_id=db.Column(db.Integer,db.ForeignKey("tasks.id"),nullable=False)
    action=db.Column(db.String(50),nullable=False)
    performed_by=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.now(),nullable=False)
