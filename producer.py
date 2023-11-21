from kafka import KafkaProducer
import time

def send_to_kafka(topic, file_name,  message):
    producer.send(topic, key=bytes(f'{file_name}'.encode('utf-8')), value=message)
    producer.flush()

file_path = 'test_data.txt'
kafka_topic = 'lab_4'

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

with open(file_path, 'r') as file:
    for line in file:
        send_to_kafka(kafka_topic, file_path, line.encode('utf-8'))
        time.sleep(5)
        print("line was sent")