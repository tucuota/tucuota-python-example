from flask import Flask, jsonify, request, redirect
import tucuota
from os import getenv

app = Flask(__name__)
tc = tucuota.TC(getenv('TC_API_KEY'))
intro = """

En este ejemplo mostramos cómo agregar pagos y suscripciones a través del checkout de TuCuota.
Más información en nuestra documentación:
https://tucuota.com/docs

Hará falta sacar un token de acceso en https://sandbox.tucuota.com/dashboard/developers y ponerlo como variable de entorno:
export TC_API_KEY=........

Para activar las notificaciones por webhook, en la misma url agregar una dirección webhook y la variable de entorno del código secreto
export TC_API_WEBHOOK_SECRET=....

Tarjeta para hacer pruebas en sandbox:
mastercard
5447651834106668

Rutas
/tucuota/payment
/tucuota/subscription

Donde se redirigen los checkouts exitosos
/tucuota/callback

Webhooks para recibir notificaciones
/tucuota/webhooks (POST)
"""


@app.route('/')
def hello():
	return "<pre>%s</pre>" % intro


@app.route('/tucuota/payment')
def payment():
	tc.sandbox = True


	# Pago, esta vez agregando datos del cliente
	response = tc.post('api/sessions', {
		'description' : "Pago único",
		'success_url' : "http://127.0.0.1:5000/tucuota/callback?course_id=5", # esta uri no será visible hasta que se complete el flujo del checkout y el cliente no la verá nunca.

		'kind' : "payment",
		'amount' : 12000, # Monto del pago
		'max_installments' : 3, # cantidad de cuotas

		'customer_id': 1544,
		'customer_name': "Juan Ramonda",
		'customer_email': "juanchoramonda@gmail.com",

		'metadata' : { # se pueden agregar acá cualquier tipo de metadatos. La suscripción o pagos que genere el checkout también tendrán la misma metadata
			'course_id': 5,
		},
	})

	uri = response.get('data', {}).get('public_uri')

	return redirect(uri)
	return jsonify(response)


@app.route('/tucuota/subscription')
def subscription():
	tc.sandbox = True

	# Suscripción, esta vez agregando solo id de cliente
	response = tc.post('api/sessions', {
		'description' : "Curso",
		'success_url' : "http://127.0.0.1:5000/tucuota/callback?course_id=5", # esta uri no será visible hasta que se complete el flujo del checkout y el cliente no la verá nunca.

		'kind' : "subscription",
		'amount' : 12000, # Monto del pago
		'count' : 3, # cantidad de repeticiones de la suscripción

		'customer_id': 1544,

		'interval_unit': "monthly",


		'metadata' : { # se pueden agregar acá cualquier tipo de metadatos. La suscripción o pagos que genere el checkout también tendrán la misma metadata
			'course_id': 5,
		},
	})

	uri = response.get('data', {}).get('public_uri')

	return redirect(uri)
	return jsonify(response)


@app.route('/tucuota/callback')
def callback():
	course_id  = request.args.get('course_id')
	session_id = request.args.get('session_id')

	# Created resource
	session = tc.get('api/sessions/%s' % session_id)
	createdResource = session.get('data', {}).get('resource')

	return jsonify(createdResource)


@app.route("/tucuota/webhooks", methods=["POST"])
def webhooks():

	payload = request.data.decode("utf-8")
	timestamp = request.headers.get("TuCuota-Timestamp", None)
	received_sig = request.headers.get("TuCuota-Signature", None)
	secret = getenv('TC_API_WEBHOOK_SECRET')

	try:
		event = tucuota.Webhook.construct_event(
			payload, timestamp, received_sig, secret
		)
	except ValueError:
		print("Error while decoding event!")
		return "Bad payload", 400
	except tucuota.TuCuotaSignatureVerificationError:
		print("Invalid signature!")
		return "Bad signature", 400

	print(event)

	return "", 200
