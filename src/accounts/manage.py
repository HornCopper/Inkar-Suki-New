from typing import Any, Literal
from pydantic import BaseModel
from datetime import datetime, timedelta

from src.utils.database import db
from src.utils.database.classes import Account
from src.utils.time import Time

import random

class CheckinRewards(BaseModel):
    total_days: int # 累计签到
    is_lucky: bool # 是否触发额外奖励
    coin: int # 签到获得的金币（包含额外）
    lucky_value: int # 幸运值

class AccountManage:
    def __init__(self, user_id: int | str):
        self.data: Account | Any = db.where_one(Account(), "user_id = ?", int(user_id), default=Account(user_id=int(user_id)))
    
    @property
    def checkin_counts(self) -> int:
        return self.data.checkin_counts

    @property
    def permission(self) -> int:
        return self.data.permission
    
    @property
    def coins(self) -> int:
        return self.data.coins
    
    @property
    def checkin_status(self) -> bool:
        """判断上次签到时间是否在当前周期内"""
        current_time = datetime.now()
        today_7_am = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
        if current_time < today_7_am:
            period_start = today_7_am - timedelta(days=1)
            period_end = today_7_am
        else:
            period_start = today_7_am
            period_end = today_7_am + timedelta(days=1)
        last_checkin_time = datetime.fromtimestamp(self.data.last_checkin)
        return period_start <= last_checkin_time < period_end

    def checkin(self) -> Literal[False] | CheckinRewards:
        if self.checkin_status:
            return False
        coin = random.randint(0, 4000)
        lucky = True if random.randint(0, 100) % 25 == 0 else False
        if lucky:
            coin += 10000
        self.add_coin(coin)
        self.add_checkin_counts(1)
        self._update_last_checkin()
        return CheckinRewards(
            total_days = self.checkin_counts + 1,
            is_lucky = lucky,
            coin = coin,
            lucky_value = random.randint(0, 100)
        )
        
    
    def add_coin(self, counts: int) -> None:
        final_coins = self.coins + counts
        instance = self.data
        instance.coins = final_coins
        db.save(instance)

    def reduce_coin(self, counts: int) -> None:
        final_coins = self.coins - counts
        if final_coins < 0:
            final_coins = 0
        instance = self.data
        instance.coins = final_coins
        db.save(instance)

    def add_checkin_counts(self, counts: int) -> None:
        final_days = self.checkin_counts + counts
        instance = self.data
        instance.checkin_counts = final_days
        db.save(instance)

    def _update_last_checkin(self):
        current_time = Time().raw_time
        instance = self.data
        instance.last_checkin = current_time
        db.save(instance)