# Implementación de TuCuota en Python


En este ejemplo mostramos cómo agregar pagos y suscripciones a través del checkout de TuCuota.
Más información en nuestra documentación:
https://tucuota.com/docs

Hará falta sacar un token de acceso en https://sandbox.tucuota.com/dashboard/developers y ponerlo como variable de entorno `TC_API_KEY`
Para activar las notificaciones por webhook, en la misma url agregar una dirección webhook y la variable de entorno `TC_API_WEBHOOK_SECRET`

```bash
export TC_API_KEY=........
export TC_API_WEBHOOK_SECRET=....
```


Tarjeta para hacer pruebas en sandbox:
- mastercard
- 5447651834106668

Rutas
- /tucuota/payment
- /tucuota/subscription
- /tucuota/callback
- /tucuota/webhooks (POST)


## Requerimientos
- Python 3
- Flask

## Instalación
`pip install -r requirements.txt`