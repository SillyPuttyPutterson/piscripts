import os
import glob
import time
#Initialize DS18B20 Temp Sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import RPi.GPIO as GPIO

# Set up GPIO:
couchPin = 17
shelfPin = 27
counterPin = 22
tempPin = 10
GPIO.setmode(GPIO.BCM)
GPIO.setup(couchPin, GPIO.OUT)
GPIO.output(couchPin, GPIO.LOW)
GPIO.setup(shelfPin, GPIO.OUT)
GPIO.output(shelfPin, GPIO.LOW)
GPIO.setup(counterPin, GPIO.OUT)
GPIO.output(counterPin, GPIO.LOW)
GPIO.setup(tempPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define some helper functions:

#Read Temp sensor and convert to F
def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
		equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		return temp_f

# This callback will be bound to the LED toggle and Beep button:
def press_callback(obj):
	print("Button pressed,", obj.text)
	if obj.text == 'BEEP!':
		# turn on the beeper:
		GPIO.output(beepPin, GPIO.HIGH)
		# schedule it to turn off:
		Clock.schedule_once(buzzer_off, .1)
	if obj.text == 'LED':
		if obj.state == "down":
			print ("button on")
			GPIO.output(ledPin, GPIO.HIGH)
		else:
			print ("button off")
			GPIO.output(ledPin, GPIO.LOW)

def buzzer_off(dt):
	GPIO.output(beepPin, GPIO.LOW)

# Toggle the flashing LED according to the speed global
# This will need better implementation
def flash(dt):
	global speed
	GPIO.output(flashLedPin, not GPIO.input(flashLedPin))
	Clock.schedule_once(flash, 1.0/speed)

# This is called when the slider is updated:
def update_speed(obj, value):
	global speed
	print("Updating speed to:" + str(obj.value))
	speed = obj.value

# Modify the Button Class to update according to GPIO input:
class InputButton(Button):
	def update(self, dt):
		if GPIO.input(buttonPin) == True:
			self.state = 'normal'
		else:
			self.state = 'down'

class MyApp(App):

	def build(self):
		# Set up the layout:
		layout = GridLayout(cols=5, spacing=30, padding=30, row_default_height=150)

		# Make the background gray:
		with layout.canvas.before:
			Color(.2,.2,.2,1)
			self.rect = Rectangle(size=(800,600), pos=layout.pos)

		# Instantiate the first UI object (the GPIO input indicator):
		inputDisplay = InputButton(text="Input")

		# Schedule the update of the state of the GPIO input button:
		Clock.schedule_interval(inputDisplay.update, 1.0/10.0)

		# Create the rest of the UI objects (and bind them to callbacks, if necessary):
		outputControl = ToggleButton(text="LED")
		outputControl.bind(on_press=press_callback)
		beepButton = Button(text="BEEP!")
		beepButton.bind(on_press=press_callback)
		wimg = Image(source='logo.png')
		speedSlider = Slider(orientation='vertical', min=1, max=30, value=speed)
		speedSlider.bind(on_touch_down=update_speed, on_touch_move=update_speed)

		# Add the UI elements to the layout:
		layout.add_widget(wimg)
		layout.add_widget(inputDisplay)
		layout.add_widget(outputControl)
		layout.add_widget(beepButton)
		layout.add_widget(speedSlider)

		# Start flashing the LED
		Clock.schedule_once(flash, 1.0/speed)

		return layout

if __name__ == '__main__':
	MyApp().run()
