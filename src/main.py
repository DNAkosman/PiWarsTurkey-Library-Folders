from pololu_drv8835_rpi import motors
from time import sleep, time
import RPi.GPIO as GPIO
import pygame
from threading import Thread
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import time

class Servo:

    def __init__(self):

        GPIO.setmode(GPIO.BOARD)
        pin = 35

        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.pin = pin
        self.desiredAngle = 90
        self.currentAngle = 90
        self.setState = False
        self.gotSleep = True

        print("const. calisti")



    def aciAyarlaAsil(self):

        
        duty = self.desiredAngle / 18 + 2
        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty)
        deltaAngle = abs(self.desiredAngle - self.currentAngle)
        sleepNeeeded = deltaAngle/270
        
        print(sleepNeeeded)
        sleep(deltaAngle / 150)  # experimental value
        self.gotSleep = True
        GPIO.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)
        self.currentAngle = self.desiredAngle


    def aciAyarla(self, aci):
        
        if self.gotSleep and (self.currentAngle is not aci):
            self.gotSleep = False
            self.desiredAngle = aci

            Thread(target=self.aciAyarlaAsil, args=()).start()



class UltrasonikSensor:

  def __init__(self, echo, trig):
      
    self.echo = echo
    self.trig = trig

    GPIO.setup(self.trig,GPIO.OUT)
    GPIO.setup(self.echo,GPIO.IN)

    GPIO.output(trig, False)


  def mesafeOlc(self):

    GPIO.output(self.trig, True)
    sleep(0.0000001)

    sinyal_baslangic = time()

    while GPIO.input(self.echo):
        sleep(0.0000001)
        sinyal_bitis = time()

        sure = sinyal_bitis - sinyal_baslangic

    return sure * 17150



class Motorlar:

    def __init__(self):
        self.hizSag = 0
        self.hizSol = 0

    def hizlariAyarla(self, hizSag, hizSol):

        self.hizSag = hizSag
        self.hizSol = hizSol

        480 if hizSag>480 else hizSag
        -480 if hizSag < -480 else hizSag

        480 if hizSol > 480 else hizSol
        -480 if hizSol < -480 else hizSol



        motors.setSpeeds(hizSag, hizSol)

    def kumandaVerisiniMotorVerilerineCevirme(self, x, y, t):
        if (t):
            if (math.copysign(1, x) != math.copysign(1, y)):
                return (int)((-y + x) * 240)
            else:
                return (int)((-y + x) * 480)
        else:
            if (math.copysign(1, x) == math.copysign(1, y)):
                return (int)((-y - x) * 240)
            else:
                return (int)((-y - x) * 480)



class Kumanda:

    def __init__(self):

        pygame.init()

        pygame.joystick.init()

        print("kumanda init")

        self.j = pygame.joystick.Joystick(0)
        self.j.init()


        self.buttons = []
        self.lx = 0
        self.ly = 0
        self.rx = 0
        self.ry = 0
        self.i = 0

    def dinlemeyeBasla(self):

        Thread(target=self.yenile, args=()).start()
        return self

    def yenile(self):

        while True:
            for e in pygame.event.get():
                if (e.type == pygame.JOYBUTTONDOWN and e.button not in self.buttons):
                    self.buttons.append(e.button)
                if (e.type == pygame.JOYBUTTONUP and e.button in self.buttons):
                    self.buttons.remove(e.button)
                if (e.type == pygame.JOYAXISMOTION):
                    if (e.axis == 0):
                        self.lx = e.value
                    elif (e.axis == 1):
                        self.ly = e.value
                    elif (e.axis == 2):
                        self.rx = e.value
                    elif (e.axis == 3):
                        self.ry = e.value

    def solVerileriOku(self):
        return self.lx, self.ly
    def sagVerileriOku(self):
        return self.rx, self.ry
    def butonlariOku(self):
        return self.buttons

    def verileriOku(self):
        return self.solVerileriOku(), self.sagVerileriOku(), self.butonlariOku()



class HizliPiCamera:

    def __init__(self, cozunurluk=(640, 480)):

        self.camera = PiCamera()
        self.camera.resolution = cozunurluk
        self.hamKare = PiRGBArray(self.camera, size=self.camera.resolution)
        self.yayin = self.camera.capture_continuous(self.hamKare, format="bgr", use_video_port=True)

        self.suAnkiKare = None

    def start(self):

        Thread(target=self.update, args=()).start()
        return self

    def update(self):

        for f in self.yayin:

            self.suAnkiKare = f.array
            self.hamKare.truncate(0)

    def read(self):

        return self.suAnkiKare

    def showImage(self):
        Thread(target=self.showImageAsil, args=()).start()

    def showImageAsil(self):

        while True:
            cv2.imshow("frame", self.suAnkiKare)

            key = cv2.waitKey(1)

            if key == ord("q"):
                cv2.destroyAllWindows()
                break


#deneme = Servo()

kumanda = Kumanda()

kumanda.dinlemeyeBasla()

motorlar = Motorlar()

# Kamera = HizliPiCamera()
#
# Kamera.start()
#
# time.sleep(1)
#
# Kamera.showImage()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(35, GPIO.OUT)
pwm = GPIO.PWM(35, 50)
pwm.start(0)

GPIO.output(35, True)

while True:

    lx, ly = kumanda.solVerileriOku()
    rx, ry = kumanda.sagVerileriOku()
    buttons = kumanda.butonlariOku()

    print((rx +1)* 90)
    
    pin = 35

    
    
    duty = ((rx +1)* 90) / 18 + 2
    
    pwm.ChangeDutyCycle(duty)

    #if(14 in buttons):
    #    print("aci ayarlaniyor to 150")
    #    deneme.aciAyarla(150)
    #else:
    #    deneme.aciAyarla(30)
    #    print("aci ayarlaniyor to 30")

    motorlar.hizlariAyarla(motorlar.kumandaVerisiniMotorVerilerineCevirme(lx, -ly, True), motorlar.kumandaVerisiniMotorVerilerineCevirme(lx, -ly, False))