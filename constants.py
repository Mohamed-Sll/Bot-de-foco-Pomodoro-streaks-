from typing import Final 

SESSION_ACTIVE: Final[str] = 'active'
SESSION_COMPLETED: Final[str] = 'completed'
SESSION_CANCELLED: Final[str] = 'cancelled'

SESSION_TYPE_FOCUS: Final[str] = 'focus'
SESSION_TYPE_BREAK: Final[str] = 'break'

DEFAULT_FOCUS_MINUTES: Final[int] = 25
DEFAULT_BREAK_MINUTES: Final[int] = 5
DEFAULT_LONG_BREAK_MINUTES: Final[int] = 15

# Alias for the short/regular break used across the codebase
DEFAULT_SHORT_BREAK_MINUTES: Final[int] = DEFAULT_BREAK_MINUTES

POMODORO_BEFORE_LONG_BREAK: Final[int] = 4

MIN_MINUTES_TO_COUNT_FOR_STREAK: Final[int] = 10


MSG_SESSION_STARTED: Final[str] = "🎯 Foco iniciado. Vemo-nos daqui a {minutes} min."
MSG_SESSION_COMPLETED: Final[str] = "✅ Sessão de {minutes} min concluída. Bom trabalho!"
MSG_SESSION_CANCELLED: Final[str] = "❌ Sessão cancelada. Não conta para o streak."
MSG_STREAK_UPDATE: Final[str] = "🔥 Streak: {days} dias seguidos"


CALLBACK_NEW_FOCUS: Final[str] = "new_focus"
CALLBACK_NEW_BREAK: Final[str] = "new_break"
CALLBACK_CANCEL_SESSION: Final[str] = "cancel_session"