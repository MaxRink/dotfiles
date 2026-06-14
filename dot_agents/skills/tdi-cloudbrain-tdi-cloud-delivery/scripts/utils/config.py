"""
Configuration constants for TDI Cloud Delivery skill.
"""

# GitLab instance
GITLAB_URL = "https://gitlab.devops.telekom.de"

# Primary group for CID operations
CID_GROUP_PATH = "cit-iaas/cid"

# Allowed groups (for validation)
ALLOWED_GROUPS = [
    "cit-iaas/cid",
]

# Default pagination
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

# Date format for display
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# =============================================================================
# COUNTRY AND LOCATION MAPPINGS
# =============================================================================
# Used for filtering epics by country/location. The system matches both:
# - Title patterns (city codes in epic titles, e.g., "skbra" = Bratislava)
# - Label patterns (environment labels, e.g., "E - IC-SK*")
#
# NOTE: Extend CITY_PATTERNS as new location patterns emerge in epic titles.
# =============================================================================

# Country code to full name mapping
COUNTRY_CODES = {
    "AT": "Austria",
    "CZ": "Czechia",
    "DE": "Germany",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "ME": "Montenegro",
    "MK": "North Macedonia",
    "PL": "Poland",
    "RO": "Romania",
    "SK": "Slovakia",
}

# Reverse lookup: name to code (case-insensitive keys built at runtime)
COUNTRY_NAMES = {name.lower(): code for code, name in COUNTRY_CODES.items()}

# City/location patterns found in epic titles (lowercase)
# Format: country_code -> list of title patterns
# These are curated based on observed epic naming conventions.
# Extend as new patterns emerge.
CITY_PATTERNS = {
    "AT": ["atwie", "atvie", "vienna", "wien"],
    "CZ": ["czthp", "czbrn", "czpra", "prague", "praha", "brno", "tmcz"],
    "DE": ["debam", "defra", "bamberg", "frankfurt"],
    "GR": ["grthe", "grsal", "thessaloniki", "salonica"],
    "HR": ["hrzag", "zagreb"],
    "HU": ["hubud", "budapest"],
    "ME": ["mepod", "podgorica"],
    "MK": ["mksko", "skopje"],
    "PL": ["plwar", "plkra", "warsaw", "warszawa", "krakow", "kraków"],
    "RO": ["robuc", "bucharest", "bucuresti"],
    "SK": ["skbra", "skvar", "skkos", "skjak", "bratislava", "varin", "kosice", "košice", "jarovce"],
}

# Environment label prefixes (used with country codes)
ENV_LABEL_PREFIXES = ["IC-", "SC-", "HC-"]

# =============================================================================
# SQUAD LABELS
# =============================================================================
# Squad labels follow the pattern "A - <name>_squad"
# Used for filtering epics by squad assignment.
# =============================================================================

# Default squad label for reports
DEFAULT_SQUAD_LABEL = "A - CDM_squad"

# Valid squad labels mapped to display names
VALID_SQUAD_LABELS = {
    "A - CDM_squad": "CDM Squad",
    "A - CaaS_squad": "CaaS Squad",
    "A - DC_squad": "DC Squad",
    "A - DCIM_squad": "DCIM Squad",
    "A - Networks_squad": "Networks Squad",
    "A - Magellan_squad": "Magellan Squad",
    "A - Monitoring_squad": "Monitoring Squad",
    "A - Onboarding_squad": "Onboarding Squad",
    "A - OBSERVABILITY_squad": "Observability Squad",
    "A - JeePain_squad": "JeePain Squad",
    "A - DEVELOPMENTS_squad": "Developments Squad",
}


def get_squad_display_name(label: str) -> str:
    """
    Get display name for a squad label.

    Args:
        label: Squad label (e.g., "A - CDM_squad")

    Returns:
        Display name (e.g., "CDM Squad") or cleaned label if not found
    """
    if label in VALID_SQUAD_LABELS:
        return VALID_SQUAD_LABELS[label]
    # Fallback: convert "A - Something_squad" to "Something Squad"
    name = label.replace("A - ", "").replace("_squad", " Squad").replace("_", " ")
    return name


def get_country_code(country_input: str) -> str | None:
    """
    Resolve a country input (code or name) to a country code.

    Args:
        country_input: Country code (e.g., "SK") or name (e.g., "Slovakia")

    Returns:
        Country code in uppercase, or None if not found
    """
    upper = country_input.upper()
    if upper in COUNTRY_CODES:
        return upper

    lower = country_input.lower()
    if lower in COUNTRY_NAMES:
        return COUNTRY_NAMES[lower]

    return None


def get_country_patterns(country_code: str) -> list[str]:
    """
    Get title patterns for a country code.

    Args:
        country_code: Two-letter country code (e.g., "SK")

    Returns:
        List of lowercase title patterns
    """
    return CITY_PATTERNS.get(country_code.upper(), [])
