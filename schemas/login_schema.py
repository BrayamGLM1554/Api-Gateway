from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    correo = fields.Email(required=True, error_messages={"required": "El correo es obligatorio."})
    pwd = fields.Str(required=True, validate=validate.Length(min=3), error_messages={"required": "La contraseña es obligatoria."})
