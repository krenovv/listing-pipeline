from datetime import datetime, timedelta


class TimeGenerator:
    def __init__(self, start_datetime: datetime, step_minutes: int = 2):
        self.current = start_datetime.replace(second=0, microsecond=0)
        self.step = timedelta(minutes=step_minutes)

    def next(self) -> str:
        result = self.current.strftime("%Y.%m.%d %H:%M")
        self.current += self.step
        return result

    def set_time(self, new_time: datetime):
        self.current = new_time.replace(second=0, microsecond=0)

    def set_step(self, minutes: int):
        self.step = timedelta(minutes=minutes)