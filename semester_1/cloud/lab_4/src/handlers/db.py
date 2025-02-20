import json
import sqlalchemy
from sqlalchemy import text, select, insert, delete, update, \
Table, Column, Integer, String, Float, MetaData

class DB:

    def __init__(self, db_url: str) -> None:
        self.engine = sqlalchemy.create_engine(url=db_url, echo=True)
        self.connection = self.engine.connect()
        metadata_obj = MetaData()
        self.table_name = 'records'
        self.table = Table(
            "records",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(30)),
            Column("category", String),
            Column("amout", Float),
            Column("description", String)
        )
        self._check_table_exist()

    def _check_table_exist(self) -> bool:
        sql_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                id              SERIAL      	PRIMARY KEY,
                name            VARCHAR(50)     NULL,
                category        VARCHAR(50)     NULL,
                amout           REAL            NULL, 
                description     VARCHAR(255)    NULL
            );"""
        self.connection.execute(text(sql_query))
        self.connection.commit()

    def shutdown(self):
        pass

    def get_record(self, id = None) -> dict:
        if id is None:
            query = select(self.table)
        else:        
            query = select(self.table).where(self.table.c.id == int(id))
        result = self.connection.execute(query)

        return [row for row in list(result.mappings().all())]

    def del_record(self, id = None) -> bool:
        if id is None:
            query = text(f"TRUNCATE TABLE {self.table_name}")
        else:        
            query = delete(self.table).where(self.table.c.id == int(id))
        
        self.connection.execute(query)
        self.connection.commit()

    def add_record(self, record) -> int:
        query = insert(self.table).values(
            **record
        )
        self.connection.execute(query)
        self.connection.commit()

    def update_record(self, id: int, new_data: dict) -> bool:
        query = update(self.table).where(self.table.c.id == id).values(**{k:v for k,v in new_data.items() if v is not None})
        self.connection.execute(query)
        self.connection.commit()
