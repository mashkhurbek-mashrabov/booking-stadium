import os
import re
import string
from typing import Union
from uuid import uuid4

from django.core.exceptions import ValidationError


def max_media_file_size_validator(value):
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValueError("Max file size is 10MB")


def price_formatter(price: Union[int, float]) -> str:
    """
    Formats a price value into a human-readable string with proper commas and decimal point handling.

    Args:
        price (Union[int, float]): The price value to be formatted.

    Returns:
        str: The formatted price string.
    """

    try:
        formatted_price = f"{price:,.2f}"
    except TypeError:
        return str(price)

    # Trim trailing '.00' and replace commas with spaces
    if formatted_price.split('.')[1] == '00':
        return formatted_price.split('.')[0]
    return formatted_price


def delete_file(instance: object, file_field: str) -> bool:
    """
        Delete the file from filesystem
        when the corresponding `Category` object is deleted
    """
    try:
        file = getattr(instance, file_field)
        if file:
            if os.path.isfile(file.path):
                os.remove(file.path)
        return True
    except Exception as e:
        return False


def generate_custom_uuid(letters_count=2, digits_count=6):
    """
    Generate a custom unique ID:
    """
    uuid = uuid4()
    letters = ''.join([char.upper() for char in str(uuid) if char in string.ascii_letters][:letters_count])
    digits = ''.join([char for char in str(uuid) if char.isdigit()][:digits_count])
    return f"{letters}{digits}"


def is_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)


def is_phone_number(phone_number):
    return re.fullmatch(r'\+998\d{9}$', phone_number)


def is_email_or_phone_number(text):
    if is_email(text):
        return 'email'
    elif is_phone_number(text):
        return 'phone_number'
    raise ValidationError({'email_phone_number': f'Invalid phone number or email: {text}'})

def send_confirmation_email(email, code):
    print(f"Code has been sent to {email}\nCode: {code}")


def send_sms(phone_number, code):
    print(f"Code has been sent to {phone_number}\nCode: {code}")
