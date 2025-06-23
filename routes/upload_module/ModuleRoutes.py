from flask import Blueprint, request, jsonify
import requests 
from services.ExternalApiService import ModuleRoutes
from models.ClassModuleMap import isValidClass
from utils.Decorators import Decorator

moduleBp = Blueprint('modules', __name__)
apiService = ModuleRoutes()

@moduleBp.route('/modules/<class_name>', methods=['GET'])
@Decorator.tokenRequired
def getMoudels(class_name):
    if not isValidClass(class_name):
        return jsonify({"error": f"kelas '{class_name}' tidak ditemukan"}),

    result = apiService.getModuleByClass(class_name)
    return jsonify(result), 200


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