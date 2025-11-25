#!/usr/bin/env python
"""Test weekday display after fix"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import ClassSession
from datetime import date

# Check session for 2025-09-01
sessions = ClassSession.objects.filter(date=date(2025, 9, 1))

print("Sessions on 2025-09-01:")
print("-" * 80)

for session in sessions:
    print(f"Class Type: {session.class_type.name}")
    print(f"Date: {session.date}")
    print(f"Weekday number: {session.weekday}")
    print(f"Weekday display: {session.get_weekday_display()}")
    print(f"Session __str__: {session}")
    print(f"Actual weekday (from date): {session.date.weekday()}")
    print("-" * 80)

if not sessions.exists():
    print("No sessions found for 2025-09-01")
    print("\nSearching for recent sessions...")
    recent = ClassSession.objects.all()[:5]
    for session in recent:
        print(f"{session} - actual weekday: {session.date.weekday()}")
