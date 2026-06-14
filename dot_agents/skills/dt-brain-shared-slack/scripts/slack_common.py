#!/usr/bin/env python3
"""
Slack Common Module
Shared utilities and API client for Slack scripts.
"""

import os
import sys
import json
import re
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print("Error: slack_sdk not installed", file=sys.stderr)
    print("Install with: pip install slack_sdk", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def error_exit(msg: str, code: int = 1):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def output_json(data: Any):
    print(json.dumps(data, indent=2, default=str))


def parse_relative_time(spec: str) -> datetime:
    """Parse relative time like '1h', '30m', '2d', '1w' into a datetime."""
    m = re.match(r'^(\d+)([mhdw])$', spec.strip())
    if not m:
        raise ValueError(f"Invalid relative time: {spec}. Use e.g. 1h, 30m, 2d, 1w")
    val, unit = int(m.group(1)), m.group(2)
    delta = {'m': timedelta(minutes=val), 'h': timedelta(hours=val),
             'd': timedelta(days=val), 'w': timedelta(weeks=val)}[unit]
    return datetime.now(timezone.utc) - delta


def parse_time(spec: str) -> datetime:
    """Parse time spec — either relative (1h, 2d) or ISO 8601."""
    if not spec:
        return datetime.now(timezone.utc)
    if re.match(r'^\d+[mhdw]$', spec.strip()):
        return parse_relative_time(spec)
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            dt = datetime.strptime(spec, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Cannot parse time: {spec}")


def ts_to_datetime(ts: str) -> datetime:
    """Convert Slack timestamp (epoch.micro) to datetime."""
    return datetime.fromtimestamp(float(ts), tz=timezone.utc)


def datetime_to_ts(dt: datetime) -> str:
    """Convert datetime to Slack timestamp string."""
    return str(dt.timestamp())


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')


def truncate(text: str, length: int = 120) -> str:
    text = text.replace('\n', ' ').strip()
    return text[:length] + '…' if len(text) > length else text


# ---------------------------------------------------------------------------
# Slack Client
# ---------------------------------------------------------------------------

class SlackClient:
    """Wrapper around slack_sdk.WebClient with caching and helpers."""

    def __init__(self, bot_token: Optional[str] = None, user_token: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get('SLACK_BOT_TOKEN')
        self.user_token = user_token or os.environ.get('SLACK_BOT_USER_TOKEN')

        if not self.bot_token:
            error_exit("SLACK_BOT_TOKEN not set. Run: source .env")

        self.bot = WebClient(token=self.bot_token)
        self.user = WebClient(token=self.user_token) if self.user_token else None

        # Caches
        self._channels: Optional[List[Dict]] = None
        self._users: Dict[str, str] = {}  # id -> display name

    # ---- rate-limit aware wrapper ------------------------------------

    @staticmethod
    def _call(client: WebClient, method: str, **kwargs) -> Any:
        """Call a Slack API method with automatic retry on rate-limit."""
        fn = getattr(client, method)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return fn(**kwargs)
            except SlackApiError as e:
                if e.response.status_code == 429:
                    headers = e.response.headers or {}
                    delay = int(headers.get('Retry-After',
                                headers.get('retry-after', 10)))
                    print(f"Rate limited, waiting {delay}s (attempt {attempt + 1}/{max_retries}) …",
                          file=sys.stderr)
                    time.sleep(delay + 1)
                    continue
                raise
        error_exit(f"Rate limited after {max_retries} retries")

    def bot_call(self, method: str, **kwargs) -> Any:
        return self._call(self.bot, method, **kwargs)

    def user_call(self, method: str, **kwargs) -> Any:
        if not self.user:
            error_exit("SLACK_BOT_USER_TOKEN not set — search requires a user token")
        return self._call(self.user, method, **kwargs)

    # ---- channels ----------------------------------------------------

    def _looks_like_channel_id(self, value: str) -> bool:
        """Check if a string looks like a Slack channel ID (C..., G..., D...)."""
        return bool(value) and value[0] in ('C', 'G', 'D') and len(value) >= 9

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get channel info directly by ID using conversations.info (fast)."""
        try:
            resp = self.bot_call('conversations_info', channel=channel_id)
            return resp.get('channel')
        except SlackApiError:
            return None

    def get_member_channels(self, types: str = 'public_channel,private_channel') -> List[Dict]:
        """List only channels the bot is a member of (fast).

        Uses users.conversations which returns only the bot's own
        memberships — typically a single API call.
        """
        channels = []
        cursor = None
        while True:
            kwargs: Dict[str, Any] = {
                'types': types,
                'exclude_archived': True,
                'limit': 1000,
            }
            if cursor:
                kwargs['cursor'] = cursor
            resp = self.bot_call('users_conversations', **kwargs)
            channels.extend(resp.get('channels', []))
            cursor = resp.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break
        return channels

    def get_channels(self, force: bool = False) -> List[Dict]:
        """List channels visible to the bot (cached).

        WARNING: This paginates through the entire workspace and can be
        very slow on large Slack instances.  Prefer resolve_channel() or
        get_channel_info() for single-channel lookups.
        """
        if self._channels is not None and not force:
            return self._channels

        channels = []
        cursor = None
        page = 0
        while True:
            kwargs: Dict[str, Any] = {
                'types': 'public_channel,private_channel',
                'exclude_archived': True,
                'limit': 200,
            }
            if cursor:
                kwargs['cursor'] = cursor
            if page > 0:
                time.sleep(1)
            resp = self.bot_call('conversations_list', **kwargs)
            channels.extend(resp['channels'])
            cursor = resp.get('response_metadata', {}).get('next_cursor')
            page += 1
            if not cursor:
                break

        self._channels = channels
        return channels

    def find_channel(self, name: str) -> Optional[Dict]:
        """Find a channel by exact name.

        Fast path via users.conversations (bot memberships only).
        Falls back to full workspace pagination only if needed.
        """
        # Fast path: check bot's own memberships (single API call)
        for ch in self.get_member_channels():
            if ch['name'] == name:
                return ch

        # Slow fallback: full workspace pagination
        for ch in self.get_channels():
            if ch['name'] == name:
                return ch
        return None

    def resolve_channel(self, name_or_id: str) -> Tuple[str, str]:
        """Return (channel_id, channel_name) from a name or ID.

        Uses conversations.info for ID lookups (single API call) instead
        of paginating through the entire workspace.
        """
        name_or_id = name_or_id.lstrip('#')

        # Fast path: direct ID lookup via conversations.info
        if self._looks_like_channel_id(name_or_id):
            info = self.get_channel_info(name_or_id)
            if info:
                return info['id'], info.get('name', name_or_id)
            return name_or_id, name_or_id

        # Name lookup
        ch = self.find_channel(name_or_id)
        if ch:
            return ch['id'], ch['name']
        error_exit(f"Channel not found: {name_or_id}")

    # ---- users -------------------------------------------------------

    def resolve_user(self, user_id: str) -> str:
        """Resolve user ID to display name (cached)."""
        if user_id in self._users:
            return self._users[user_id]
        try:
            resp = self.bot_call('users_info', user=user_id)
            user = resp['user']
            name = user.get('real_name') or user.get('name') or user_id
            self._users[user_id] = name
            return name
        except SlackApiError:
            self._users[user_id] = user_id
            return user_id

    def resolve_users_bulk(self, user_ids: List[str]) -> Dict[str, str]:
        """Resolve multiple user IDs."""
        for uid in set(user_ids):
            if uid not in self._users:
                self.resolve_user(uid)
        return {uid: self._users.get(uid, uid) for uid in user_ids}

    # ---- history -----------------------------------------------------

    def get_history(self, channel_id: str, oldest: Optional[datetime] = None,
                    latest: Optional[datetime] = None, limit: int = 200,
                    include_threads: bool = False) -> List[Dict]:
        """Fetch channel history within a time range."""
        messages = []
        cursor = None
        kwargs: Dict[str, Any] = {'channel': channel_id, 'limit': min(limit, 200)}
        if oldest:
            kwargs['oldest'] = datetime_to_ts(oldest)
        if latest:
            kwargs['latest'] = datetime_to_ts(latest)

        remaining = limit
        page = 0
        while remaining > 0:
            kwargs['limit'] = min(remaining, 200)
            if cursor:
                kwargs['cursor'] = cursor
            if page > 0:
                time.sleep(1)
            try:
                resp = self.bot_call('conversations_history', **kwargs)
            except SlackApiError as e:
                err = e.response.get('error', '')
                if err == 'not_in_channel':
                    # Try to join the channel first
                    try:
                        self.bot_call('conversations_join', channel=channel_id)
                        print("Joined channel, retrying …", file=sys.stderr)
                        resp = self.bot_call('conversations_history', **kwargs)
                    except SlackApiError:
                        error_exit(f"Cannot read channel {channel_id}: bot is not a member and cannot join")
                else:
                    raise
            batch = resp.get('messages', [])
            messages.extend(batch)
            remaining -= len(batch)
            page += 1
            cursor = resp.get('response_metadata', {}).get('next_cursor')
            if not cursor or not batch:
                break

        if include_threads:
            messages = self._expand_threads(channel_id, messages)

        return messages

    def _expand_threads(self, channel_id: str, messages: List[Dict]) -> List[Dict]:
        """Fetch thread replies for messages that have them."""
        expanded = []
        for msg in messages:
            expanded.append(msg)
            if msg.get('reply_count', 0) > 0 and msg.get('ts'):
                try:
                    resp = self.bot_call('conversations_replies',
                                         channel=channel_id, ts=msg['ts'], limit=100)
                    replies = resp.get('messages', [])[1:]  # skip parent
                    for r in replies:
                        r['_is_thread_reply'] = True
                        r['_parent_ts'] = msg['ts']
                    expanded.extend(replies)
                except SlackApiError:
                    pass
        return expanded

    # ---- search (user token) -----------------------------------------

    def search_messages(self, query: str, sort: str = 'timestamp',
                        sort_dir: str = 'desc', count: int = 50,
                        page: int = 1) -> Dict:
        """Search messages using user token."""
        resp = self.user_call('search_messages',
                              query=query, sort=sort, sort_dir=sort_dir,
                              count=count, page=page)
        return resp.get('messages', {})

    # ---- formatting --------------------------------------------------

    def format_message(self, msg: Dict, show_channel: bool = False) -> str:
        """Format a message for display."""
        user = msg.get('user', msg.get('username', 'unknown'))
        if user and not user.startswith('B'):  # skip bots by ID
            user = self.resolve_user(user)
        ts = ts_to_datetime(msg['ts'])
        text = truncate(msg.get('text', ''))
        prefix = ''
        if msg.get('_is_thread_reply'):
            prefix = '  ↳ '
        if show_channel:
            ch = msg.get('channel', {})
            ch_name = ch.get('name', ch) if isinstance(ch, dict) else ch
            return f"{prefix}[{format_datetime(ts)}] #{ch_name} | {user}: {text}"
        return f"{prefix}[{format_datetime(ts)}] {user}: {text}"
