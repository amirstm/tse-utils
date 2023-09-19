from enum import Enum

class Nsc(Enum):
    A = "مجاز"
    AG = "مجاز مسدود"
    AR = "مجاز محفوظ"
    AS = "مجاز متوقف"
    I = "ممنوع"
    IG = "ممنوع مسدود"
    IR = "ممنوع محفوظ"
    IS = "ممنوع متوقف"

class TradeSide(Enum):
    BUY = "خرید"
    SELL = "فروش"

class OrderState(Enum):
    SENT_TO_CORE = "ارسال به هسته"
    ACTIVE = "فعال"
    EXECUTED = "اجرا شده"
    CANCELED = "حذف شده"
    ERROR = "خطا"

    def is_active(self) -> bool:
        return self == OrderState.ACTIVE
    
class OrderValidity(Enum):
    DAY = "روز"
    GOOD_TILL_CANCEL = "معتبر تا لغو"
    GOOD_TILL_DATE = "معتبر تا تاریخ"
    FILL_OR_KILL = "اجرا و حذف"

class OrderLock(Enum):
    UNLOCK = "آزاد"
    LOCK_FOR_CREATION = "قفل برای ایجاد"
    LOCK_FOR_EDITION = "قفل برای ویرایش"
    LOCK_FOR_CANCELATION = "قفل برای حذف"

class TraderTokenType(Enum):
    ONLINE = "آنلاین"
    API = "API"

class TraderConnectionState(Enum):
    NO_LOGIN = "وارد نشده"
    CONNECTING = "در حال اتصال"
    CONNECTED = "متصل"
    RECONNECTING = "در حال اتصال مجدد"
    CONNECTION_BROKEN = "قطع اتصال"
    LOGGED_OUT = "خارج شده"

    def is_stable(self) -> bool:
        return self == TraderConnectionState.NO_LOGIN or self == TraderConnectionState.CONNECTED or self == TraderConnectionState.LOGGED_OUT
    
    def can_request_connect(self) -> bool:
        return self == TraderConnectionState.NO_LOGIN or self == TraderConnectionState.LOGGED_OUT
