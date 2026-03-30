import boto3
import uuid
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from config import DYNAMODB_TABLE_NAME, S3_BUCKET_NAME, AWS_REGION

BRUSSELS_TZ = ZoneInfo("Europe/Brussels")


def now_iso() -> str:
    return datetime.now(BRUSSELS_TZ).strftime("%d-%m-%Y")


def days_from_now(days: int) -> str:
    future_date = datetime.now(BRUSSELS_TZ) + timedelta(days=days)
    return future_date.strftime("%d-%m-%Y")


def add_job(company, title, job_url, status):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    job_id = str(uuid.uuid4())
    created_at = now_iso()
    next_followup_at = days_from_now(7)

    # Main job item
    job_item = {
        'job_id': job_id,
        'item_type': 'JOB',
        'company': company,
        'title': title,
        'job_url': job_url,
        'status': status,
        'created_at': created_at,
        'updated_at': created_at,
        'next_followup_at': next_followup_at
    }

    table.put_item(Item=job_item)
    return job_id


def get_job(job_id):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.query(
        KeyConditionExpression='job_id = :job_id',
        ExpressionAttributeValues={':job_id': job_id}
    )
    return response['Items']


def get_all_jobs():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.scan(
        FilterExpression='item_type = :type',
        ExpressionAttributeValues={':type': 'JOB'}
    )
    return response['Items']


def update_job(job_id, company, title, job_url, status, created_at="", next_followup_at="", job_description="",
               resume_used="", cover_letter="", feedback=""):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    updated_at = now_iso()

    # Convert date strings (YYYY-MM-DD) to ISO datetime format
    if created_at:
        created_at_iso = datetime.strptime(created_at, '%Y-%m-%d').replace(tzinfo=BRUSSELS_TZ).strftime(
            "%d-%m-%YT%H:%M:%S%z")
    else:
        created_at_iso = now_iso()

    if next_followup_at:
        next_followup_iso = datetime.strptime(next_followup_at, '%Y-%m-%d').replace(tzinfo=BRUSSELS_TZ).strftime(
            "%d-%m-%YT%H:%M:%S%z")
    else:
        next_followup_iso = days_from_now(7)

    # Update main JOB item
    table.update_item(
        Key={'job_id': job_id, 'item_type': 'JOB'},
        UpdateExpression='SET company = :company, title = :title, job_url = :url, #st = :status, created_at = :created, next_followup_at = :followup, updated_at = :updated',
        ExpressionAttributeNames={'#st': 'status'},
        ExpressionAttributeValues={
            ':company': company,
            ':title': title,
            ':url': job_url,
            ':status': status,
            ':created': created_at_iso,
            ':followup': next_followup_iso,
            ':updated': updated_at
        }
    )

    # Update or create DESCRIPTION item
    if job_description.strip():
        table.put_item(Item={
            'job_id': job_id,
            'item_type': 'DESCRIPTION',
            'content': job_description,
            'updated_at': updated_at
        })

    # Update or create RESUME item
    if resume_used.strip():
        table.put_item(Item={
            'job_id': job_id,
            'item_type': 'RESUME',
            'content': resume_used,
            'updated_at': updated_at
        })

    # Update or create COVER_LETTER item
    if cover_letter.strip():
        table.put_item(Item={
            'job_id': job_id,
            'item_type': 'COVER_LETTER',
            'content': cover_letter,
            'updated_at': updated_at
        })

    # Update or create FEEDBACK item
    if feedback.strip():
        table.put_item(Item={
            'job_id': job_id,
            'item_type': 'FEEDBACK',
            'content': feedback,
            'updated_at': updated_at
        })


def delete_job(job_id):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Get all items for this job_id
    items = get_job(job_id)

    # Delete each item
    for item in items:
        table.delete_item(Key={
            'job_id': job_id,
            'item_type': item['item_type']
        })

    return len(items)
