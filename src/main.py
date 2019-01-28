
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
import imutils
import PiWarsTurkiyeRobotKiti2019
class Servo:
    def __init__(self, pin, setup=GPIO.BOARD):
        GPIO.setmode(setup)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.pin = pin
        self.desiredAngle = 90
        self.currentAngle = 90
        self.setState = False
        self.gotSleep = True
    def aciAyarlaAsil(self):
        duty = self.desiredAngle / 18 + 2
        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty)
        deltaAngle = abs(self.desiredAngle - self.currentAngle)
        sleepNeeeded = deltaAngle/270
        self.gotSleep = False
        print(sleepNeeeded)
        sleep(deltaAngle / 270)  # experimental value
        self.gotSleep = True
        GPIO.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)
        self.currentAngle = self.desiredAngle
    def aciAyarla(self, aci):
        if self.gotSleep:
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
        self.j = pygame.joystick.Joystick(0)
        self.j.init()
        self.buttons = []
        self.lx = 0
        self.ly = 0
        self.i = 0
    def dinlemeyeBasla(self):
        Thread(target=self.yenile, args=()).start()
        return self
    def yenile(self):
        while True:
            for e in pygame.event.get():
                if (e.type == pygame.JOYAXISMOTION):
                    if (e.axis == 0):
                        self.lx = e.value
                    elif (e.axis == 1):
                        self.ly = e.value
    def verileriOku(self):
        return self.lx, self.ly
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
kumanda = Kumanda()
kumanda.dinlemeyeBasla()
# servo = Servo(37)
motorlar = Motorlar()
# Kamera = HizliPiCamera()
#
# Kamera.start()
#
# time.sleep(1)
#
# Kamera.showImage()
while True:
    lx, ly = kumanda.verileriOku()
    print(lx, ly)
    motorlar.hizlariAyarla(motorlar.kumandaVerisiniMotorVerilerineCevirme(lx, -ly, True), motorlar.kumandaVerisiniMotorVerilerineCevirme(lx, -ly, False))