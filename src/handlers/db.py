import os
import json

class DB:

    def __init__(self, db_file_path) -> None:
        self.db_file_path = db_file_path 
        self.data = {'current_id': 1}

        if os.path.isfile(self.db_file_path):
            self._read_db_file()
        else:
            self._save_db_file()

    def shutdown(self):
        self._save_db_file()

    def _read_db_file(self):
        with open(self.db_file_path, 'r') as data_file:
            self.data = json.load(data_file)
        if self.data: return True

    def _save_db_file(self):
        with open(self.db_file_path, "w") as data_file:
            json.dump(self.data, data_file, indent=4)

    def get_record(self, id='all') -> dict:
        if id == 'all':
            return self.data
        return self.data.get(id, None)

    def del_record(self, id = 'all') -> bool:
        if id == 'all':
            self.data = {'current_id': 1}
            result = True
        else:
            result = self.data.pop(id, None)
        self._save_db_file()
        return bool(result)

    def add_record(self, record) -> int:
        self.data[str(self.data['current_id'])] = record
        self.data['current_id'] += 1
        self._save_db_file()
        return self.data['current_id'] - 1

    def update_record(self, id: int, new_data: dict) -> bool:
        if self.data.get(id):
            update_data = {k: v for k, v in new_data.items() if v is not None}
            self.data[id].update(update_data)
        else:
            return False
        self._save_db_file()
        return True
