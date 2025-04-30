from time import now

class Info:
    time: int
    message: str
    
    def __init__(self, message: str):
        self.message = message
        self.time = now()