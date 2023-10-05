"""Enums used in tse-utils are in the enums module"""
from enum import Enum


class Nsc(Enum):
    """Nsc state of instruments"""
    A = "مجاز"
    AG = "مجاز مسدود"
    AR = "مجاز محفوظ"
    AS = "مجاز متوقف"
    I = "ممنوع"
    IG = "ممنوع مسدود"
    IR = "ممنوع محفوظ"
    IS = "ممنوع متوقف"


class TradeSide(Enum):
    """Trade/Order side"""
    BUY = "خرید"
    SELL = "فروش"


class OrderState(Enum):
    """Trader orders' state"""
    SENT_TO_CORE = "ارسال به هسته"
    ACTIVE = "فعال"
    EXECUTED = "اجرا شده"
    CANCELED = "حذف شده"
    ERROR = "خطا"

    def is_active(self) -> bool:
        """Checks if order is active"""
        return self == OrderState.ACTIVE


class OrderValidityType(Enum):
    """Validity type for trader orders"""
    DAY = "روز"
    GOOD_TILL_CANCEL = "معتبر تا لغو"
    GOOD_TILL_DATE = "معتبر تا تاریخ"
    FILL_OR_KILL = "اجرا و حذف"


class OrderLock(Enum):
    """Trader orders' lock state"""
    UNLOCK = "آزاد"
    LOCK_FOR_CREATION = "قفل برای ایجاد"
    LOCK_FOR_EDITION = "قفل برای ویرایش"
    LOCK_FOR_CANCELATION = "قفل برای حذف"


class TraderConnectionState(Enum):
    """Connection state of trader account"""
    NO_LOGIN = "وارد نشده"
    CONNECTING = "در حال اتصال"
    CONNECTED = "متصل"
    RECONNECTING = "در حال اتصال مجدد"
    CONNECTION_BROKEN = "قطع اتصال"
    LOGGED_OUT = "خارج شده"

    def is_stable(self) -> bool:
        """Checks if connection is in a stable status"""
        return self in (
            TraderConnectionState.NO_LOGIN,
            TraderConnectionState.CONNECTED,
            TraderConnectionState.LOGGED_OUT
        )

    def can_request_connect(self) -> bool:
        """Checks if connection is down and stable"""
        return self in (
            TraderConnectionState.NO_LOGIN,
            TraderConnectionState.LOGGED_OUT
        )
