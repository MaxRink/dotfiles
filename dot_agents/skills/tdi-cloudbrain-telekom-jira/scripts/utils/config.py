"""Configuration constants for Telekom Jira integration."""

import os
import sys

# Add core lib to path for cloudbrain_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'lib'))
from cloudbrain_config import get_config_value, get_config_list

# Jira instance configuration
JIRA_URL = "https://jira.telekom.de"

# Allowed projects (configurable via cloudbrain.yaml or JIRA_PROJECTS env var)
_projects = get_config_list("jira", "projects",
                            default=["CAASPROD", "TCAAS", "ONB"],
                            env_var="JIRA_PROJECTS")
ALLOWED_PROJECTS = set(p.upper() for p in _projects)

# Project aliases for user convenience (configurable via cloudbrain.yaml)
_default_aliases = {
    "caas": "CAASPROD",
    "tdi caas": "CAASPROD",
    "tcaas": "TCAAS",
    "converged": "TCAAS",
    "onb": "ONB",
    "onboarding": "ONB",
}
_config_aliases = get_config_value("jira", "aliases", default=None)
PROJECT_ALIASES = _config_aliases if _config_aliases is not None else _default_aliases

# Custom field IDs
CUSTOM_FIELDS = {
    "target_start": "customfield_21920",
    "target_end": "customfield_21921",
    "epic_link": "customfield_17615",
    "epic_name": "customfield_12815",
    "sprint": "customfield_12810",
}

# Default fields to retrieve in searches
DEFAULT_SEARCH_FIELDS = [
    "key",
    "summary",
    "status",
    "assignee",
    "issuetype",
    "created",
    "updated",
    "labels",
    "customfield_21920",  # target_start
    "customfield_21921",  # target_end
]

# Required labels per project (configurable via cloudbrain.yaml)
_default_required_labels = {
    "CAASPROD": {"tdi-caas-operations", "tdi-caas-development"},
}
_config_required_labels = get_config_value("jira", "required_labels", default=None)
if _config_required_labels is not None:
    CAASPROD_REQUIRED_LABELS = set()
    REQUIRED_LABELS_BY_PROJECT = {
        k: set(v) for k, v in _config_required_labels.items()
    }
else:
    CAASPROD_REQUIRED_LABELS = {"tdi-caas-operations", "tdi-caas-development"}
    REQUIRED_LABELS_BY_PROJECT = _default_required_labels

# Environment variable name
ENV_TOKEN = "JIRA_API_TOKEN"
