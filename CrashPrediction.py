import json
import boto3
import base64
import uuid
from datetime import datetime
import os

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'mi-bucket-imagenes')

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)
    print('response_show_custom_labels', response)
    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)

    return response['CustomLabels']

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

        model='arn:aws:rekognition:us-east-1:992382769661:project/car-classifierv2/version/car-classifierv2.2025-08-11T11.29.01/1754929741944'
        min_confidence=90

        custom_labels = show_custom_labels(model,BUCKET_NAME,filename, min_confidence)
        print("Custom labels detected: " + str(len(custom_labels)))
        
        # Preparar respuesta con las etiquetas detectadas
        if custom_labels:
            # Si se detectaron etiquetas, devolver la primera
            first_label = custom_labels[0]
            return response(200, {
                'name': first_label['Name'],
                'confidence': str(first_label['Confidence']),
                'labels_count': len(custom_labels)
            })
        else:
            # Si no se detectaron etiquetas
            return response(200, {
                'name': 'No labels detected',
                'confidence': '0',
                'labels_count': 0
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