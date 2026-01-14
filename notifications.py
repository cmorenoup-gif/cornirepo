import logging
import os
from google.cloud import logging as cloud_logging

# Configuración de Cornilove Notifications
def send_critical_alert(message, report_name="N/A"):
    """
    Envía una alerta crítica que el Cloud Monitoring de Google 
    capturará para enviarte un correo electrónico.
    """
    # 1. Configurar el logger de Google Cloud
    log_client = cloud_logging.Client()
    logger = log_client.logger("cornilove-alerts")

    alert_payload = {
        "event": "SYNC_FAILURE",
        "company": "CORNILOVE DB LLC",
        "report": report_name,
        "message": message,
        "severity": "CRITICAL"
    }

    # 2. Escribir el log de error
    logger.log_struct(alert_payload, severity="ERROR")
    
    # 3. También lo imprimimos en la consola local de Cloud Run
    logging.error(f"🚨 ALERTA CORNILOVE: {message} en reporte {report_name}")
