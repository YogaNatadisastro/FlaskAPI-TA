import requests
from config.config import Config

class ModuleRoutes:
    def __init__(self):
        self.module_base_url = Config.MODULE_BASE_URL
        self.get_module_url = Config.GLOBAL_MODULE_URL

    def getModuleByClassroomId(self, classroom_id):
        url = f"{self.module_base_url}/modules/class/{classroom_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def getAllModules(self):
        url = f"{self.get_module_url}/list-resources"
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

    def uploadModule(self, data, files):
        url = f"{self.module_base_url}/upload_resource"
        resource_name = data.get('resource_name')
        file = files.get('file')

        if not resource_name or not file:
            raise ValueError("resource_name is required")
        
        payload = {'resource_name': resource_name}
        file_data = {'file': (file.filename, file.stream, file.content_type)}

        response = requests.post(url, data=payload, files=file_data, verify=False)
        response.raise_for_status()

        return response.json()
    