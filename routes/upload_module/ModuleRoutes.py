from flask import Blueprint, request, jsonify, Response
from models import db 
import requests 
from services.ExternalApiService import ExternalService
from models.classroom.classroom import Classroom
from models.modules.Modules import Modules
from models.ClassModuleMap import isValidClass
from utils.Decorators import Decorator

moduleBp = Blueprint('modules', __name__)
apiService = ExternalService()

@moduleBp.route('/upload', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)# Assuming roleId 1 is for 'Guru'
def uploadModule(current_user):
    try:
       result = apiService.uploadModule(
           current_user=current_user,
           data=request.form,
           files=request.files
       )
       return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        return jsonify({
            "error": "Gagal mengupload module",
            "details": str(e)
        }), 500
    

@moduleBp.route('/<int:classroom_id>/add_module', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(1)
def addModuleToClassroom(current_user, classroom_id):
    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return jsonify({"error": "Kelas tidak ditemukan"}), 404
    
    data = request.get_json()
    resource_id = data.get('resource_id')

    if not resource_id:
        return jsonify({"error": "resource_id is required"}), 400
    
    #Cek duplikasi
    existing = Modules.query.filter_by(classroom_id=classroom_id, resource_id=resource_id).first()
    if existing:
        return jsonify({"message": "Module sudah di tambahkan ke kelas ini"}), 409
    
    newModule = Modules(classroom_id=classroom_id, resource_id=resource_id)
    db.session.add(newModule)
    db.session.commit()

    return jsonify({"message": "Module berhasil ditambahkan ke kelas"}), 201


@moduleBp.route('/<int:classroom_id>', methods=['GET'])
@Decorator.tokenRequired
def getModulesByClassroom(current_user, classroom_id):
    result, error, status = apiService.getModuleByClassroomId(classroom_id)
    if error:
        return jsonify(error), status
    else:
        return jsonify(result), status
  
    
@moduleBp.route('list-modules', methods=['GET'])
@Decorator.tokenRequired
def getAllModules(current_user):
    try:
        result = apiService.getAllModules()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil modul", "details": str(e)}), 500
    

@moduleBp.route('resource/download/<string:resource_name>', methods=['GET'])
@Decorator.tokenRequired
def downloadModules(current_user, resource_name=None):
    try:
        externalResponse = apiService.downloadModule(resource_name)
        content_type = externalResponse.headers.get('Content-Type', 'application/octet-stream')
        contentDisposition = externalResponse.headers.get(
            'Content-Disposition', f'inline; filename="{resource_name}.pdf"'
        )
        
        return Response(
            externalResponse.iter_content(chunk_size=8192),
            status=externalResponse.status_code,
            content_type=content_type,
            headers={
                "Content-Disposition": contentDisposition
            }
        )
    
    except Exception as e:
        return jsonify({
            "error": "Gagal mengunduh resource",
            "details": str(e)
        }), 500