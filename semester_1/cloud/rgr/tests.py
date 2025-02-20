curl -X 'POST' 'http://3.83.64.120/crud/record?name=test&category=food&amout=15&description=test%201%20test%202'  
curl -X 'GET' 'http://3.83.64.120/crud/record'

[{"id":1,"name":"test","category":"food","amout":15.0,"description":"test 1 test 2"},{"id":2,"name":"test","category":"food","amout":15.0,"description":"test 1 test 2"}]

curl -X 'GET' 'http://3.83.64.120/crud/record?record_id=2'

[{"id":2,"name":"test","category":"food","amout":15.0,"description":"test 1 test 2"}]

curl -X 'DELETE' 'http://3.83.64.120/crud/record?record_id=1'

curl -X 'PUT' 'http://3.83.64.120/crud/record?record_id=2&name=test2&category=bills&amout=500'

curl -X 'DELETE' 'http://3.83.64.120/crud/record'