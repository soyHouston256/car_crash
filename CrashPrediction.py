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
        # Debug logging
        print(f"Event received: {json.dumps(event, indent=2)}")
        print(f"HTTP Method: {event.get('method')}")
        print(f"Request Context: {event.get('requestContext', {})}")
        
        if event.get('method') != 'POST':
            return response(405, {'error': f'Método no permitido. Recibido: {event.get("method")}'})
        
        # Extraer imagen
        body = event['body']  # El body ya es un objeto, no necesita json.loads()
        image_data = base64.b64decode(body['image'])
        
        # Generar nombre único
        #filename = f"images/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}.jpg"
        filename = f"test/{uuid.uuid4()}.jpg"
        
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
        print(f"Error: {str(e)}")
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