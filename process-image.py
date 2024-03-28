import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error
import random
import string
from io import BytesIO
from cgi import parse_header, parse_multipart, FieldStorage
import json
from base64 import b64decode

print('Loading function')

rekognition = boto3.client('rekognition')
comprehend = boto3.client('comprehend')
s3 = boto3.resource("s3")

def detect_text(bucket, photo):

    response = rekognition.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    textDetections = response['TextDetections']
    detectedTexts = []
    for text in textDetections:
        languageCode = comprehend.detect_dominant_language(Text= text['DetectedText'])['Languages'][0]['LanguageCode']
        print(languageCode)
        try:
            sentiment = comprehend.detect_sentiment(Text= text['DetectedText'], LanguageCode=languageCode)
            sentiment['LanguageCode'] = languageCode
            sentiment['DetectedText'] = text['DetectedText']
            detectedTexts.append(sentiment)
        except Exception as e:
            print(e)
        
    return detectedTexts

def lambda_handler(event, context):
    
    wavBody = b64decode(event['body-json'])
    wavs = wavBody.split(b'\r\n')  
    bucket = "upload-image-for-recognition"
    image_upload_bucket = s3.Bucket(bucket)

    key = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + ".png"
    s3_upload = image_upload_bucket.put_object(
        Body = b"\r\n".join(wavs[4:]),
        Key = key
    )

    try:
        response = detect_text(bucket, key)

        print(response)

        return response
    except Exception as e:
        print(e)
        
        raise e
