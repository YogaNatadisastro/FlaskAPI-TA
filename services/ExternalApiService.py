import requests
from config.config import Config

class ModuleRoutes:
    def __init__(self):
        self.module_base_url = Config.MODULE_BASE_URL

    def getModuleByClass (self, class_name):
        url = f"{self.module_base_url}/modules/class/{class_name}"
        response = requests.get(url)
        return response.json()
    
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