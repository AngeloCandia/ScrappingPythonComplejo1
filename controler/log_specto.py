""" Archivo log_specto.py.
    Este archivo, contiene todas las funciones relacionadas con el acceso y
    actualizacion a la base de datos dynamoDb
"""
from datetime import datetime

from boto3.dynamodb.conditions import Attr  # ,Key


def save_log(dynamodb, star_date, date, status):
    """Funcion save_log().

    Guarda un registro a la tabla 'log_specto', una vez finalizado la
    descarga de un dia completo en specto

    Parameters
    ----------
    dynamodb : dynamodb
        Variable base de datos Dynamodb de aws
    star_date : str
        fecha de ejecucion, con formato datetime
    date : str
        fecha del dia descargado
    status: estado de la descarga

    Returns
    -------
    None

    """
    try:

        # Agregar nuevo item a la tabla
        dynamodb.put_item(TableName='log_specto',
                          ConditionExpression='attribute_not_exists(fecha_ejecucion)',
                          Item={'fecha_ejecucion': {'S': str(star_date)},
                                'fecha': {'S': str(date)},
                                'estado': {'S': str(status)},
                                'fecha_ultima_ejecucion': {'S': str(" ")},
                               })

    except dynamodb.exceptions.ConditionalCheckFailedException:

        # Mensaje error
        print("[controler.log_specto.save_log] El registro ya existe")

def update_log(log_specto, star_date, date, status):
    """Funcion update_log().

    Actualiza un registro ya existente en la tabla log_specto, esto se debe
    a que tal descarga no se descargo correctamente, finalizo correctamente o
    se interrumpio

    Parameters
    ----------
    log_specto : tabledynamodb
        Variable tabla base de datos Dynamodb de aws
    star_date : str
        fecha de ejecucion, con formato datetime
    date : str
        fecha del dia descargado
    status: estado de la descarga

    Returns
    -------
    None
    """
    # Obtener fecha actual
    fecha_ultima_eje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Actualizar tabla
    log_specto.update_item(

        Key={
            'fecha_ejecucion': str(star_date),
            'fecha': str(date)
        },
        UpdateExpression="set estado = :r, fecha_ultima_ejecucion = :m ",
        ExpressionAttributeValues={
            ':r':str(status),
            ':m':str(fecha_ultima_eje)
        },
        ReturnValues="ALL_NEW"
        # Si la columna que va despues de "Set" no existe, se agrega
    )


def validate_log(log_specto, date, status):
    """Funcion validate_log().

    Valida que exista un registro en la tabla 'log_specto' con la fecha y
    estado de entrada

    log_specto : tabledynamodb
        Variable tabla base de datos Dynamodb de aws
    star_date : str
        fecha de ejecucion, con formato datetime
    date : str
        fecha del dia descargado
    status: estado de la descarga

    Returns
    -------
    bool
        Retorna True, si el registro existe. False, si no existe
    """
    # Buscar item en la tabla
    response = log_specto.scan(

        FilterExpression=Attr("fecha").eq(str(date))
        & Attr("estado").eq(str(status))
    )

    # Obtener total items encontrados
    encontrado = response['Count']

    # Validar cantidad
    if encontrado >= 1:

        # True si hay uno o mas
        return True

    elif encontrado == 0:

        # False si son 0
        return False
