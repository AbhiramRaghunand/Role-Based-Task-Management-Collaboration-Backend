from flask import Blueprint,jsonify,request_started
from app.utils.rbac import role_required

admin_bp=Blueprint('admin',__name__)

@admin_bp.route('/userslist',methods=['GET'])
@role_required('ADMIN')
def get_user_list():
    return jsonify({"message":"List of users"}),200

