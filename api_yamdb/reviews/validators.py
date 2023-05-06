import re
from datetime import datetime

from django.core.exceptions import ValidationError


def year_validator(value):
    if value > datetime.now().year:
        raise ValidationError(
            ('Год не может быть больше текущего года.'),
            params={'value': value},
        )


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if value is None:
        raise AssertionError(
            ('Имя пользователя не может быть пустым.'),
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': value},
        )
    if len(value) > 150:
        raise AssertionError(
            ('Имя пользователя не может быть более 150 символов.'),
        )
