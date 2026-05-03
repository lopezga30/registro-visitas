import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ["TABLE_NAME"]
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")
SENDER_EMAIL       = os.environ.get("SENDER_EMAIL", "")
SITE_URL           = os.environ.get("SITE_URL", "")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
ses = boto3.client("ses", region_name="us-east-1")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")

    if method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    if path == "/visits" and method == "GET":
        return get_visits()

    if path == "/visits" and method == "POST":
        body = json.loads(event.get("body") or "{}")
        return post_visit(body)

    return response(404, {"error": "Not found"})


def get_visits():
    result = table.scan()
    return response(200, {"visits": result.get("Items", [])})


def post_visit(body):
    name = (body.get("name") or "").strip()[:100]
    message = (body.get("message") or "").strip()[:300]

    if not name or not message:
        return response(400, {"error": "name y message son requeridos"})

    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=item)

    # Enviar notificación por email (no bloqueante: si falla, igual devuelve 201)
    if NOTIFICATION_EMAIL:
        try:
            send_notification(name, message, item["timestamp"])
        except Exception as e:
            print(f"[WARN] No se pudo enviar notificación: {e}")

    return response(201, {"visit": item})


def send_notification(name, message, timestamp):
    # Formatear fecha legible
    dt = datetime.fromisoformat(timestamp)
    fecha = dt.strftime("%d/%m/%Y %H:%M UTC")

    subject = f"✉️ Nuevo mensaje de {name} — Registro de Visitas"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; color: #333;">
      <div style="background: linear-gradient(135deg, #7c3aed, #db2777); padding: 28px 32px; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 20px;">📋 Registro de Visitas</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 14px;">Nuevo mensaje recibido</p>
      </div>
      <div style="background: #f9f9f9; padding: 28px 32px; border: 1px solid #e5e5e5; border-top: none;">
        <p style="margin: 0 0 6px;"><strong>De:</strong> {name}</p>
        <p style="margin: 0 0 20px; font-size: 13px; color: #888;">{fecha}</p>
        <div style="background: white; border-left: 4px solid #7c3aed; padding: 16px 20px; border-radius: 0 8px 8px 0; font-size: 15px; line-height: 1.6; color: #444;">
          {message}
        </div>
      </div>
      <div style="background: #f0f0f0; padding: 16px 32px; border-radius: 0 0 12px 12px; text-align: center; border: 1px solid #e5e5e5; border-top: none;">
        <a href="{SITE_URL}" style="color: #7c3aed; text-decoration: none; font-size: 13px;">Ver todos los mensajes →</a>
      </div>
    </div>
    """

    text_body = f"Nuevo mensaje en Registro de Visitas\n\nDe: {name}\nFecha: {fecha}\n\nMensaje:\n{message}\n\nVer el sitio: {SITE_URL}"

    ses.send_email(
        Source=f"Registro de Visitas <{SENDER_EMAIL}>",
        Destination={"ToAddresses": [NOTIFICATION_EMAIL]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Html": {"Data": html_body, "Charset": "UTF-8"},
                "Text": {"Data": text_body, "Charset": "UTF-8"},
            },
        },
    )
    print(f"[INFO] Notificación enviada a {NOTIFICATION_EMAIL}")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
