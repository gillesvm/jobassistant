#!/usr/bin/env python3
"""
Migration script to normalize date formats in DynamoDB.

This script will:
1. Scan all JOB items in the DynamoDB table
2. Normalize created_at, next_followup_at, and updated_at to ISO format with Brussels timezone
3. Update the items in place
"""
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from config import DYNAMODB_TABLE_NAME, AWS_REGION

BRUSSELS_TZ = ZoneInfo("Europe/Brussels")


def parse_date_flexible(date_str):
    """
    Parse a date string in various formats and return a timezone-aware datetime.
    Returns None if parsing fails.
    """
    if not date_str:
        return None

    # Try DD-MM-YYYYTHH:MM:SS+ZZZZ or DD-MM-YYYYTHH:MM:SSZ format (e.g., "30-03-2026T00:00:00+0200" or "27-03-2026T12:53:50Z")
    # This is a common format in our data that needs special handling
    try:
        if 'T' in date_str and len(date_str.split('-')) >= 3:
            # Check if it starts with DD-MM-YYYY pattern (2 digits, dash, 2 digits, dash)
            parts = date_str.split('T')[0].split('-')
            if len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4:
                # This is DD-MM-YYYY format with time
                # Parse the date part
                date_part = date_str.split('T')[0]
                time_part = date_str.split('T')[1] if 'T' in date_str else '00:00:00+02:00'

                # Parse date
                dt = datetime.strptime(date_part, '%d-%m-%Y')

                # Parse time and timezone
                if time_part.endswith('Z'):
                    # UTC timezone indicated by Z
                    time_str = time_part[:-1]
                    if ':' in time_str:
                        time_parts = time_str.split(':')
                        dt = dt.replace(hour=int(time_parts[0]), minute=int(time_parts[1]),
                                       second=int(time_parts[2]) if len(time_parts) > 2 else 0)
                    # Add UTC timezone and convert to Brussels
                    from datetime import timezone
                    dt = dt.replace(tzinfo=timezone.utc)
                    dt = dt.astimezone(BRUSSELS_TZ)
                    return dt
                elif '+' in time_part:
                    time_str, tz_str = time_part.split('+')
                    # Parse timezone offset
                    tz_hours = int(tz_str[:2])
                    tz_mins = int(tz_str[2:]) if len(tz_str) > 2 else 0
                    # Combine date and time
                    if ':' in time_str:
                        time_parts = time_str.split(':')
                        dt = dt.replace(hour=int(time_parts[0]), minute=int(time_parts[1]),
                                       second=int(time_parts[2]) if len(time_parts) > 2 else 0)
                    # Add Brussels timezone
                    dt = dt.replace(tzinfo=BRUSSELS_TZ)
                    return dt
    except Exception:
        pass

    # Try ISO format first (with or without timezone)
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # If it's naive (no timezone), add Brussels timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=BRUSSELS_TZ)
        else:
            # Convert to Brussels timezone
            dt = dt.astimezone(BRUSSELS_TZ)
        return dt
    except Exception:
        pass

    # Try YYYY-MM-DD format
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        dt = dt.replace(tzinfo=BRUSSELS_TZ)
        return dt
    except Exception:
        pass

    # Try DD-MM-YYYY format
    try:
        dt = datetime.strptime(date_str, '%d-%m-%Y')
        dt = dt.replace(tzinfo=BRUSSELS_TZ)
        return dt
    except Exception:
        pass

    print(f"WARNING: Could not parse date: {date_str}")
    return None


def migrate_dates():
    """Migrate all date fields in JOB items to ISO format with Brussels timezone."""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Get all JOB items
    response = table.scan(
        FilterExpression='item_type = :type',
        ExpressionAttributeValues={':type': 'JOB'}
    )

    jobs = response['Items']
    print(f"Found {len(jobs)} job items to process")

    updated_count = 0
    skipped_count = 0

    for job in jobs:
        job_id = job.get('job_id')
        company = job.get('company', 'Unknown')
        title = job.get('title', 'Unknown')

        print(f"\nProcessing: {company} - {title}")
        print(f"  Job ID: {job_id}")

        updates_needed = False
        update_expression_parts = []
        expression_attribute_values = {}

        # Process created_at
        if job.get('created_at'):
            created_dt = parse_date_flexible(job['created_at'])
            if created_dt:
                created_iso = created_dt.isoformat()
                if created_iso != job['created_at']:
                    print(f"  created_at: {job['created_at']} -> {created_iso}")
                    update_expression_parts.append('created_at = :created')
                    expression_attribute_values[':created'] = created_iso
                    updates_needed = True
                else:
                    print(f"  created_at: already in correct format")
            else:
                print(f"  created_at: SKIPPED (could not parse)")

        # Process next_followup_at
        if job.get('next_followup_at'):
            followup_dt = parse_date_flexible(job['next_followup_at'])
            if followup_dt:
                followup_iso = followup_dt.isoformat()
                if followup_iso != job['next_followup_at']:
                    print(f"  next_followup_at: {job['next_followup_at']} -> {followup_iso}")
                    update_expression_parts.append('next_followup_at = :followup')
                    expression_attribute_values[':followup'] = followup_iso
                    updates_needed = True
                else:
                    print(f"  next_followup_at: already in correct format")
            else:
                print(f"  next_followup_at: SKIPPED (could not parse)")

        # Process updated_at
        if job.get('updated_at'):
            updated_dt = parse_date_flexible(job['updated_at'])
            if updated_dt:
                updated_iso = updated_dt.isoformat()
                if updated_iso != job['updated_at']:
                    print(f"  updated_at: {job['updated_at']} -> {updated_iso}")
                    update_expression_parts.append('updated_at = :updated')
                    expression_attribute_values[':updated'] = updated_iso
                    updates_needed = True
                else:
                    print(f"  updated_at: already in correct format")
            else:
                print(f"  updated_at: SKIPPED (could not parse)")

        # Update the item if needed
        if updates_needed:
            update_expression = 'SET ' + ', '.join(update_expression_parts)
            try:
                table.update_item(
                    Key={'job_id': job_id, 'item_type': 'JOB'},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values
                )
                print(f"  ✓ Updated successfully")
                updated_count += 1
            except Exception as e:
                print(f"  ✗ Failed to update: {e}")
                skipped_count += 1
        else:
            print(f"  ✓ No updates needed")
            skipped_count += 1

    print(f"\n{'='*60}")
    print(f"Migration complete!")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total:   {len(jobs)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    print("="*60)
    print("Date Format Migration Script")
    print("="*60)
    print(f"Table: {DYNAMODB_TABLE_NAME}")
    print(f"Region: {AWS_REGION}")
    print(f"Target timezone: {BRUSSELS_TZ}")
    print("="*60)

    response = input("\nThis will update date formats in the database. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate_dates()
    else:
        print("Migration cancelled.")
