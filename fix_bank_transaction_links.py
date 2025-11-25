"""
Script to find and clean up bank transaction links to deleted instructor payments
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import BankTransaction, MonthlyInstructorPayment, MonthlyFederationPayment
from decimal import Decimal

# Find transactions with 425000 amount or matching description
target_amount = Decimal('425000.00')
search_description = "amgaa bagsh"

print("Searching for bank transactions...")
print("=" * 80)

# Search by description first
transactions = BankTransaction.objects.filter(
    description__icontains=search_description
)

# If not found, search by amount
if not transactions.exists():
    print(f"No transactions found with description '{search_description}'")
    print(f"Searching by amount {target_amount}...")
    
    transactions = BankTransaction.objects.filter(
        credit_amount=target_amount
    ) | BankTransaction.objects.filter(
        debit_amount=target_amount
    ) | BankTransaction.objects.filter(
        debit_amount=-target_amount
    )

if not transactions.exists():
    print(f"No bank transactions found with amount {target_amount}")
else:
    for txn in transactions:
        print(f"\nBank Transaction ID: {txn.id}")
        print(f"Date: {txn.transaction_date}")
        print(f"Credit: {txn.credit_amount}")
        print(f"Debit: {txn.debit_amount}")
        print(f"Description: {txn.description}")
        print(f"Status: {txn.status}")
        
        # Check instructor payments linked to this transaction
        instructor_payments = MonthlyInstructorPayment.objects.filter(bank_transaction=txn)
        print(f"\nLinked Instructor Payments: {instructor_payments.count()}")
        for payment in instructor_payments:
            print(f"  - Payment ID {payment.id}: {payment.instructor} / {payment.class_type} / {payment.month} / {payment.instructor_share_amount}")
        
        # Check federation payments linked to this transaction
        federation_payments = MonthlyFederationPayment.objects.filter(bank_transaction=txn)
        print(f"\nLinked Federation Payments: {federation_payments.count()}")
        for payment in federation_payments:
            print(f"  - Payment ID {payment.id}: {payment.class_type} / {payment.month} / {payment.federation_share_amount}")
        
        # Ask to clean up
        print("\n" + "=" * 80)
        response = input(f"Clear bank_transaction link from this transaction (ID {txn.id})? [y/N]: ")
        
        if response.lower() == 'y':
            # Clear instructor payment links
            cleared_instructor = instructor_payments.update(bank_transaction=None)
            print(f"  ✓ Cleared {cleared_instructor} instructor payment links")
            
            # Clear federation payment links
            cleared_federation = federation_payments.update(bank_transaction=None)
            print(f"  ✓ Cleared {cleared_federation} federation payment links")
            
            # Update transaction status
            txn.update_status()
            print(f"  ✓ Updated transaction status to: {txn.status}")
        else:
            print("  Skipped")

print("\n" + "=" * 80)
print("Done!")
