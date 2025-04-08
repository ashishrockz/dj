import uuid
import random
import string
from django.utils.text import slugify

def generate_unique_slug(instance, field_name, new_slug=None):
    """
    Generate a unique slug for a model instance.
    If the generated slug is not unique, it adds a random string to make it unique.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, field_name))
    
    Model = instance.__class__
    qs = Model.objects.filter(slug=slug).exclude(id=instance.id)
    
    if qs.exists():
        random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        new_slug = f"{slug}-{random_string}"
        return generate_unique_slug(instance, field_name, new_slug=new_slug)
    
    return slug

def generate_order_number():
    """
    Generate a unique order number.
    Format: ORD-XXXXX where X is alphanumeric.
    """
    order_number = f"ORD-{uuid.uuid4().hex[:5].upper()}"
    return order_number

def generate_batch_number():
    """
    Generate a unique batch number.
    Format: B-XXXXXXXX where X is alphanumeric.
    """
    batch_number = f"B-{uuid.uuid4().hex[:8].upper()}"
    return batch_number

def calculate_order_totals(items, shipping_cost=0, tax_rate=0.07):
    """
    Calculate order subtotal, tax, and total.
    
    Args:
        items: List of dicts with 'quantity' and 'price' keys
        shipping_cost: Shipping cost amount
        tax_rate: Tax rate as a decimal (default 7%)
    
    Returns:
        Dict with 'subtotal', 'tax', and 'total' keys
    """
    subtotal = sum(item['quantity'] * item['price'] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax + shipping_cost
    
    return {
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }

def check_low_stock_items():
    """
    Check for low stock items and return a list of them.
    """
    from .models import InventoryItem
    return InventoryItem.objects.filter(quantity__lte=models.F('low_stock_threshold'))