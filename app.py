'''
    Proyecto RPA cosmos_specto
    Obtener las RPM de los camiones
'''
#########################################################################
import os
import os.path
import time
import glob
import datetime
import sys
#########################################################################
from controler import (iniciar_scraping, access_login, llenar_formulario,
                       select_drop, download_files, cerrar_scrapping,
                       save_log, update_log, validate_log)
from model import Bucket
#########################################################################


# Funcion ejecutar Specto
def run_specto():
    '''
        run_specto()
        funcion base del proyecto cosmos_specto.
        En ella contiene todas las funciones y procesos que realiza
        durante la ejecucion
        No recibe parametros
        No retorna un valor
    '''
    ######################################################################

    # Iniciar scraping
    driver = iniciar_scraping()

    ######################################################################

    try:

        # Realizar login
        access_login(driver)

    except Exception as error:

        # Mensaje Error
        print("[app.run_specto] Pagina en mantenimiento, cerrando app")
        print(error)

        # Cerrar navegador
        driver.quit()

        # Finalizar RPA
        sys.exit(0)

    ##########################################################################

    # Buscar opcion en la barra de navegacion
    sm = driver.find_elements_by_class_name("menuFloatingEntry")

    opcion_formulario = "Gráfico/Descarga Último mes" # "Gráfico/Descarga Histórico"  #  #
    # Loop opciones barra de navegacion
    for x in sm:

        # Validar la opcion a buscar
        if x.text == opcion_formulario:

            # Click al boton
            x.click()

            # Romper loop
            break

    ###########################################################################

    # SE CAYO, AÑADI ESTO, MEJORAR MAS ADELANTE
    time.sleep(1)

    # Usar funcion select_drop, devuelve las opciones del drop
    option = select_drop(driver, "site_id")

    # Recorrer opciones del drop
    for f in option:

        # Valida opcion a buscar
        if f.text == "Los Pelambres":

            # Clic en la opcion
            f.click()

            # Rompe el loop
            break

    ###########################################################################

    # Ejecucion fecha definida
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # fecha_anterior = llenar_formulario(driver,"2020/04/21") # YYYY-MM-DD
    fecha_anterior = llenar_formulario(driver, "2020/06/30")  # YYYY-MM-DD

    ###########################################################################

    # Obtener año, mes y dia de la fecha anterior
    year = fecha_anterior[0:4]
    month = fecha_anterior[5:7]
    day = fecha_anterior[8:10]

    # Pasar fecha a Datetime
    fecha_limite = datetime.datetime.strptime(str(year) + '-' + str(month) + '-' +  str(day), '%Y-%m-%d') + datetime.timedelta(days=1) #fecha limite igual fecha anterior

    # Obtener un rango de fecha desde la fecha ingresada
    fecha_limite = datetime.datetime.strptime(str(fecha_limite.date()), '%Y-%m-%d') - datetime.timedelta(days=30) #lecha limite -60 dias

    # Reeemplazar '-' con '/'
    fecha_limite = str(fecha_limite)[0:10].replace("-", "/")

    # Instanciar Bucket
    b = Bucket()

    # Objeto dynamoDB
    dynamodb = b.get_dynamodb_c()
    log_specto = b.get_dynamodb_s()

    # Capturar cuando se caiga la ejecucion de descarga
    try:

        # Loop desde fecha limite hasta fecha anterior
        while str(fecha_anterior) >= str(fecha_limite):

            existe = validate_log(log_specto, fecha_anterior, "Finalizado")

            if existe:

                # Mensaje dia ya descargado y finalizado
                print(f"[app.run] Data from {fecha_anterior} alredy exists, skip...")

                # Continuar con la siguiente fecha
                fecha_anterior = llenar_formulario(driver, str(fecha_anterior), True)

                # Sigue siguiente iteracion
                continue

            # Obtener la fecha en este mismo momento
            fecha_eje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Crear un registro en 'log_specto'
            save_log(dynamodb, fecha_eje, fecha_anterior, "Comenzando descargas")

            # Obtener la hora
            desde = datetime.datetime.now().strftime("%H:%M:%S")

            # Mensaje inicio de descarga
            print(f"[app.run] Star download files to {fecha_anterior} from {desde}")

            # Descargar archivos
            completado = download_files(driver) # descarga todos los camiones del dia

            # Obtener la hora, de nuevo
            desde = datetime.datetime.now().strftime("%H:%M:%S")

            # Mensaje fin de descarga
            print(f"[app.run] Finish download files to {fecha_anterior} from {desde}")

            ##################### AQUI BORRA EL ARCHIVO ###############################

            # Obtener ruta del proyecto
            ruta = os.getcwd() + "/documents"

            # Obtener lista archivos con formato .csv
            source = ruta + "/*.csv"

            # Obtener lista de archivos
            files = glob.glob(source)

            # Loop a los archivos csv
            for f in files:

                # Obtener nombre y ruta del archivo csv
                filename = os.path.basename(f)

                # Subir archivo al S3
                b.upload(f, f'specto/{filename}')

                # Borrar archivo en local
                os.remove(f)

            # ############ AQUI BORRA EL ARCHIVO ##########################

            if completado:

                update_log(log_specto, fecha_eje,
                           fecha_anterior, "Finalizado")

            else:

                update_log(log_specto, fecha_eje,
                           fecha_anterior, "Descarga interrumpida")

            # Continuar con la siguiente fecha
            fecha_anterior = llenar_formulario(driver, str(fecha_anterior), True)

    except Exception as e:

        update_log(log_specto, fecha_eje,
                   fecha_anterior, "Descarga interrumpida")

        # Guardar en variable la linea , nombre y detalle del error
        line_error, name_error, d_name_error =\
            'Error on line {}'.\
            format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e

        # Mensaje de error
        print("[app.run_specto]Error ejecucion")
        print("[app.run] " + line_error)
        print("[app.run] " + name_error)
        print("[app.run] " + str(d_name_error))

    # Cierra el navegador
    cerrar_scrapping(driver)


# Ejecutar proceso
if __name__ == '__main__':

    # Nombre de la funcion inicio
    print("[app.run] Start RPA Specto Process")
    run_specto()
    print("[app.run] Finish RPA Specto Process")
