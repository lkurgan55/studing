from kafka import KafkaConsumer

consumer = KafkaConsumer('lab_4', bootstrap_servers='localhost:9092')
file_pattern = "_output.txt"

for msg in consumer:
    file_name = msg.key.decode().split('.')[0] + file_pattern
    with open(file_name, 'a') as file:
        print({'partiotion': msg.partition, 'key': msg.key.decode(), 'value': msg.value.decode()})
        file.write(msg.value.decode())

