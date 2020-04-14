"""

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com

"""

import RPi.GPIO as GPIO
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

elements = {
	'boil': {'pin': 30},
	'hlt': {'pin': 22}
}
pumps = {
	'wort': {'pin': 23},
	'water': {'pin': 24}
}


def initialize():
	for pump in pumps:
		GPIO.setup(pumps[pump]['pin'], GPIO.OUT, initial=GPIO.LOW)
	for element in elements:
		GPIO.setup(elements[element]['pin'], GPIO.OUT, initial=GPIO.LOW)


@app.route("/")
def ces():
	templateData = {
		'boilelement': GPIO.input(elements['boil']['pin']),
		'hltelement': GPIO.input(elements['hlt']['pin']),
		'wortpump': GPIO.input(pumps['wort']['pin']),
		'waterpump': GPIO.input(pumps['water']['pin']),
	}
	return render_template('ces.html', **templateData)


@socketio.on('shutdown')
def shutdown():
	shutdown_server()
	return 'Server shutting down...'


@socketio.on('my_event')
def test_message(message):
	session['receive_count'] = session.get('receive_count', 0) + 1
	emit('my_response',
	     {'data': message['data'], 'count': session['receive_count']})


@socketio.on('toggle_pump')
def toggle_pump(pump):
	session['receive_count'] = session.get('receive_count', 0) + 1
	pinNumber = pumps[pump]['pin']
	if GPIO.input(pinNumber) == GPIO.LOW:
		GPIO.output(pinNumber, GPIO.HIGH)
		message = "Turned " + pump + " pump on."
	else:
		GPIO.output(pinNumber, GPIO.LOW)
		message = "Turned " + pump + " pump off."

	emit('my_response', {'data': message, 'count': session['receive_count']})


@socketio.on('toggle_element')
def toggle_element(element):
	session['receive_count'] = session.get('receive_count', 0) + 1
	pinNumber = elements[element]['pin']
	if GPIO.input(pinNumber) == GPIO.LOW:
		GPIO.output(pinNumber, GPIO.HIGH)
		message = "Enabled " + element + " element."
	else:
		GPIO.output(pinNumber, GPIO.LOW)
		message = "Disabled " + element + " element."

	emit('my_response', {'data': message, 'count': session['receive_count']})


@socketio.on('set_target_temp')
def set_target_temp(message):
	session['receive_count'] = session.get('receive_count', 0) + 1
	element = message['elementName']
	temp = message['temp']
	pinNumber = elements[element]['pin']
	message = "Set " + element + " target temp to " + temp + "."

	emit('my_response', {'data': message, 'count': session['receive_count']})


def shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')

	for pump in pumps:
		GPIO.output(pumps[pump]['pin'], GPIO.LOW)
	GPIO.cleanup()

	func()


if __name__ == "__main__":
	initialize()
	socketio.run(app, host='0.0.0.0', debug=True)
