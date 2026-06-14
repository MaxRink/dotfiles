"""Configuration constants for Telekom Wiki (Confluence) integration."""

# Confluence instance configuration
WIKI_URL = "https://wiki.telekom.de"

# Allowed spaces (security restriction)
ALLOWED_SPACES = {"CITTEST", "TCAAS", "CITOH", "CKBSH"}

# Default space
DEFAULT_SPACE = "CITTEST"

# Environment variable names
ENV_USER = "CONFLUENCE_USER"
ENV_TOKEN = "CONFLUENCE_TOKEN"

# Default expand fields for page retrieval
DEFAULT_EXPAND = "body.storage,version,space,ancestors"

# Default limits
DEFAULT_LIMIT = 25
DEFAULT_SEARCH_LIMIT = 25
MAX_DEPTH = 10
