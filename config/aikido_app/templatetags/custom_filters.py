from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_amount(payments):
    """
    Sum the 'amount' field from a list/queryset of payment objects
    Usage: {{ payments|sum_amount }}
    """
    if not payments:
        return Decimal('0.00')
    
    total = Decimal('0.00')
    for payment in payments:
        if hasattr(payment, 'amount') and payment.amount:
            total += Decimal(str(payment.amount))
    
    return total
