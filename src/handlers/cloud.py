import boto3	
import os	


class Cloud:	
    def __init__(self, bucket_name: str) -> None:	
        self.bucket_name = bucket_name	
        self.client = boto3.client(	
            's3',	
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],	
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )	

    def check_file_exist(self, file_name) -> bool:	
        results = self.client.list_objects(	
            Bucket=self.bucket_name, 	
            Prefix=file_name	
        )	

        return 'Contents' in results	

    def get_file(self, file_name):	
        self.client.download_file(
            self.bucket_name,
            file_name,
            f"/{file_name}"
        )

    def save_file(self, file_name):	
        self.client.upload_file(	
            f"/{file_name}"	,	
            self.bucket_name,	
            file_name	
        )