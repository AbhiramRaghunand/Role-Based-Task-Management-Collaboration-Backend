from flask import Blueprint,request,jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required

auth_bp=Blueprint('auth',__name__)

@auth_bp.route('/signup',methods=['POST'])
def signup():
    data=request.get_json()

    name=data.get('name')
    email=data.get('email')
    password=data.get('password')
    role=data.get('role','USER')

    if not all([name,email,password]):
        return jsonify({'message':'Missing required fields'}),400
    
    user=User(
        name=name,
        email=email,
        role=role
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
    
    access_token=create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token':access_token,
        'user':{
            'id':user.id,
            'name':user.name,
            'email':user.email,
            'role':user.role
        }
    })


@auth_bp.route('/protected',methods=['GET'])
@jwt_required()
def protected():
    current_user_id=get_jwt_identity()
    current_user=User.query.get(current_user_id)

    return jsonify({
        "id":current_user.id,
        "name":current_user.name,
        "email":current_user.email,
        "role":current_user.role
    })
