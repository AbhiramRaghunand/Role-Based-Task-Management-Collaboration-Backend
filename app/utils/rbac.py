from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args,**kwargs):

            #ensure JWT is present
            verify_jwt_in_request()

            from app.models.user import User

            #get current user identity
            user_id=get_jwt_identity()
            user=User.query.get(int(user_id))

            if not user:
                return jsonify({"Error":"User not found"}),401
            
            #Admin override
            if user.role=="admin":
                return fn(*args,**kwargs)
            
            #role check
            if user.role not in allowed_roles:
                return jsonify({"Error":"Access denied"}),403
            
            return fn(*args,**kwargs)
        return wrapper
    return decorator