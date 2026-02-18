import re

def validate_name(name: str) -> bool:
    return bool(re.match(r'^[а-яА-Яa-zA-ZёЁ\s-]+$', name.strip()))

def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^\+?\d{10,15}$', re.sub(r'\s', '', phone.strip())))
