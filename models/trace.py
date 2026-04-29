from typing import List, Dict

class TraceLog:
    def __init__(self):
        self.steps = []

    def add(self, stage: str, data: Dict):
        self.steps.append({
            "stage": stage,
            "output": data
        })

    def get_trace(self):
        return self.steps