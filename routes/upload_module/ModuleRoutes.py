from flask import Blueprint, request, jsonify
from models import db 
import requests 
from services.ExternalApiService import ModuleRoutes
from models.classroom.classroom import Classroom
from models.modules.Modules import Modules
from models.ClassModuleMap import isValidClass
from utils.Decorators import Decorator

moduleBp = Blueprint('modules', __name__)
apiService = ModuleRoutes()

@moduleBp.route('/upload', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(roleIdRequired=2)  # Assuming roleId 2 is for 'Guru'
def uploadModule(current_user):
    data = request.form
    files = request.files
    try: 
        result = apiService.uploadModule(data, files)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to upload module", "details": str(e)}), 500
    

@moduleBp.route('/<int:classroom_id>/add_module', methods=['POST'])
@Decorator.tokenRequired
@Decorator.rolesRequired(roleIdRequired=1)
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


@moduleBp.route('/<int:classroom_id>/modules', methods=['GET'])
@Decorator.tokenRequired
def getModulesByClassroom(current_user, classroom_id):
    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return jsonify({"error": "Kelas tidak ditemukan"}), 404
    
    mappings = Modules.query.filter_by(classroom_id=classroom_id).all()
    resourceIds = [m.resource_id for m in mappings]

    try:
        result = apiService.getFilteredModules(classroom, resourceIds)
        return jsonify(result), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Gagal mengambil modul", "details": str(e)}), 500
  
    
@moduleBp.route('list-modules', methods=['GET'])
@Decorator.tokenRequired
def getAllModules(current_user):
    try:
        result = apiService.getAllModules()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil modul", "details": str(e)}), 500