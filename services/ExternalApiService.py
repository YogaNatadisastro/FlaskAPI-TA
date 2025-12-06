import requests
from models import db
from flask import current_app, jsonify
from config.config import Config
from models.modules.Modules import Modules
from models.classroom.classroom import Classroom

class ExternalService:
    def __init__(self):
        self.module_base_url = Config.MODULE_BASE_URL
        self.get_module_url = Config.GLOBAL_MODULE_URL

    def getModuleByClassroomId(self, classroom_id):
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return None, {"error": "Kelas tidak ditemukan"}, 404
        
        mappings = Modules.query.filter_by(classroom_id=classroom_id).all()
        if not mappings:
            return {
                "classroom_id": classroom_id,
                "modules": []
            }, None, 200
        
        modules_data = []
        for m in mappings:
            modules_data.append({
                "id": m.id,
                "resource_name": m.resource_name,
                "module_name": m.module_name,
                "classroom_id": m.classroom_id,
                "uploaded_at": m.created_at.isoformat() if m.created_at else None
            })
        
        return {
            "classroom_id": classroom_id,
            "modules": modules_data
        }, None, 200
    
    def getAllModules(self):
        url = f"{self.module_base_url}/list-resources"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def getFilteredModules(self, classroom, resource_ids):
        try: 
            response = requests.get(f"{self.get_module_url}/list-resources")
            response.raise_for_status()
            all_resources = response.json().get('resources', [])

            # Filter resoureces sesuai dengan Id yang terdaftar di kelas
            filtered_resources = [res for res in all_resources if res['id'] in resource_ids]

            return {
                'classroom_id': classroom.id,
                'class_name': classroom.class_name,
                'modules': filtered_resources
            }
        except requests.exceptions.RequestException as e:
            raise Exception({
                "error": "Gagal mengambil data modul",
                "details": str(e)
            })

    def uploadModule(self, current_user, data, files):
        try:
            url = f"{self.module_base_url}/upload_resource"
            module_name = data.get('module_name')
            resource_name = data.get('resource_name')
            classroom_id = data.get('classroom_id')
            file = files.get('file')

            if not module_name:
                raise ValueError("module_name is required")

            if not resource_name or not file:
                raise ValueError("resource_name is required")
            
            if not classroom_id:
                raise ValueError("classroom_id is required")
            
            if not file:
                raise ValueError("File is required")
            
            payload = {'resource_name': resource_name}
            file_data = {'file': (file.filename, file.stream, file.content_type)}

            response = requests.post(url, data=payload, files=file_data)
            response.raise_for_status()
            ms_result = response.json()

            job_id = ms_result.get('job_id')
            if not job_id:
                raise ValueError("upload did not return job_id")
            
            new_module = Modules(
                module_name=module_name,
                resource_name=resource_name,
                job_id=job_id,
                classroom_id=classroom_id,
                uploaded_by=current_user.id
            )

            db.session.add(new_module)
            db.session.commit()

            return {
                "message": "Module uploaded successfully",
                "module_id": new_module.id,
                "job_id": job_id,
                "resource_name": resource_name
            }
        except Exception as e:
            db.session.rollback()
            raise e
    
    def downloadModule(self, resource_name):
        try:
            url = f"{self.get_module_url}/download_resource/resource/{resource_name}"
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception({
                "error": "Gagal mengunduh resource",
                "details": str(e)
            })
    