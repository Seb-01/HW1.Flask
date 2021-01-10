import jsonschema
from flask import request

#import errors
import errors


def validate(source: str, req_schema: dict):
    """Валидатор входящих запросов"""

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(
                    # getattr(object, name, default)
                    # Параметры: object - объект, значение атрибута которого требуется получить
                    # name - имя атрибута объект, должно быть строкой
                    # default - значение по умолчанию, которое будет возвращено, если имя атрибута name отсутствует.
                    # Возвращаемое значение: значение именованного атрибута объекта
                    instance=getattr(request, source), schema=req_schema,
                )
            except jsonschema.ValidationError as e:
                #raise e.message
                raise errors.ValidationError

            result = func(*args, **kwargs)

            return result

        # Renaming the function name:
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
