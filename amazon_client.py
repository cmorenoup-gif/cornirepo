import os
import time
from sp_api.api import Reports
from sp_api.base import Marketplaces

class AmazonClient:
    def __init__(self):
        self.creds = {
            "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
            "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
            "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
            "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
            "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
            "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
        }

    def get_report(self, report_type):
        """Proceso de 3 pasos: Solicitar, Esperar y Obtener Documento"""
        client = Reports(credentials=self.creds, marketplace=Marketplaces.US)
        
        # 1. Crear el reporte
        res = client.create_report(reportType=report_type)
        report_id = res.payload.get("reportId")

        # 2. Esperar a que Amazon lo procese (Polling)
        status = "IN_QUEUE"
        while status not in ["COMPLETED", "FATAL", "CANCELLED"]:
            time.sleep(10) # Espera 10 segundos para no saturar la API
            res = client.get_report(report_id)
            status = res.payload.get("processingStatus")

        if status == "COMPLETED":
            doc_id = res.payload.get("reportDocumentId")
            # 3. Descargar el contenido
            return client.get_report_document(doc_id).payload.get("url")
        return None
