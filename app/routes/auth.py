from flask import Blueprint,request,jsonify
from app import db
from app.models.user import User

auth_bp=Blueprint('auth',__name__)

@auth_bp.route('/signup',methods=['POST'])
def signup():
    data=request.get_json()

    name=data.get('name')
    email=data.get('email')
    password=data.get('password')

    if not all([name,email,password]):
        return jsonify({'message':'Missing required fields'}),400
    
    user=User(
        name=name,
        email=email,
        role="USER"
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message':'User created successfully',
        'user':{
            'id':user.id,
            'name':user.name,
            'email':user.email,
            'role':user.role
        }
    })

@auth_bp.route('/login',methods=['POST'])
def login():
    data=request.get_json()

    email=data.get('email')
    password=data.get('password')

    if not all([email,password]):
        return jsonify({'message':'Missing required fields'}),400
    
    user=User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message':'Invalid credentials'}),401
    
    return jsonify({
        'message':'Login successful',
        'user':{
            'id':user.id,
            'name':user.name,
            'email':user.email,
            'role':user.role
        }
    })