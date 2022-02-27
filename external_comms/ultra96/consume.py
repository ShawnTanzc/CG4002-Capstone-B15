# consume.py
import pika, os

# import requests module
import requests
import json

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = 'amqp://irbtroao:L4MSsACucAWueNiBrRY5_tqU50agWjFi@armadillo.rmq.cloudamqp.com/irbtroao'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)

channel = connection.channel() # start a channel
channel.queue_declare(queue='hello') # Declare a queue

def callback(ch, method, properties, body):
    payload = json.loads(body)
    print(" [x] Received: {} ".format(payload))

channel.basic_consume(queue='hello',
                      on_message_callback=callback,
                      auto_ack=True)

print(' [*] Waiting for messages:')
channel.start_consuming()
connection.close()