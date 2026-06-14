"""Configuration constants for Telekom Wiki (Confluence) integration."""

import os
import sys

# Add core lib to path for cloudbrain_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'lib'))
from cloudbrain_config import get_config_list, get_config_value

# Confluence instance configuration
WIKI_URL = "https://wiki.telekom.de"

# Allowed spaces (configurable via cloudbrain.yaml or CONFLUENCE_SPACES env var)
_spaces = get_config_list("confluence", "spaces",
                          default=["CITTEST", "TCAAS"],
                          env_var="CONFLUENCE_SPACES")
ALLOWED_SPACES = set(s.upper() for s in _spaces)

# Default space (configurable via cloudbrain.yaml or CONFLUENCE_DEFAULT_SPACE env var)
DEFAULT_SPACE = get_config_value("confluence", "default_space",
                                 default="CITTEST",
                                 env_var="CONFLUENCE_DEFAULT_SPACE")

# Environment variable names
ENV_USER = "CONFLUENCE_USER"
ENV_TOKEN = "CONFLUENCE_TOKEN"

# Default expand fields for page retrieval
DEFAULT_EXPAND = "body.storage,version,space,ancestors"

# Default limits
DEFAULT_LIMIT = 25
DEFAULT_SEARCH_LIMIT = 25
MAX_DEPTH = 10
