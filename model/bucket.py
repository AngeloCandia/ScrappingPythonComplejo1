'''
    bucket.py:

        archivo que contiene la clase y funciones necesarias para subir
        los archivos output al buscket s3 de AWS
'''
import configparser

import boto3

CONFIG = configparser.ConfigParser()
CONFIG.read('etc/config.ini')


class Bucket:
    '''
        Clase Bucket:
        Clase que contine los parametros necesarios para logearse al buscket.
        Contiene las funciones para subir archivo con formato csv al bucket
        Y
        La funcion para acceder a la base de de datos DynamoDB 'log_specto'
    '''
    def __init__(self):
        '''
            Funcion __init__()
            Funcion de inicio al instanciar la clase Bucket
            Args:
                self (self): Variable autoreferente a la clase instanciada
            Parameters
                ----------
                region_name : str
                    Nombre de region de la cuenta AWS
                accesss_key : str
                    Clave para acceder al bucket
                secret_accesss_key : str
                    Clave secreta para acceder al bucket
                bucket_name : str
                    Nombre del bucket destino
                s3_b : boto3
                    Variable para subir los archivos al bucket principalmente
                dynamodb: boto3
                    Vatiable para manejar la base de datos DynamoDB a nivel
                    cliente
                dynamodb2: boto3
                    Vatiable para manejar la base de datos DynamoDB a nivel
                    recurso

        '''
        self.region_name = CONFIG.get('aws', 'region_name')
        self.access_key = CONFIG.get('aws', 'access_key')
        self.secret_access_key = CONFIG.get('aws', 'secret_access_key')
        self.bucket_name = CONFIG.get('aws', 'bucket_name')

        self.s3_b = boto3.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_access_key
        )

        self.dynamodb = boto3.client(
            'dynamodb',
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_access_key
        )

        self.dynamodb2 = boto3.resource(
            'dynamodb',
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_access_key
        )

    def upload(self, filename, key):
        '''
            upload()
            Funcion para subir los archivos output al bucket
            Parameters
            ----------
            filename : str
                Nombre del archivo descargado
            key : str
                Ruta de destino dle bucker
        '''
        try:
            self.s3_b.upload_file(
                Filename=filename,
                Bucket=self.bucket_name,
                Key=key
            )
        except Exception as error:
            print(f"[controller.Bucket.upload] {str(error)}")

    def get_dynamodb_c(self):
        '''
            get_dynamodb_c()
            Funcion para obtener dynamodb a nivel cliente
        '''
        return self.dynamodb
        # return self.dynamodb, self.dynamodb2

    def get_dynamodb_s(self):
        '''
            get_dynamodb_c()
            Funcion para obtener dynamodb a nivel recurso
        '''
        log_specto = self.dynamodb2.Table('log_specto')

        return log_specto
