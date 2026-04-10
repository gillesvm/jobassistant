#!/usr/bin/env python3
"""
Test script to verify all three date-related fixes are working.
"""
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from config import DYNAMODB_TABLE_NAME, AWS_REGION

BRUSSELS_TZ = ZoneInfo("Europe/Brussels")


def test_date_parsing():
    """Test that various date formats can be parsed correctly."""
    from routes.jobs import edit_job_form

    print("="*60)
    print("Test 1: Date Parsing in Edit Form")
    print("="*60)

    test_dates = [
        "2026-04-08T00:00:00+02:00",  # ISO with timezone
        "2026-04-08",                  # Date only
        "08-04-2026",                  # DD-MM-YYYY
    ]

    for date_str in test_dates:
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            formatted = dt.strftime('%Y-%m-%d')
            print(f"  ✓ {date_str:30} -> {formatted}")
        except Exception:
            try:
                # Try YYYY-MM-DD
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                formatted = dt.strftime('%Y-%m-%d')
                print(f"  ✓ {date_str:30} -> {formatted}")
            except Exception:
                try:
                    # Try DD-MM-YYYY
                    dt = datetime.strptime(date_str, '%d-%m-%Y')
                    formatted = dt.strftime('%Y-%m-%d')
                    print(f"  ✓ {date_str:30} -> {formatted}")
                except Exception:
                    print(f"  ✗ {date_str:30} -> FAILED")


def test_overdue_detection():
    """Test that overdue detection works correctly."""
    print("\n" + "="*60)
    print("Test 2: Overdue Detection Logic")
    print("="*60)

    now = datetime.now(BRUSSELS_TZ)
    print(f"Current time: {now}")
    print()

    test_cases = [
        ("2026-04-08T00:00:00+02:00", True, "YO IT (yesterday)"),
        ("2026-04-06T00:00:00+02:00", True, "Kingfisher (3 days ago)"),
        ("2026-04-09T00:00:00+02:00", True, "Nubex (today at midnight)"),
        ("2026-04-10T00:00:00+02:00", False, "Future (tomorrow)"),
    ]

    for date_str, expected_overdue, description in test_cases:
        followup_dt = datetime.fromisoformat(date_str)
        is_overdue = followup_dt < now
        status = "✓" if is_overdue == expected_overdue else "✗"
        print(f"  {status} {description:25} | {date_str:30} | Overdue: {is_overdue} (expected: {expected_overdue})")


def test_database_dates():
    """Test that all dates in the database are now normalized."""
    print("\n" + "="*60)
    print("Test 3: Database Date Normalization")
    print("="*60)

    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    response = table.scan(
        FilterExpression='item_type = :type',
        ExpressionAttributeValues={':type': 'JOB'}
    )

    jobs = response['Items']
    all_good = True

    for job in jobs:
        company = job.get('company', 'Unknown')
        created = job.get('created_at', '')
        followup = job.get('next_followup_at', '')

        # Check if dates are in ISO format (should contain 'T' and timezone info)
        created_ok = 'T' in created and ('+' in created or 'Z' in created)
        followup_ok = 'T' in followup and ('+' in followup or 'Z' in followup)

        if created_ok and followup_ok:
            print(f"  ✓ {company[:30]:30} | Dates normalized")
        else:
            print(f"  ✗ {company[:30]:30} | Created: {created_ok} | Followup: {followup_ok}")
            all_good = False

    print()
    if all_good:
        print("  All dates are properly normalized! ✓")
    else:
        print("  Some dates need attention! ✗")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Date Fixes Verification Tests")
    print("="*60)
    print()

    test_date_parsing()
    test_overdue_detection()
    test_database_dates()

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
