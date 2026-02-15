from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity
from app.utils.response import success_response,error_response


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
                return error_response(
                    message="User not found",
                    status_code=404
                )
            
            #Admin override
            if user.role=="admin":
                return fn(*args,**kwargs)
            
            #role check
            if user.role not in allowed_roles:
                return error_response(
                    message="Access Denied",
                    status_code=404
                )
            
            return fn(*args,**kwargs)
        return wrapper
    return decorator