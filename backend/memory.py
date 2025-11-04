from typing import List
import json
import pathlib
from datetime import datetime

class Memory:

    memory_dir = pathlib.Path("../memory")

    def load_conversation(self,session_id:str, system_prompt:str) -> List[dict]:
        memory_file=self.memory_dir/f"{session_id}.json"
        if not memory_file.exists():
            return [{"role":"system", "content":system_prompt}]
        with open(memory_file, "r") as f:
            return json.load(f)

    def save_conversation(self,session_id:str, messages:List[dict]):
        print("Saving Conversations", messages)
        memory_file=self.memory_dir/f"{session_id}.json"
        with open(memory_file, "w") as f:
            json.dump(messages, f)


