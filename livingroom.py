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
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label

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

# This callback will be bound to the toggle buttons and temperature display:
def press_callback(obj):
	print("Button pressed,", obj.text)
	if obj.text == 'COUNTER':
		if obj.state == "down":
			print ("button on")
			GPIO.output(counterPin, GPIO.HIGH)
		else:
			print ("button off")
			GPIO.output(counterPin, GPIO.LOW)

    if obj.text == 'SHELF':
		if obj.state == "down":
			print ("button on")
			GPIO.output(shelfPin, GPIO.HIGH)
		else:
			print ("button off")
			GPIO.output(shelfPin, GPIO.LOW)

	if obj.text == 'COUCH':
		if obj.state == "down":
			print ("button on")
			GPIO.output(couchPin, GPIO.HIGH)
		else:
			print ("button off")
			GPIO.output(couchPin, GPIO.LOW)


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
		outputControl = ToggleButton(text="COUCH")
		outputControl.bind(on_press=press_callback)
		beepButton = Button(text="COUNTER")
		beepButton.bind(on_press=press_callback)


		# Add the UI elements to the layout:
		layout.add_widget(inputDisplay)
		layout.add_widget(outputControl)
		layout.add_widget(beepButton)


		return layout

if __name__ == '__main__':
	MyApp().run()
