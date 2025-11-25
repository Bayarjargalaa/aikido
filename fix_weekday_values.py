#!/usr/bin/env python
"""
Fix weekday values in ClassSession records to match Python's datetime.weekday() convention.
Old convention: Monday=1, Wednesday=3, Friday=5, Saturday=6, Sunday=0
New convention: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import ClassSession
from datetime import datetime

def fix_weekday_values():
    """Fix all ClassSession weekday values to match datetime.weekday()"""
    
    sessions = ClassSession.objects.all()
    total = sessions.count()
    fixed = 0
    already_correct = 0
    
    print(f"Total sessions to check: {total}")
    print("-" * 80)
    
    for session in sessions:
        # Calculate correct weekday from date
        correct_weekday = session.date.weekday()
        
        if session.weekday != correct_weekday:
            old_weekday = session.weekday
            old_display = session.get_weekday_display()
            
            session.weekday = correct_weekday
            session.save(update_fields=['weekday'])
            
            # Refresh to get new display
            session.refresh_from_db()
            new_display = session.get_weekday_display()
            
            print(f"Fixed: {session.date} - {session.class_type.name}")
            print(f"  Old: weekday={old_weekday} ({old_display})")
            print(f"  New: weekday={correct_weekday} ({new_display})")
            print()
            fixed += 1
        else:
            already_correct += 1
    
    print("-" * 80)
    print(f"Summary:")
    print(f"  Fixed: {fixed}")
    print(f"  Already correct: {already_correct}")
    print(f"  Total: {total}")

if __name__ == '__main__':
    fix_weekday_values()
