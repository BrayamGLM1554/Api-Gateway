from marshmallow import Schema, fields, validate, ValidationError

class ProveedorSchema(Schema):
    proveedorId = fields.Integer()
    nombre = fields.Str(required=True, validate=validate.Length(max=100))
    tipo = fields.Str(validate=validate.Length(max=50))
    direccion = fields.Str(validate=validate.Length(max=200))
    telefono = fields.Str(validate=validate.Length(max=20))
    email = fields.Email(validate=validate.Length(max=100))
    fechaAlta = fields.DateTime(allow_none=True)
    fechaBaja = fields.DateTime(allow_none=True)
    estatus = fields.Str(validate=validate.Length(max=50))

class ActivoFijoSchema(Schema):
    activofijoId = fields.Integer()
    nombre = fields.Str(required=True, validate=validate.Length(max=100))
    descripcion = fields.Str(validate=validate.Length(max=200))
    serial = fields.Str(validate=validate.Length(max=100))
    fechaCompra = fields.Date(allow_none=True)
    proveedorID = fields.Int(allow_none=True)
    sucursalID = fields.Int(allow_none=True)
    fechaAlta = fields.Date(allow_none=True)
    fechaBaja = fields.Date(allow_none=True)
    estatus = fields.Str(validate=validate.Length(max=50))

class SucursalSchema(Schema):
    sucursalId = fields.Integer()
    pais = fields.Str(validate=validate.Length(max=100))
    nombre = fields.Str(required=True, validate=validate.Length(max=100))
    longitud = fields.Decimal(as_string=True, allow_none=True)
    latitud = fields.Decimal(as_string=True, allow_none=True)
    fechaBaja = fields.DateTime(allow_none=True)
    fechaAlta = fields.DateTime(allow_none=True)
    estatus = fields.Str(validate=validate.Length(max=50))
    estado = fields.Str(validate=validate.Length(max=100))
    direccion = fields.Str(validate=validate.Length(max=200))
    codigoPostal = fields.Str(validate=validate.Length(max=20))
    ciudad = fields.Str(validate=validate.Length(max=100))

# Mecanismo RASP (activo): recibe los eventos sospechosos de IAST y decide si bloquear

def verificar_rasp(eventos):
    if eventos:
        raise ValidationError("Se detectaron patrones maliciosos en el cuerpo de la petición.")
