import json
import sys

record = [{
    'id': 2147483647,
    'name': ' '*50,
    'category': ' '*50,
    'amount': 1E+37,
    'description': ' '*255,
}]

record = json.dumps({'id': 2147483647})

print(f'Size = {sys.getsizeof(record)}')