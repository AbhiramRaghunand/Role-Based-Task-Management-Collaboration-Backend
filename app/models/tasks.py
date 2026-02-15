from app.extensions import db
from datetime import datetime

class Task(db.Model):
    __tablename__='tasks'

    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text,nullable=False)
    status=db.Column(db.String(20),default="PENDING",nullable=False)
    created_by=db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.now())

    def __repr__(self):
        return f"<Task {self.title} - Status: {self.status}>"
    
