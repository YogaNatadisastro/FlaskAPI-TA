# import os
# from models import db
# from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
# from models.modules.Modules import Modules
# from models.classroom.Classroom import Classroom
# from datetime import datetime
# from utils.Decorators import Decorator

# moduleBp = Blueprint('module', __name__)
# UPLOAD_FOLDER = 'uploads/modules'

# @moduleBp.route('/modules', methods=['POST'])
# @Decorator.tokenRequired
# @Decorator.rolesRequired(2)
# def uploadModule(current_user):
#     module_name = request.form.get('module_name')
#     classroom_id = request.form.get('classroom_id')
#     file = request.files.get('file_path')

#     if not file:
#         return jsonify({"error": "No file uploaded"}), 400
    
#     classroom = Classroom.query.filter_by(
#         id=classroom_id, user_id=current_user.id).first()
#     if not classroom:
#         return jsonify({"error": "Classroom not found"}), 404
    
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)

#     fileName = secure_filename(file.filename)
#     file_path = os.path.join(UPLOAD_FOLDER, fileName)
#     file.save(file_path)

#     module = Modules(
#         module_name=module_name,
#         file_path=file_path,
#         classroom_id=classroom_id
#     )
    
#     db.session.add(module)
#     db.session.commit()

#     userInfo ={
#         "id": current_user.id,
#         "username": current_user.username,
#         "email": current_user.email,
#         "role_id": current_user.role_id
#     }

#     return jsonify({
#         "message": "Module uploaded successfully",
#         "module": {
#             "id": module.id,
#             "module_name": module.module_name,
#             "file_path": module.file_path,
#             "classroom_id": module.classroom_id,
#             "uploaded_by": userInfo
#         } 
#     }), 201