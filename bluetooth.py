#Comandi utili

#self.ble.gatts_write(self.tx, 'MSG')

#self.ble.gatts_notify(1, self.tx, 'ciao')


from machine import Pin
from machine import Timer
from time import sleep_ms
import ubluetooth
import turtle
import testbooting

ble_msg = ""
ble_buffer= ""
ble_lati=""
ble_numpoli=""

class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):        
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    
    def ble_irq(self, event, data):
        global ble_msg
        global ble_buffer
        global ble_lati
        global ble_numpoli
        
        #Connessione
        if event == 1:
            
            self.connected()
            sleep_ms(1000)
            self.ble.gatts_notify(1, self.tx, 'Cosa si vuole fare? \n')
            self.ble.gatts_notify(1, self.tx, 'Andare dritto \n Girare a destra \n Girare a sinistra \n Fare un poligono regolare \n Fare un polipoligono \n')
            
        #Disconnessione
        elif event == 2:
            
            self.advertiser()
            self.disconnected()
        
######################################################################################################################################
        
        #Scrittura nella chat
        elif event == 3:
            
            #Lettura da chat bluetooth e salvataggio in una variabile
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
            #Funzionalità
            
            #Per andare dritto
            if ble_msg == 'Andare dritto':
                sleep_ms(1000)
                self.ble.gatts_notify(1, self.tx, 'Aggiungere lunghezza da percorrere in cm \n')
               
            elif ble_buffer == 'Andare dritto':    
                ble_buffer = int(ble_msg)
                turtle.forward(ble_buffer*10)
                ble_msg=''
            
            #Per girare a destra
            elif ble_msg == 'Girare a destra':
                self.ble.gatts_notify(1, self.tx, 'Di quanto si vuole girare in gradi \n')
            
            elif ble_buffer == 'Girare a destra':
                ble_buffer = int(ble_msg)
                turtle.right(ble_buffer)
                ble_msg = ''
           
            #Per girare a sinistra
            elif ble_msg == 'Girare a sinistra':
                self.ble.gatts_notify(1, self.tx, 'Di quanto si vuole girare in gradi \n')
            
            elif ble_buffer == 'Girare a sinistra':
                ble_buffer = int(ble_msg)
                turtle.left(ble_buffer)
                ble_msg = ''
            
            #Per fare un quadrato 
            elif ble_msg == 'Fare un poligono regolare':
                self.ble.gatts_notify(1, self.tx, 'Quanti lati deve avere \n ')
                
            elif ble_buffer == 'Fare un poligono regolare':
                ble_lati= int(ble_msg)
                self.ble.gatts_notify(1, self.tx, 'Quanto deve essere lungo il lato in cm \n ')
                ble_buffer == 'Poligono verificato'
                
            elif ble_buffer == 'Poligono verificato':
                ble_buffer = int(ble_msg)
                for i in range(ble_lati):
                    turtle.forward(ble_buffer*10)
                    turtle.right(360/lati)
                
                
            ble_buffer = ble_msg
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
                # adv_data
                # raw: 0x02010209094553503332424C45
                # b'\x02\x01\x02\t\tESP32BLE'
                #
                # 0x02 - General discoverable mode
                # 0x01 - AD Type = 0x01
                # 0x02 - value = 0x02
                
                # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
                # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics



led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")

def buttons_irq(pin):
    led.value(not led.value())
    ble.send('LED state will be toggled.')
    print('LED state will be toggled.')   
but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)