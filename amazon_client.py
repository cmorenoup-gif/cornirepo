import os
import time
import logging
from sp_api.api import Orders, Reports
from sp_api.base import Marketplaces, SellingApiException

class AmazonClient:
    def __init__(self):
        # Toma las credenciales inyectadas por Secret Manager
        self.creds = {
            "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
            "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
            "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
            "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
            "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
            "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
        }

    def fetch_orders(self, created_after="2026-01-01T00:00:00Z"):
        """Descarga órdenes para el histórico de ventas"""
        try:
            client = Orders(credentials=self.creds, marketplace=Marketplaces.US)
            response = client.get_orders(CreatedAfter=created_after)
            return response.payload.get("Orders", [])
        except SellingApiException as e:
            logging.error(f"Error al obtener órdenes: {str(e)}")
            raise e

    def get_report(self, report_type):
        """
        Proceso de 3 pasos para reportes pesados (Inventory Ledger, FBA, etc.)
        1. Solicitar -> 2. Esperar (Polling) -> 3. Obtener URL de descarga
        """
        try:
            client = Reports(credentials=self.creds, marketplace=Marketplaces.US)
            
            # 1. Crear la solicitud del reporte
            logging.info(f"[AMAZON] Solicitando reporte tipo: {report_type}")
            res_create = client.create_report(reportType=report_type)
            report_id = res_create.payload.get("reportId")

            # 2. Bucle de espera (Polling)
            status = "IN_QUEUE"
            while status not in ["COMPLETED", "FATAL", "CANCELLED"]:
                logging.info(f"[AMAZON] Reporte {report_id} en estado: {status}. Esperando 20s...")
                time.sleep(20)  # Espera estratégica para no saturar la API
                res_status = client.get_report(report_id)
                status = res_status.payload.get("processingStatus")

            # 3. Obtener la URL del documento final
            if status == "COMPLETED":
                doc_id = res_status.payload.get("reportDocumentId")
                res_doc = client.get_report_document(doc_id)
                logging.info(f"[SUCCESS] Reporte {report_type} listo para descarga.")
                return res_doc.payload.get("url")
            
            logging.error(f"[ERROR] El reporte terminó con estado: {status}")
            return None

        except SellingApiException as e:
            logging.error(f"Error en SP-API Reports: {str(e)}")
            return None
