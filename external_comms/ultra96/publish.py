# publish.py
import pika, os
import ssl
import json

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = 'INSERT URL'
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel

#channel.exchange_declare('test_exchange')
channel.queue_declare(queue='hello') # Declare a queue
# channel.queue_bind('test_queue', 'test_exchange', 'tests')

payload= [{
    "player_type": 1,
    "player_hp": 100,
    "player_shield_hp": 0,
    "is_shielded": False,
    "player_shield_count": 3,
    "player_grenade": 3,
    "player_ammo": 6,
    "player_kill_count": 0
},
    {
        "player_type": 2,
        "player_hp": 100,
        "player_shield_hp": 0,
        "is_shielded": False,
        "player_shield_count": 3,
        "player_grenade": 3,
        "player_ammo": 6,
        "player_kill_count": 0
    }]

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=json.dumps(payload))


print(" [x] Sent: {}".format(json.dumps((payload))))
channel.close()
connection.close()