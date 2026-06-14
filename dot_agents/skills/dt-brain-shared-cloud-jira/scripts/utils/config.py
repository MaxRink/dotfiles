"""Configuration constants for Telekom Jira integration."""

# Jira instance configuration
JIRA_URL = "https://jira.telekom.de"

# Allowed projects (security restriction)
ALLOWED_PROJECTS = {"CAASPROD", "TCAAS", "ONB"}

# Project aliases for user convenience
PROJECT_ALIASES = {
    "caas": "CAASPROD",
    "tdi caas": "CAASPROD",
    "tcaas": "TCAAS",
    "converged": "TCAAS",
    "onb": "ONB",
    "onboarding": "ONB",
}

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

# Required labels for CAASPROD
CAASPROD_REQUIRED_LABELS = {
    "tdi-caas-operations",
    "tdi-caas-development",
}

# Environment variable name
ENV_TOKEN = "JIRA_API_TOKEN"
