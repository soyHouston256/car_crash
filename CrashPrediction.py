import json
import boto3
import base64
import uuid
from datetime import datetime
import os

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'mi-bucket-imagenes')

def lambda_handler(event, context):
    try:
        if event.get('httpMethod') != 'POST':
            return response(405, {'error': 'Método no permitido'})
        
        # Extraer imagen
        body = json.loads(event['body'])
        image_data = base64.b64decode(body['image'])
        
        # Generar nombre único
        filename = f"images/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}.jpg"
        
        # Subir a S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=image_data,
            ContentType='image/jpeg'
        )
        
        return response(200, {
            'message': 'Imagen subida exitosamente',
            'url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        })
        
    except Exception as e:
        return response(500, {'error': str(e)})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }