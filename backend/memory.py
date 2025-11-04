from typing import List
import json
import pathlib
from datetime import datetime
import os
from botocore.exceptions import ClientError
import boto3


s3_client = boto3.client("s3")
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
memory_dir = pathlib.Path("../memory")

class Memory:
    # Memory storage configuration
    def __init__(self, memory_dir: str = None):
            """Initialize Memory with storage directory"""
            if memory_dir is None:
                memory_dir = os.getenv("MEMORY_DIR", "../memory")
            self.memory_dir = pathlib.Path(memory_dir)
        

    def load_conversation(self,session_id:str, system_prompt:str) -> List[dict]:
        """Load conversation history from storage"""
        if USE_S3:
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
                return json.loads(response["Body"].read().decode("utf-8"))
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    return []
                raise
        else:
            memory_file=self.memory_dir/f"{session_id}.json"
            if not memory_file.exists():
                return [{"role":"system", "content":system_prompt}]
            with open(memory_file, "r") as f:
                return json.load(f)

    def save_conversation(self,session_id:str, messages:List[dict]):

        """Save conversation history to storage"""
        if USE_S3:
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=get_memory_path(session_id),
                Body=json.dumps(messages, indent=2),
                ContentType="application/json",
            )
        else:
            print("Saving Conversations", messages)
            memory_file=self.memory_dir/f"{session_id}.json"
            with open(memory_file, "w") as f:
                json.dump(messages, f)

# Memory management functions
def get_memory_path(session_id: str) -> str:
    return f"{session_id}.json"
