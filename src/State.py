from enums import MessageType
from payloads import Data


class State(dict[MessageType, Data]):
    def __setitem__(self, key: MessageType, value):
        if not isinstance(key, MessageType):
            raise KeyError(f"Invalid key: {key} (must be a valid state)")
        super().__setitem__(key, value)