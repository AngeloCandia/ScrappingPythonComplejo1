""" Archivo functions.py.
    Este archivo, contiene todas las funciones relacionadas con el proceso
    RPA a la pagina web SPECTO.
"""
#########################################################################
import time
import sys
import os
import datetime
import configparser
from selenium import webdriver
#########################################################################

# Instanciar config.ini
config = configparser.ConfigParser()
config.read('etc/config.ini')

###########################################################################

def obtener_ayer(fecha=None): # añadir parametro para sacar hoy
    """Funcion obtener_ayer().

    Funcion que a partir de la fecha ingresada, devuelve el dia de ayer.
    Funcion sujeto a cambios por nuevos requermientos!!!

    Parameters
    ----------
    fecha : str
        Variable para obtener el dia de ayer, por defecto es None

    Returns
    -------
    ayer : str
        retorna la fecha de ayer, a la igresada inicialmente

    """

    # Validar si campo fecha es None
    if fecha == None:

        #### MODO AUTO ####
        year = int(time.strftime("%Y"))
        month = int(time.strftime("%m"))
        day = int(time.strftime("%d"))

    else:

        #### MODO USUARIO ####
        #fecha_ejemplo = "2019/12/01"
        year = fecha[0:4]
        month = fecha[5:7]
        day = fecha[8:10]

    fecha_str = str(year) + '-' + str(month) + '-' +  str(day)

    # Pasar fecha a datetime
    before_date = datetime.datetime.strptime(fecha_str, '%Y-%m-%d') +\
        datetime.timedelta(days=0)

    ########################### MEJORAR ESTA PARTE #####################
    # Le resto 1 dia
    before_date = \
        datetime.datetime.strptime(str(before_date.date()),  '%Y-%m-%d') -\
        datetime.timedelta(days=1)

    # No le resto 1 dia
    # before_date =\
    #    datetime.datetime.strptime(str(before_date.date()), '%Y-%m-%d') -\
    #    datetime.timedelta(days=0)
    ########################### MEJORAR ESTA PARTE #####################

    # Obtengo año , mes y dia de la fecha
    year = int(before_date.strftime('%Y'))
    month = int(before_date.strftime('%m'))
    day = int(before_date.strftime('%d'))

    # Validar si el dia tiene 1 digito
    if len(str(day)) == 1:

        # Agregar un 0 a la izquierda
        day = f"0{str(day)}"

    # Validar si mes tiene 1 digito
    if len(str(month)) == 1:

        # Agregar un 0 a la izquierda
        month = f"0{str(month)}"

    # Obtener la fecha de ayer con el formato correspondiente
    ayer = str(year) + "/" + str(month) + "/" + str(day)

    # Retornar fecha de ayer
    return ayer

#################################################################################

def cantidad_csv():
    """ cantidad_csv().

    Funcion que cuenta cantidad de archivos '.csv' en una carpeta determinada

    Returns
    -------
    contador_csv : int
        retorna la cantidad de archivos '.csv' que actualmente existen en el
        directorio

    """
    # Variable entera con valor 0 por defecto
    contador_csv = 0

    # Obtener ruta de la carpeta del proyecto
    ruta_fija = os.getcwd().replace("\\", "/") + "/" # C:/Users/Angelo/Documents/cosmos_specto/

    # Obtener directorio documents
    directory = os.path.join(ruta_fija + "/documents")

    # Loop para cada elemento en el directorio
    for root, dirs, files in os.walk(directory):

        # Loop especifico para los archivos
        for file in files:

            # Validar si el archivo termina con .csv
            if file.endswith(".csv"):

                # sumar al contador + 1
                contador_csv += 1

    # Retornar contador_csv
    return contador_csv

##################################################################################

def iniciar_scraping():
    """Funcion iniciar_scraping().

    Funcion que inicia el proceso RPA a la pagina Specto.
    Principalmente, configura el navegador a ejecutar, setea la ruta de
    descarga y retorna la variable driver

    Returns
    -------
    driver : selenium
        variable para interactuar con la pagina SPECTO

    """

    # Obtener ruta de la carpeta del proyecto
    ruta_fija = os.getcwd() # C:\Users\Angelo\Documents\cosmos_specto

    # Obtener url pagina specto
    url = config.get('specto', 'url')

    # Instanciar opciones chrome
    chromeOptions = webdriver.ChromeOptions()

    # Configuracion de descarga chrome
    # La ruta de descarga tiene que ir con los '\'
    prefs = {"download.default_directory": ruta_fija+"\documents",
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "safebrowsing.enabled": True}

    # Añadir configuracion
    chromeOptions.add_experimental_option("prefs", prefs)

    # Crear variable RPA con ejecutate y preferencias
    driver = webdriver.Chrome(executable_path="sw\chromedriver.exe", options=chromeOptions)

    # Tiempo de espera a elementos de la pagina web
    driver.implicitly_wait(2)

    # Iniciar proceso RPA
    driver.get(url)

    # Devolver variable RPA
    return driver

###############################################################################

def access_login(driver):
    """Funcion access_login().

    Funcion que abarca todo el proceso de acceso e ingreso al login de la
    pagina especto

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web

    """

    # Obtener variable usuario
    usuario = config.get('specto', 'user')

    # Obtener variable contraseña
    clave = config.get('specto', 'password')

    # Buscar campo usuario e ingresar variable usuario
    driver.find_element_by_id("formLoginUsuario").send_keys(usuario)

    # Buscar campo contraseña e ingresar variable contraseña
    driver.find_element_by_id("formLoginClave").send_keys(clave)

    # Buscar boton 'iniciar sesion'
    driver.find_element_by_name("Submit").click()

    # Buscar opcion 'Motores' en la barra de navegacion
    driver.find_element_by_id("menuEngines").click()

###############################################################################

def llenar_formulario(driver, desde=None, solo_fecha=False):
    """Funcion llenar_formulario().

    Funcion que llena los campos de entrada necesarios para descargar los
    datos RPM de los distintos camiones

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web SPECTO
    desde : str
        Variable que indica el rango de fecha que se quiere descargar durante
        la ejecucion
    solo_fecha : str
        Variable para validar si antes de descargar cierto dia, es necesario
        volver a llenar el formulario

    Returns
    -------
    ayer: str
        devuelve la siguiente fecha a descargar


    """
    # Valida si queremos sacar la fecha de ayer o una anterior a ayer
    if desde == None:

        # Llama a la funcion obtener_ayer()
        ayer = obtener_ayer()

    else:

        # Llama a la funcion obtener_ayer() con fecha
        ayer = obtener_ayer(desde)

    # Lista con los campos de entrada
    campos = ["fleet_state_power_min",
              "fleet_state_power_max",
              "fleet_state_load_factor_min",
              "fleet_state_load_factor_max",
              "fleet_state_pedal_min",
              "fleet_state_pedal_max",
              "fleet_state_rpm_min",
              "fleet_state_rpm_max"]

    # Lista con los campos fecha inicio y fin
    campos_fecha = ["fechaDesde", "fechaHasta"]

    # ¿Que es solo_fecha ?
    # Es una variable que define como se llena el formulario de Specto.
    # True, significa que ya se a llenado anteriormente, entonces solo se registra la fecha nueva
    # False, significa que es la primera fecha a ingresar, por ende, se llena todo el formulario

    # Valida solo fecha
    if solo_fecha:

        # Recorre los campos_fecha
        for x in campos_fecha:

            # Limpiar el campo de entrada
            driver.find_element_by_id(x).clear()

            # Descansa 1 segundo
            time.sleep(1)

            # Ingresar en el campo de entrada la fecha de ayer
            driver.find_element_by_id(x).send_keys(ayer)

    else:

        # Recorre variable campos
        for x in campos:

            # Ingresa 0 en los campos de entrada
            driver.find_element_by_id(x).send_keys("0")

        # Recorre variable campos_fecha
        for x in campos_fecha:

            # Ingresa la fecha de ayer
            driver.find_element_by_id(x).send_keys(ayer)

        hoy = time.strftime('%Y/%m/%d')

        if hoy == ayer:

            fecha_ahora = datetime.datetime.now()

            fecha_atras = datetime.datetime.now() - datetime.timedelta(hours=4)

            hora_inicio = '{:02}:00'.format(fecha_atras.hour)

            hora_fin = str(fecha_ahora.hour) + ':00'

        else:

            hora_inicio = '00:00'

            hora_fin = '23:59'

        # Busca el campo horaDesde y agrega "00:00"
        driver.find_element_by_id("horaDesde").send_keys(hora_inicio)

        # Busca el campo HoraHasta y agrega "23:59", ambos tienen el mismo nombre
        driver.find_elements_by_id("horaDesde")[1].send_keys(hora_fin)

        ############################## MEJORAR ESTA PARTE #######################
        try:
            
            driver.find_element_by_id("puntos_muestra").clear()
            
            driver.find_element_by_id("puntos_muestra").send_keys("87000")
            
        except:
            
            pass
        ############################## MEJORAR ESTA PARTE #######################

        # Llama funciona seleccionar_paramentros
        driver = seleccionar_parametros(driver)

    # Valida si el RPA esta scrapiando un rango de fecha
    if desde == None:

        # En caso de que no, devuelve 0. el proceso finalizara
        return 0

    else:

        # En caso que si, el proceso continuara con la fecha anterior
        return ayer

###############################################################################

def seleccionar_parametros(driver):
    """Funcion seleccionar_parametros().

    Funcion para seleccionar las columnas, requeridas para obtener el RPM de
    los camiones. Esta funcion reduce en gran medida las columnas que no se
    utilizan

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web SPECTO

    Returns
    -------
    driver: selenium
        devuelve la variable interaccion a la pagina web, para continuar
        con la ejecucion, en el punto donde se encuentra


    """

    # Busca elemento 'submit'
    parametros = driver.find_element_by_class_name("submit")

    # Clic al boton
    parametros.click()

    # Buscar elemento en el modal con nombre displayParametersBox
    modal = driver.find_element_by_id("displayParametersBox")

    # Obtener las opciones del modal
    modal_options = modal.find_elements_by_class_name("paramElement")

    # Recorrer las opciones del modal
    for option in modal_options:

        # Valida si la opcion es 'Actual Speed'
        if str(option.text) == "Actual Speed":

            # Obtenemos el checkBox de la opcion
            checkbox = option.find_element_by_class_name("parametroCheckboxDummy")

            # Verificar el estado del checkbox
            status = checkbox.is_selected()

            # Validar si esta marcado
            if status:

                # No hacer nada, esta ya marcado el checkbox
                pass

            else:

                # El checkbox no esta marcado, se marca
                option.click()

            # Buscar el boton para salir del modal
            driver.find_element_by_class_name("button").click()

            # Romper el loop
            break

    # Retornar variable driver
    return driver

###############################################################################
# Funcion para recorrer combo box en paginas web
def select_drop(driver, drop):
    """Funcion select_drop().

    Funcion para recorrer los distintos combo box que tiene la pagina web
    SPECTO y seleccionar el elemento requerido

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web SPECTO
    drop : str
        Opcion que necesitamos encontrar

    Returns
    -------
    option: str
        devuelve las opciones que contiene el combo box


    """

    # Buscar drop con la variable 'drop'
    input_select = driver.find_element_by_id(drop)

    # Optener opciones del drop
    option = input_select.find_elements_by_tag_name("option")

    # Validar el tipo de drop
    if drop == "fleet_id":

        # Validar total de opciones
        while len(option) != 9:

            # Volver a sacar las opciones, en ocasiones no carga todo
            option = select_drop(driver, "fleet_id")

    # Validar tipo de drop
    elif drop == "device_avl":

        # Validar total de opciones
        while len(option) <= 1: #sub_option

            # Volver a sacar las opciones, en ocasiones no carga todo
            sub_option = select_drop(driver, "device_avl")

    # Si la opcion es 'site_id', no le haremos cambios a option

    # Borrar primera opcion, siempre es 'Seleccione'
    option.pop(0)

    # Devolvermos opciones
    return option

###############################################################################

def download_files(driver):
    """Funcion download_files().

    Funcion que realiza las descargas de todos los camiones de un dia

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web SPECTO

    Returns
    -------
    bool
        True si las descargas se realizaron correctamente, False si hubo un
        error durante la ejecucion


    """
    try:

        # Usar funcion select_drop() con 'fleed_id'
        option = select_drop(driver, "fleet_id")

        # Loop a las opciones
        for flotas in option:

            # Clic a la flota
            flotas.click()

            # Descansa 5 segundos
            time.sleep(5)

            # Obtener las opciones a partir de la flota
            sub_option = select_drop(driver, "device_avl")

            # Loop a las opciones de las flota
            for equipos in sub_option:

                # Variable contador con valor 0
                contador = 0

                # Validar si el equipo es PALA
                if equipos.text[0:4] == "PALA":

                    # Omitir equipo
                    pass

                else:

                    # Descansa 5 segundos
                    time.sleep(3)

                    # Clic a la opcion equipo
                    equipos.click()

                    # Buscar boton para descargar csv
                    driver.find_element_by_name("SubmitExcel").click()

                    # Llamamos a la function cantidad_csv()
                    n_contador_csv = cantidad_csv()

                    # call a la funcion cantidad_csv() para asignar el mismo valor en otra variable
                    o_contador_csv = cantidad_csv()

                    # ¿Que es n_contador_csv y o_contador_csv?
                    # Son variables enteras que indican el total de archivos csv en una carpeta
                    # n = nuevo, o = original
                    # Poco antes de definirlas en paralelo se esta descando un archivo csv nuevo
                    # Elel while valida que o_contador_csv sea distinto a n_contador_csv pero mas 1
                    # Cuando el while se rompa, significa que ya se descargo completamente el csv
                    # y finalmente ambas variables tienen el mismo valor
                   
                    count = 0
                    while o_contador_csv != (n_contador_csv + 1):

                        # Volver a llamar a la funcion cantidad_csv()
                        o_contador_csv = cantidad_csv()

                        count = count + 1
                        if count >= 550000:
                            print("La descarga fallo")
                            driver.find_element_by_name("SubmitExcel").click()
                            break
                    count = 0

                #break # Estos break estan para reducir el total de archivo de cada fecha

            #break # Estos break estan para reducir el total de archivo de cada fecha

            # Asignar las sub opciones de flotas a None para agregar las que siguen
            sub_option = None

        return True

    except Exception as e:

        # Guardar en variable la linea , nombre y detalle del error
        line_error, name_error, d_name_error = \
            'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__,

        # Mensaje de error
        print("[controler.functions.download_files]Error durante descarga")
        print("[app.run.download_files] " + line_error)
        print("[app.run.download_files] " + name_error)
        print("[app.run.download_files] " + str(d_name_error))

        return False

###############################################################################

def cerrar_scrapping(driver):
    """Funcion cerrar_scrapping().

    Funcion para cerrar el navegador una vez finalizaod el proceso RPA

    Parameters
    ----------
    driver : selenium
        Variable para interactuar con la pagina web SPECTO, en este caso,
        cerrar el navegador y finalizar el script

    """
    # Cerrar navegador
    driver.quit()

    # Finalizar proceso
    sys.exit(0)
    