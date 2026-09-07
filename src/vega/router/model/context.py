from time import localtime, struct_time, time


class Context:
    room_id: str
    device_id: str
    init_time: struct_time
    last_push: float | int
    content: str

    def __init__(self, room_id: str, device_id: str, content: str):
        self.room_id = room_id
        self.device_id = device_id
        self.init_time = localtime()
        self.last_push = time()
        self.content = content
