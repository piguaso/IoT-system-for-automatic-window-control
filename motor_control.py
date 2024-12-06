from machine import Pin, PWM

# Motor pins
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
