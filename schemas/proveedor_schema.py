from marshmallow import Schema, fields, validate

class ProveedorSchema(Schema):
    token = fields.Str(required=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2))
    tipo = fields.Str(required=True)
    direccion = fields.Str(required=True)
    telefono = fields.Str(required=True, validate=validate.Length(min=7))
    email = fields.Email(required=True)
