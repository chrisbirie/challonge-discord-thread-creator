"""Constants and default values for tourney_threads configuration."""

# Challonge API constants
DEFAULT_API_BASE_URL = "https://api.challonge.com/v2.1"
DEFAULT_TOKEN_URL = "https://api.challonge.com/oauth/token"
DEFAULT_PATH_SUFFIX = ".json"

# Default templates for thread creation
DEFAULT_THREAD_NAME_TEMPLATE = "{round_label}: {p1_name} vs {p2_name}"
DEFAULT_MESSAGE_TEMPLATE = (
    "Hi {p1_mention} vs {p2_mention}! {role_mentions}\n"
    "This is your scheduling thread for {round_label}."
)

# Discord configuration defaults
DEFAULT_THREAD_ARCHIVE_MINUTES = 10080  # 7 days
MAX_THREAD_NAME_LENGTH = 100

# Default pagination
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 25
