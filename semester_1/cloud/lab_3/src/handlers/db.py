import json
import boto3	


class DB:

    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name: str, db_file: str) -> None:
        self.bucket_name = bucket_name	
        self.db_file = db_file

        self.s3 = boto3.resource(
            's3',	
            aws_access_key_id=aws_access_key_id,	
            aws_secret_access_key=aws_secret_access_key
        )
        self.s3object = self.s3.Object(self.bucket_name, self.db_file)
        if self._check_file_exist():
            self._get_file()
        else:
            self.data = {'current_id': 1}
            self._save_db_file()

    def _check_file_exist(self) -> bool:	
        return self.db_file in {file_obj.key for file_obj in self.s3.Bucket(self.bucket_name).objects.all()}

    def _get_file(self):	
        self.data = json.loads(self.s3object.get()['Body'].read().decode('utf-8')) 

    def _save_db_file(self):	
        self.s3object.put(Body=(bytes(json.dumps(self.data, indent=4).encode('UTF-8'))))

    def shutdown(self):
        self._save_db_file()

    def get_record(self, id = None) -> dict:
        self._get_file()
        if id is None:
            print(self.data)
            return [{k: v} for k, v in self.data.items() if k != 'current_id']
        return [{id: self.data.get(id, None)}]

    def del_record(self, id = None) -> bool:
        self._get_file()
        if id is None:
            self.data = {'current_id': 1}
            result = True
        else:
            result = self.data.pop(id, None)
        self._save_db_file()
        return bool(result)

    def add_record(self, record) -> int:
        self._get_file()
        self.data[str(self.data['current_id'])] = record
        self.data['current_id'] += 1
        self._save_db_file()
        return self.data['current_id'] - 1

    def update_record(self, id: int, new_data: dict) -> bool:
        self._get_file()
        if self.data.get(id):
            update_data = {k: v for k, v in new_data.items() if v is not None}
            self.data[id].update(update_data)
        else:
            return False
        self._save_db_file()
        return True
