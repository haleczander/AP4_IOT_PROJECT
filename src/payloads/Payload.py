from Data import Data
from State import State


class Payload(State):
    def __init__(self):
        super().__init__()

    def add(self, value: Data):
        self.__setitem__(value.key, value)