import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

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
    return response(201, {"visit": item})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
