from datetime import datetime

class Time:
    def __init__(self, time: int = 0):
        time = int(datetime.now().timestamp()) if time == 0 else time
        self.current: int = time

    def format(self, form: str = "%Y年%m月%d日 %H:%M:%S"):
        timestamp = self.current
        if timestamp >= 1000000000000:
            timestamp = int(timestamp / 1000)
        return datetime.fromtimestamp(timestamp).strftime(form)

    def relate(self, time: int = 0) -> str:
        start = int(self.current)
        end = int(time)

        start_timestamp = datetime.fromtimestamp(start)
        end_timestamp = datetime.fromtimestamp(end)

        timedelta = end_timestamp - start_timestamp
        total_seconds = abs(int(timedelta.total_seconds()))

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        days = f"{days:02}"
        hours = f"{hours:02}"
        minutes = f"{minutes:02}"

        if start >= end:
            flag = "前"
        else:
            flag = "后"
        relateTime = f"{days}天{hours}时{minutes}分{flag}"
        return relateTime
