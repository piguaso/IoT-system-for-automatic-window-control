import machine, network, time
from machine import Pin, SoftI2C, I2C, PWM
from bmp280 import BMP280
import ssd1306
from umqtt.robust import MQTTClient  # Importar MQTTClient
import urequests  # Biblioteca para solicitudes HTTP

# Configuración del bus I2C para BMP280 y OLED
bus_bmp = I2C(0, sda=Pin(0), scl=Pin(1))  # Bus I2C para el BMP280
i2c_oled = SoftI2C(scl=Pin(3), sda=Pin(2))  # Bus I2C para la OLED

# Configuración de la pantalla OLED
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_oled)

# Configuración del sensor BMP280
bmp = BMP280(bus_bmp, addr=0x77)

# Configuración de MQTT
mqtt_host = "mqtt3.thingspeak.com"
mqtt_channel_id = "2775818"  # Reemplaza con tu Channel ID
mqtt_publish_topic = f"channels/{mqtt_channel_id}/publish"
mqtt_client_id = "DygnXXXXXXXXXXXX"  # Client ID proporcionado
mqtt_username = "DygnXXXXXXXXXXXXX"  # Username proporcionado
mqtt_password = "HSw1XXXXXXXXXXXXX"  # Reemplaza con el password completo proporcionado

# Inicializar el cliente MQTT
mqtt_client = MQTTClient(
    client_id=mqtt_client_id,
    server=mqtt_host,
    port=1883,  # Puerto estándar de MQTT
    user=mqtt_username,
    password=mqtt_password
)

# Configuración del motor L298N
in3 = Pin(14, Pin.OUT)  # IN3 conectado al GPIO 14
in4 = Pin(15, Pin.OUT)  # IN4 conectado al GPIO 15
enb = PWM(Pin(13))      # ENB conectado al GPIO 13 para control PWM
enb.freq(1000)          # Configuración de la frecuencia PWM a 1 kHz

# Funciones del motor
def motor_forward(speed):
    in3.high()          # IN3 a alto
    in4.low()           # IN4 a bajo
    enb.duty_u16(speed) # Establecer velocidad del motor (0-65535 para el ciclo de trabajo)

def motor_backward(speed):
    in3.low()           # IN3 a bajo
    in4.high()          # IN4 a alto
    enb.duty_u16(speed) # Establecer velocidad del motor (0-65535 para el ciclo de trabajo)

def motor_stop():
    in3.low()           # Detener motor
    in4.low()           # Detener motor
    enb.duty_u16(0)     # Deshabilitar motor (establecer ciclo de trabajo PWM a 0)

# Conexión Wi-Fi
def conectar_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Esperar conexión
    oled.fill(0)
    oled.text("Conectando a:", 0, 0)
    oled.text(ssid, 0, 10)
    oled.show()

    tiempo_inicio = time.time()
    while not wlan.isconnected():
        if time.time() - tiempo_inicio > 10:  # Tiempo de espera máximo
            raise OSError("No se pudo conectar a la red Wi-Fi")

    print("Conexion establecida")
    oled.fill(0)
    oled.text("Conexion establecida", 0, 0)
    oled.text(f"IP: {wlan.ifconfig()[0]}", 0, 10)
    oled.show()

# Escanear redes Wi-Fi y permitir selección
def escanear_redes():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    redes = wlan.scan()  # Escanear redes disponibles

    # Mostrar las primeras 4 redes en la OLED
    oled.fill(0)
    oled.text("Redes Wi-Fi:", 0, 0)
    for i, red in enumerate(redes[:4]):
        oled.text(f"{i+1}.{red[0].decode()}", 0, 10 + i * 10)
    oled.show()

    # Mostrar redes en la terminal
    print("Redes Wi-Fi disponibles:")
    for i, red in enumerate(redes[:4]):
        print(f"{i+1}. {red[0].decode()}")

    # Seleccionar una red
    seleccion = int(input("Selecciona una red (1-4): ")) - 1
    ssid = redes[seleccion][0].decode()
    password = input(f"Introduce la contraseña para {ssid}: ")

    return ssid, password

# Publicar datos en MQTT
def publicar_datos(temp, pres):
    # Crear el mensaje en el formato ThingSpeak
    mensaje = f"field1={temp}&field2={pres}"
    print(f"Publicando: {mensaje}")
    mqtt_client.publish(mqtt_publish_topic, mensaje)
    
    # Mensaje en la terminal indicando que se envió el mensaje
    print("Mensaje enviado a ThingSpeak")

# Enviar datos a Google Sheets
def enviar_a_google_sheets(temp, pres):
    url = "https://script.google.com/macros/s/AKfycbXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    headers = {"Content-Type": "application/json"}
    data = {"temperature": temp, "pressure": pres}
    print(f"Enviando datos a Google Sheets: {data}")
    try:
        response = urequests.post(url, json=data, headers=headers)
        print(f"Respuesta del servidor: {response.text}")
        response.close()
    except Exception as e:
        print(f"Error al enviar datos: {e}")

# Configuración del intervalo de publicaciones (5 segundos)
ultima_peticion = 0
intervalo_peticiones = 5

# Variables para controlar el movimiento del motor
mover_hacia_adelante = False
mover_hacia_atras = False

try:
    # Escanear y conectar a Wi-Fi
    ssid, password = escanear_redes()
    conectar_wifi(ssid, password)

    # Conectar al broker MQTT
    mqtt_client.connect()
    print("Conectado al broker MQTT")

    while True:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
            # Leer datos del sensor BMP280
            temperatura = bmp.temperature
            presion = bmp.pressure / 100  # Convertir a hPa

            # Redondear valores
            temp = round(temperatura, 1)
            pres = round(presion, 1)

            # Mostrar datos en la OLED
            oled.fill(0)
            oled.text('BMP Temp: {:.1f}C'.format(temp), 0, 20)
            oled.text('Pressure: {:.1f}hPa'.format(pres), 0, 30)
            oled.text('Enviando datos...', 0, 40)
            oled.show()

            # Publicar datos a ThingSpeak mediante MQTT
            publicar_datos(temp, pres)

            # Enviar datos a Google Sheets
            enviar_a_google_sheets(temp, pres)

            # Lógica para mover el motor basado en la temperatura
            if temp >= 30 and not mover_hacia_adelante:
                motor_forward(62768)  # 50% de velocidad (valor PWM)
                mover_hacia_adelante = True  # Evitar múltiples movimientos hacia adelante
                mover_hacia_atras = False  # Resetear el movimiento hacia atrás
                print("Moviendo hacia adelante por 3 segundos...")
                time.sleep(3)  # Mover durante 3 segundos
                motor_stop()  # Detener motor

            elif temp <= 30 and not mover_hacia_atras:
                motor_backward(62768)  # 50% de velocidad (valor PWM)
                mover_hacia_atras = True  # Evitar múltiples movimientos hacia atrás
                mover_hacia_adelante = False  # Resetear el movimiento hacia adelante
                print("Moviendo hacia atrás por 3 segundos...")
                time.sleep(3)  # Mover durante 3 segundos
                motor_stop()  # Detener motor

            ultima_peticion = time.time()

except OSError as e:
    oled.fill(0)
    oled.text("Error de Wi-Fi", 0, 0)
