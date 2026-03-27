import boto3
import uuid
from datetime import datetime, timezone
from config import DYNAMODB_TABLE_NAME, S3_BUCKET_NAME, AWS_REGION


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%d-%m-%YT%H:%M:%SZ")


def add_job(job_data):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.put_item(Item=job_data)
    return response


def get_job(job_id):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={'job_id': job_id})
    return response['Item']


def get_all_jobs():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.scan()
    return response['Items']


def delete_job(job_id):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.delete_item(Key={'job_id': job_id})
    return response
