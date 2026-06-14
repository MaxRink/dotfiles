#!/usr/bin/env python3
"""Persistent mini-REPL for RLM-style workflows in Claude Code.

This script provides a *stateful* Python environment across invocations by
saving a pickle file to disk. It is intentionally small and dependency-free.

Supports two modes:
  - Single-file mode: Traditional init with one context file
  - Multi-file mode: init-dir with directory + glob pattern, preserving file:line citations

Typical flow (single-file):
  1) Initialise context:
       python rlm_repl.py init path/to/context.txt
  2) Execute code repeatedly (state persists):
       python rlm_repl.py exec -c 'print(len(content))'

Typical flow (multi-file):
  1) Initialise from directory:
       python rlm_repl.py init-dir ./script/plsql --pattern "*.sql" --recursive
  2) Check session info:
       python rlm_repl.py sessions
  3) Execute with session state:
       python rlm_repl.py --state .claude/rlm_state/session_xxx/state.pkl exec -c 'print(get_files())'

The script injects these variables into the exec environment:
  - context: dict with keys {path, loaded_at, content}
  - content: string alias for context['content']
  - buffers: list[str] for storing intermediate text results

It also injects helpers:
  - peek(start=0, end=1000) -> str
  - grep(pattern, max_matches=20, window=120, flags=0) -> list[dict]
  - chunk_indices(size=200000, overlap=0) -> list[(start,end)]
  - write_chunks(out_dir, size=200000, overlap=0, prefix='chunk') -> list[str]
  - add_buffer(text: str) -> None
  - file_at_offset(offset) -> dict  # multi-file mode only
  - get_files() -> list[dict]  # multi-file mode only
  - get_session_id() -> str  # multi-file mode only
  - add_partial_result(result: dict) -> None  # for interrupt-safe processing
  - clear_partial_results() -> None  # clear on successful completion

Multi-file mode creates:
  - Session-based state in .claude/rlm_state/session_<id>/
  - chunks_manifest.json with file boundary metadata
  - Chunk files with LINE_OFFSET markers for split files

Security note:
  This runs arbitrary Python via exec. Treat it like running code you wrote.
"""

from __future__ import annotations

import argparse
import atexit
import bisect
import fnmatch
import io
import json
import os
import pickle
import re
import signal
import sys
import textwrap
import time
import traceback
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Global state for interrupt handling
_current_session_state: Optional[Dict[str, Any]] = None
_current_session_path: Optional[Path] = None
_partial_results_buffer: List[Dict[str, Any]] = []
_processing_interrupted: bool = False


DEFAULT_STATE_DIR = Path(".claude/rlm_state")
DEFAULT_STATE_PATH = DEFAULT_STATE_DIR / "state.pkl"
DEFAULT_MAX_OUTPUT_CHARS = 8000
DEFAULT_CHUNK_SIZE = 200_000
DEFAULT_OVERLAP_PCT = 0.1


class RlmReplError(RuntimeError):
    pass


def _save_partial_results() -> None:
    """Save partial results when interrupted.

    Called on SIGINT/SIGTERM or atexit to preserve work done so far.
    Writes to partial_results.json in the session directory.
    """
    global _current_session_state, _current_session_path, _partial_results_buffer, _processing_interrupted

    if _current_session_path is None:
        return

    session_dir = _current_session_path.parent
    partial_file = session_dir / "partial_results.json"

    # Get total chunks info if available
    manifest_path = session_dir / "chunks_manifest.json"
    total_chunks = 0
    if manifest_path.exists():
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                manifest = json.load(f)
                total_chunks = manifest.get("total_chunks", 0)
        except Exception:
            pass

    partial_data = {
        "status": "interrupted",
        "interrupted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": _current_session_state.get("session_id") if _current_session_state else None,
        "completed_findings": len(_partial_results_buffer),
        "total_chunks": total_chunks,
        "partial_findings": _partial_results_buffer,
        "resume_hint": "Use the session state to resume processing from where it stopped",
    }

    try:
        _ensure_parent_dir(partial_file)
        with partial_file.open("w", encoding="utf-8") as f:
            json.dump(partial_data, f, indent=2)
        print(f"\nPartial results saved to: {partial_file}", file=sys.stderr)
    except Exception as e:
        print(f"\nWarning: Could not save partial results: {e}", file=sys.stderr)


def _interrupt_handler(signum: int, frame: Any) -> None:
    """Handle SIGINT/SIGTERM by saving partial results and exiting."""
    global _processing_interrupted
    _processing_interrupted = True

    signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
    print(f"\nReceived {signal_name}, saving partial results...", file=sys.stderr)

    _save_partial_results()
    sys.exit(130 if signum == signal.SIGINT else 143)


def _setup_interrupt_handlers() -> None:
    """Set up signal handlers for graceful interruption."""
    signal.signal(signal.SIGINT, _interrupt_handler)
    signal.signal(signal.SIGTERM, _interrupt_handler)
    atexit.register(_cleanup_on_exit)


def _cleanup_on_exit() -> None:
    """Cleanup handler for normal exit."""
    global _partial_results_buffer
    # Only save if we have partial results and processing was interrupted
    if _processing_interrupted and _partial_results_buffer:
        _save_partial_results()


def add_partial_result(result: Dict[str, Any]) -> None:
    """Add a result to the partial results buffer.

    Called during chunk processing to accumulate results.
    These will be saved if processing is interrupted.
    """
    global _partial_results_buffer
    _partial_results_buffer.append(result)


def set_current_session(state: Dict[str, Any], state_path: Path) -> None:
    """Set the current session for interrupt handling.

    Called at the start of processing to enable partial result saving.
    """
    global _current_session_state, _current_session_path
    _current_session_state = state
    _current_session_path = state_path


def clear_partial_results() -> None:
    """Clear the partial results buffer.

    Called when processing completes successfully.
    """
    global _partial_results_buffer, _processing_interrupted
    _partial_results_buffer = []
    _processing_interrupted = False


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.exists():
        raise RlmReplError(
            f"No state found at {state_path}. Run: python rlm_repl.py init <context_path>"
        )
    with state_path.open("rb") as f:
        state = pickle.load(f)
    if not isinstance(state, dict):
        raise RlmReplError(f"Corrupt state file: {state_path}")
    return state


def _save_state(state: Dict[str, Any], state_path: Path) -> None:
    _ensure_parent_dir(state_path)
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    with tmp_path.open("wb") as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    tmp_path.replace(state_path)


def _read_text_file(path: Path, max_bytes: int | None = None) -> str:
    if not path.exists():
        raise RlmReplError(f"Context file does not exist: {path}")
    data: bytes
    with path.open("rb") as f:
        data = f.read() if max_bytes is None else f.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to a lossy decode that will not crash.
        return data.decode("utf-8", errors="replace")


def _truncate(s: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + f"\n... [truncated to {max_chars} chars] ...\n"


def _is_pickleable(value: Any) -> bool:
    try:
        pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    except Exception:
        return False


def _filter_pickleable(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    kept: Dict[str, Any] = {}
    dropped: List[str] = []
    for k, v in d.items():
        if _is_pickleable(v):
            kept[k] = v
        else:
            dropped.append(k)
    return kept, dropped


def _make_helpers(context_ref: Dict[str, Any], buffers_ref: List[str], state_ref: Optional[Dict[str, Any]] = None):
    # These close over context_ref/buffers_ref so changes persist.
    def peek(start: int = 0, end: int = 1000) -> str:
        content = context_ref.get("content", "")
        return content[start:end]

    def grep(
        pattern: str,
        max_matches: int = 20,
        window: int = 120,
        flags: int = 0,
    ) -> List[Dict[str, Any]]:
        content = context_ref.get("content", "")
        out: List[Dict[str, Any]] = []
        for m in re.finditer(pattern, content, flags):
            start, end = m.span()
            snippet_start = max(0, start - window)
            snippet_end = min(len(content), end + window)
            out.append(
                {
                    "match": m.group(0),
                    "span": (start, end),
                    "snippet": content[snippet_start:snippet_end],
                }
            )
            if len(out) >= max_matches:
                break
        return out

    def chunk_indices(size: int = 200_000, overlap: int = 0) -> List[Tuple[int, int]]:
        if size <= 0:
            raise ValueError("size must be > 0")
        if overlap < 0:
            raise ValueError("overlap must be >= 0")
        if overlap >= size:
            raise ValueError("overlap must be < size")

        content = context_ref.get("content", "")
        n = len(content)
        spans: List[Tuple[int, int]] = []
        step = size - overlap
        for start in range(0, n, step):
            end = min(n, start + size)
            spans.append((start, end))
            if end >= n:
                break
        return spans

    def write_chunks(
        out_dir: str | os.PathLike,
        size: int = 200_000,
        overlap: int = 0,
        prefix: str = "chunk",
        encoding: str = "utf-8",
    ) -> List[str]:
        content = context_ref.get("content", "")
        spans = chunk_indices(size=size, overlap=overlap)
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        paths: List[str] = []
        for i, (s, e) in enumerate(spans):
            p = out_path / f"{prefix}_{i:04d}.txt"
            p.write_text(content[s:e], encoding=encoding)
            paths.append(str(p))
        return paths

    def add_buffer(text: str) -> None:
        buffers_ref.append(str(text))

    def file_at_offset(offset: int) -> Optional[Dict[str, Any]]:
        """Return file info for a character offset (multi-file mode only).

        Returns: {"path": "file.sql", "line": 234} or None
        """
        if state_ref is None:
            return None
        files = state_ref.get("files", [])
        return _file_at_offset(files, offset)

    def get_files() -> List[Dict[str, Any]]:
        """Return list of files in multi-file mode."""
        if state_ref is None:
            return []
        return state_ref.get("files", [])

    def get_session_id() -> Optional[str]:
        """Return current session ID."""
        if state_ref is None:
            return None
        return state_ref.get("session_id")

    return {
        "peek": peek,
        "grep": grep,
        "chunk_indices": chunk_indices,
        "write_chunks": write_chunks,
        "add_buffer": add_buffer,
        "file_at_offset": file_at_offset,
        "get_files": get_files,
        "get_session_id": get_session_id,
        "add_partial_result": add_partial_result,
        "clear_partial_results": clear_partial_results,
    }


def _generate_session_id() -> str:
    """Generate a unique session ID for state isolation."""
    return uuid.uuid4().hex[:12]


def _get_session_state_dir(session_id: str) -> Path:
    """Return the state directory for a session."""
    return DEFAULT_STATE_DIR / f"session_{session_id}"


def _load_exclusions_from_json(json_path: Path) -> List[str]:
    """Load exclusion patterns from a feature-definition.json file.

    Looks for glob patterns in:
    1. scope.exclusion_patterns (array) - preferred
    2. exclusion_patterns (root level array) - fallback

    Returns list of fnmatch-compatible patterns.
    """
    if not json_path.exists():
        return []
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Try scope.exclusion_patterns first (feature-definition.json v2 format)
        scope = data.get("scope", {})
        if isinstance(scope, dict):
            patterns = scope.get("exclusion_patterns", [])
            if isinstance(patterns, list) and patterns:
                return [str(p) for p in patterns if p]

        # Fallback: root level exclusion_patterns
        patterns = data.get("exclusion_patterns", [])
        if isinstance(patterns, list) and patterns:
            return [str(p) for p in patterns if p]

        # Legacy fallback: root level excluded_scope (if it's a list)
        excluded = data.get("excluded_scope", [])
        if isinstance(excluded, list):
            return [str(p) for p in excluded if p]

        return []
    except (json.JSONDecodeError, IOError):
        return []


def _matches_exclusion(path: Path, exclusions: List[str], base_dir: Path) -> bool:
    """Check if a path matches any exclusion pattern."""
    rel_path = str(path.relative_to(base_dir))
    for pattern in exclusions:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def _count_lines(content: str) -> int:
    """Count lines in content."""
    if not content:
        return 0
    return content.count("\n") + (1 if not content.endswith("\n") else 0)


def _build_file_metadata(
    source_dir: Path,
    pattern: str,
    recursive: bool,
    exclusions: List[str],
    max_bytes: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]], str, int]:
    """Scan directory and build file metadata with content.

    Returns: (files_list, skipped_files, combined_content, total_lines)
    """
    files: List[Dict[str, Any]] = []
    skipped: List[Dict[str, str]] = []
    combined_parts: List[str] = []
    current_offset = 0
    total_lines = 0

    # Collect matching files
    if recursive:
        all_files = sorted(source_dir.rglob(pattern))
    else:
        all_files = sorted(source_dir.glob(pattern))

    for file_path in all_files:
        if not file_path.is_file():
            continue

        # Check exclusions
        if _matches_exclusion(file_path, exclusions, source_dir):
            skipped.append({"path": str(file_path), "reason": "excluded by pattern"})
            continue

        # Try to read the file
        try:
            content = _read_text_file(file_path, max_bytes=max_bytes)
        except Exception as e:
            skipped.append({"path": str(file_path), "reason": str(e)})
            continue

        # Check if binary
        if "\x00" in content[:1024]:
            skipped.append({"path": str(file_path), "reason": "binary file detected"})
            continue

        file_lines = _count_lines(content)
        file_size = len(content)

        # Add file marker for context preservation
        marker = f"\n-- FILE_START: {file_path.relative_to(source_dir)}\n"
        end_marker = f"\n-- FILE_END: {file_path.relative_to(source_dir)}\n"

        # Compute line offsets for accurate line attribution
        # line_offsets[i] = byte offset where line i+1 starts (0-indexed array)
        line_offsets = [0]  # Line 1 starts at offset 0
        for pos, char in enumerate(content):
            if char == "\n":
                line_offsets.append(pos + 1)

        # Record file metadata
        files.append({
            "path": str(file_path.relative_to(source_dir)),
            "absolute_path": str(file_path),
            "start_offset": current_offset + len(marker),
            "end_offset": current_offset + len(marker) + file_size,
            "lines": file_lines,
            "size_bytes": file_size,
            "line_offsets": line_offsets,
        })

        combined_parts.append(marker)
        combined_parts.append(content)
        combined_parts.append(end_marker)

        current_offset += len(marker) + file_size + len(end_marker)
        total_lines += file_lines

    combined_content = "".join(combined_parts)
    return files, skipped, combined_content, total_lines


def _file_at_offset(files: List[Dict[str, Any]], offset: int) -> Optional[Dict[str, Any]]:
    """Return file info for a given character offset.

    Uses binary search for O(log n) lookup.
    Returns: {"path": "file.sql", "line": 234} or None
    """
    if not files:
        return None

    # Build sorted list of start offsets for binary search
    starts = [f["start_offset"] for f in files]
    idx = bisect.bisect_right(starts, offset) - 1

    if idx < 0:
        return None

    file_info = files[idx]
    if offset > file_info["end_offset"]:
        return None

    # Calculate line number within file using pre-computed line offsets
    relative_offset = offset - file_info["start_offset"]

    # Use binary search on line_offsets if available
    line_offsets = file_info.get("line_offsets")
    if line_offsets:
        # bisect_right gives the insertion point; -1 gives the line index (0-based)
        # +1 to convert to 1-based line number
        line_idx = bisect.bisect_right(line_offsets, relative_offset) - 1
        line_number = max(1, line_idx + 1)
    else:
        # Fallback: estimate based on average line length (50 chars/line)
        line_number = max(1, int(relative_offset / 50))

    return {
        "path": file_info["path"],
        "line": min(line_number, file_info["lines"]),
        "file_info": file_info,
    }


def _create_multifile_chunks(
    content: str,
    files: List[Dict[str, Any]],
    max_chars: int = DEFAULT_CHUNK_SIZE,
    overlap_pct: float = DEFAULT_OVERLAP_PCT,
) -> List[Dict[str, Any]]:
    """Create chunks with file boundary metadata.

    Returns list of chunk metadata with file attribution.
    """
    chunks: List[Dict[str, Any]] = []
    n = len(content)

    if n == 0:
        return chunks

    overlap = int(max_chars * overlap_pct)
    step = max_chars - overlap

    chunk_idx = 0
    pos = 0

    while pos < n:
        chunk_end = min(n, pos + max_chars)

        # Find which files are in this chunk
        files_in_chunk: List[Dict[str, Any]] = []
        for file_info in files:
            f_start = file_info["start_offset"]
            f_end = file_info["end_offset"]

            # Check for overlap with this chunk
            if f_start < chunk_end and f_end > pos:
                # Calculate line range within the chunk
                chunk_file_start = max(0, pos - f_start)
                chunk_file_end = min(f_end - f_start, chunk_end - f_start)

                # Estimate lines (rough calculation)
                file_size = f_end - f_start
                lines_in_file = file_info["lines"]

                if file_size > 0:
                    start_line = int((chunk_file_start / file_size) * lines_in_file) + 1
                    end_line = int((chunk_file_end / file_size) * lines_in_file)
                else:
                    start_line = 1
                    end_line = 1

                complete = (f_start >= pos and f_end <= chunk_end)

                file_entry = {
                    "path": file_info["path"],
                    "start_line": max(1, start_line),
                    "end_line": max(1, end_line),
                    "complete": complete,
                }

                # Add continuation markers for split files
                if f_start < pos:
                    prev_chunk = f"chunk_{chunk_idx - 1:04d}" if chunk_idx > 0 else None
                    file_entry["continued_from"] = prev_chunk
                if f_end > chunk_end:
                    file_entry["continues_in"] = f"chunk_{chunk_idx + 1:04d}"

                files_in_chunk.append(file_entry)

        chunks.append({
            "chunk_id": f"chunk_{chunk_idx:04d}",
            "char_range": [pos, chunk_end],
            "files_contained": files_in_chunk,
        })

        chunk_idx += 1
        pos += step

        if chunk_end >= n:
            break

    return chunks


def _write_chunks_with_manifest(
    content: str,
    files: List[Dict[str, Any]],
    session_dir: Path,
    session_id: str,
    max_chars: int = DEFAULT_CHUNK_SIZE,
    overlap_pct: float = DEFAULT_OVERLAP_PCT,
) -> Tuple[Path, List[str]]:
    """Write chunks to files and create manifest.

    Returns: (manifest_path, list of chunk file paths)
    """
    chunks_dir = session_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunk_metadata = _create_multifile_chunks(content, files, max_chars, overlap_pct)

    chunk_paths: List[str] = []

    for chunk in chunk_metadata:
        start, end = chunk["char_range"]
        chunk_content = content[start:end]

        # Add LINE_OFFSET markers for split files
        header_lines = []
        for fc in chunk["files_contained"]:
            if fc.get("continued_from"):
                header_lines.append(
                    f"-- CONTINUED_FROM: {fc['continued_from']}\n"
                    f"-- FILE: {fc['path']}\n"
                    f"-- LINE_OFFSET: {fc['start_line']}\n"
                )

        if header_lines:
            chunk_content = "".join(header_lines) + chunk_content

        chunk_file = chunks_dir / f"{chunk['chunk_id']}.txt"
        chunk_file.write_text(chunk_content, encoding="utf-8")
        chunk_paths.append(str(chunk_file))
        chunk["file_path"] = f"chunks/{chunk['chunk_id']}.txt"

    # Write manifest
    manifest = {
        "session_id": session_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_files": len(files),
        "total_chunks": len(chunk_metadata),
        "chunk_size": max_chars,
        "overlap_chars": int(max_chars * overlap_pct),
        "chunks": chunk_metadata,
    }

    manifest_path = session_dir / "chunks_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path, chunk_paths


def cmd_init_dir(args: argparse.Namespace) -> int:
    """Initialize state from a directory of files."""
    source_dir = Path(args.directory).resolve()

    if not source_dir.is_dir():
        raise RlmReplError(f"Not a directory: {source_dir}")

    # Generate session ID for isolation
    session_id = _generate_session_id()
    session_dir = _get_session_state_dir(session_id)
    state_path = session_dir / "state.pkl"

    # Collect exclusions
    exclusions: List[str] = list(args.exclude) if args.exclude else []
    if args.exclude_from:
        exclusions.extend(_load_exclusions_from_json(Path(args.exclude_from)))

    # Build file metadata and combined content
    files, skipped, content, total_lines = _build_file_metadata(
        source_dir=source_dir,
        pattern=args.pattern,
        recursive=args.recursive,
        exclusions=exclusions,
        max_bytes=args.max_bytes,
    )

    if not files:
        raise RlmReplError(
            f"No files found matching pattern '{args.pattern}' in {source_dir}"
        )

    # Create state (version 2 for multi-file mode)
    state: Dict[str, Any] = {
        "version": 2,
        "session_id": session_id,
        "mode": "multi-file",
        "created_at": time.time(),
        "source_dir": str(source_dir),
        "pattern": args.pattern,
        "exclusions": exclusions,
        "files": files,
        "skipped_files": skipped,
        "context": {
            "path": str(source_dir),
            "loaded_at": time.time(),
            "content": content,
            "total_chars": len(content),
            "total_files": len(files),
            "total_lines": total_lines,
        },
        "buffers": [],
        "globals": {},
    }

    _save_state(state, state_path)

    # Write chunks and manifest
    manifest_path, chunk_paths = _write_chunks_with_manifest(
        content=content,
        files=files,
        session_dir=session_dir,
        session_id=session_id,
        max_chars=args.chunk_size,
        overlap_pct=args.overlap_pct,
    )

    print(f"Session ID: {session_id}")
    print(f"State: {state_path}")
    print(f"Source: {source_dir}")
    print(f"Pattern: {args.pattern}")
    print(f"Files loaded: {len(files)}")
    print(f"Files skipped: {len(skipped)}")
    print(f"Total chars: {len(content):,}")
    print(f"Total lines: {total_lines:,}")
    print(f"Chunks created: {len(chunk_paths)}")
    print(f"Manifest: {manifest_path}")

    if skipped:
        print("\nSkipped files:")
        for s in skipped[:5]:
            print(f"  - {s['path']}: {s['reason']}")
        if len(skipped) > 5:
            print(f"  ... and {len(skipped) - 5} more")

    return 0


def cmd_init(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    ctx_path = Path(args.context)

    content = _read_text_file(ctx_path, max_bytes=args.max_bytes)
    state: Dict[str, Any] = {
        "version": 1,
        "context": {
            "path": str(ctx_path),
            "loaded_at": time.time(),
            "content": content,
        },
        "buffers": [],
        "globals": {},
    }
    _save_state(state, state_path)

    print(f"Initialised RLM REPL state at: {state_path}")
    print(f"Loaded context: {ctx_path} ({len(content):,} chars)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state = _load_state(Path(args.state))
    ctx = state.get("context", {})
    content = ctx.get("content", "")
    buffers = state.get("buffers", [])
    g = state.get("globals", {})
    version = state.get("version", 1)
    mode = state.get("mode", "single-file")

    print("RLM REPL status")
    print(f"  State file: {args.state}")
    print(f"  Version: {version}")
    print(f"  Mode: {mode}")

    if version >= 2 and mode == "multi-file":
        session_id = state.get("session_id", "unknown")
        files = state.get("files", [])
        skipped = state.get("skipped_files", [])
        print(f"  Session ID: {session_id}")
        print(f"  Source dir: {state.get('source_dir')}")
        print(f"  Pattern: {state.get('pattern')}")
        print(f"  Files loaded: {len(files)}")
        print(f"  Files skipped: {len(skipped)}")
        print(f"  Total chars: {ctx.get('total_chars', len(content)):,}")
        print(f"  Total lines: {ctx.get('total_lines', 0):,}")
    else:
        print(f"  Context path: {ctx.get('path')}")
        print(f"  Context chars: {len(content):,}")

    print(f"  Buffers: {len(buffers)}")
    print(f"  Persisted vars: {len(g)}")
    if args.show_vars and g:
        for k in sorted(g.keys()):
            print(f"    - {k}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    if state_path.exists():
        state_path.unlink()
        print(f"Deleted state: {state_path}")
    else:
        print(f"No state to delete at: {state_path}")
    return 0


def cmd_sessions(args: argparse.Namespace) -> int:
    """List all RLM sessions."""
    if not DEFAULT_STATE_DIR.exists():
        print("No sessions found")
        return 0

    sessions: List[Dict[str, Any]] = []
    for session_dir in DEFAULT_STATE_DIR.glob("session_*"):
        if not session_dir.is_dir():
            continue
        state_file = session_dir / "state.pkl"
        if not state_file.exists():
            continue
        try:
            state = _load_state(state_file)
            sessions.append({
                "session_id": state.get("session_id", session_dir.name[8:]),
                "mode": state.get("mode", "unknown"),
                "source_dir": state.get("source_dir", "N/A"),
                "pattern": state.get("pattern", "N/A"),
                "files": len(state.get("files", [])),
                "created": state.get("created_at", 0),
                "state_path": str(state_file),
            })
        except Exception:
            continue

    if not sessions:
        print("No sessions found")
        return 0

    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x["created"], reverse=True)

    print(f"Found {len(sessions)} session(s):\n")
    for s in sessions:
        created_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["created"]))
        print(f"  {s['session_id']}")
        print(f"    Mode: {s['mode']}")
        print(f"    Source: {s['source_dir']}")
        print(f"    Pattern: {s['pattern']}")
        print(f"    Files: {s['files']}")
        print(f"    Created: {created_str}")
        print(f"    State: {s['state_path']}")
        print()

    return 0


def cmd_export_buffers(args: argparse.Namespace) -> int:
    state = _load_state(Path(args.state))
    buffers = state.get("buffers", [])
    out_path = Path(args.out)
    _ensure_parent_dir(out_path)
    out_path.write_text("\n\n".join(str(b) for b in buffers), encoding="utf-8")
    print(f"Wrote {len(buffers)} buffers to: {out_path}")
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = _load_state(state_path)

    # Enable interrupt handling for this session
    set_current_session(state, state_path)

    ctx = state.get("context")
    if not isinstance(ctx, dict) or "content" not in ctx:
        raise RlmReplError("State is missing a valid 'context'. Re-run init.")

    buffers = state.setdefault("buffers", [])
    if not isinstance(buffers, list):
        buffers = []
        state["buffers"] = buffers

    persisted = state.setdefault("globals", {})
    if not isinstance(persisted, dict):
        persisted = {}
        state["globals"] = persisted

    code = args.code
    if code is None:
        code = sys.stdin.read()

    # Build execution environment.
    # Start from persisted variables, then inject context, buffers and helpers.
    env: Dict[str, Any] = dict(persisted)
    env["context"] = ctx
    env["content"] = ctx.get("content", "")
    env["buffers"] = buffers

    helpers = _make_helpers(ctx, buffers, state)
    env.update(helpers)

    # Capture output.
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code, env, env)
    except Exception:
        traceback.print_exc(file=stderr_buf)

    # Pull back possibly mutated context/buffers.
    maybe_ctx = env.get("context")
    if isinstance(maybe_ctx, dict) and "content" in maybe_ctx:
        state["context"] = maybe_ctx
        ctx = maybe_ctx

    maybe_buffers = env.get("buffers")
    if isinstance(maybe_buffers, list):
        state["buffers"] = maybe_buffers
        buffers = maybe_buffers

    # Persist any new variables, excluding injected keys.
    injected_keys = {
        "__builtins__",
        "context",
        "content",
        "buffers",
        *helpers.keys(),
    }
    to_persist = {k: v for k, v in env.items() if k not in injected_keys}
    filtered, dropped = _filter_pickleable(to_persist)
    state["globals"] = filtered

    _save_state(state, state_path)

    out = stdout_buf.getvalue()
    err = stderr_buf.getvalue()

    if dropped and args.warn_unpickleable:
        msg = "Dropped unpickleable variables: " + ", ".join(dropped)
        err = (err + ("\n" if err else "") + msg + "\n")

    if out:
        sys.stdout.write(_truncate(out, args.max_output_chars))

    if err:
        sys.stderr.write(_truncate(err, args.max_output_chars))

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rlm_repl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Persistent mini-REPL for RLM-style workflows.

            Examples:
              python rlm_repl.py init context.txt
              python rlm_repl.py status
              python rlm_repl.py exec -c "print(len(content))"
              python rlm_repl.py exec <<'PY'
              print(peek(0, 2000))
              PY
            """
        ),
    )
    p.add_argument(
        "--state",
        default=str(DEFAULT_STATE_PATH),
        help=f"Path to state pickle (default: {DEFAULT_STATE_PATH})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialise state from a context file")
    p_init.add_argument("context", help="Path to the context file")
    p_init.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Optional cap on bytes read from the context file",
    )
    p_init.set_defaults(func=cmd_init)

    # init-dir command for multi-file mode
    p_init_dir = sub.add_parser(
        "init-dir",
        help="Initialise state from a directory of files (multi-file mode)"
    )
    p_init_dir.add_argument("directory", help="Path to the source directory")
    p_init_dir.add_argument(
        "--pattern",
        default="*",
        help="Glob pattern for file matching (default: *)"
    )
    p_init_dir.add_argument(
        "--recursive",
        action="store_true",
        help="Search recursively in subdirectories"
    )
    p_init_dir.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclusion pattern (can be specified multiple times)"
    )
    p_init_dir.add_argument(
        "--exclude-from",
        type=str,
        default=None,
        help="JSON file to load exclusion patterns from (feature-definition.json)"
    )
    p_init_dir.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Characters per chunk (default: {DEFAULT_CHUNK_SIZE})"
    )
    p_init_dir.add_argument(
        "--overlap-pct",
        type=float,
        default=DEFAULT_OVERLAP_PCT,
        help=f"Overlap percentage between chunks (default: {DEFAULT_OVERLAP_PCT})"
    )
    p_init_dir.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Optional cap on bytes per file"
    )
    p_init_dir.set_defaults(func=cmd_init_dir)

    p_status = sub.add_parser("status", help="Show current state summary")
    p_status.add_argument(
        "--show-vars", action="store_true", help="List persisted variable names"
    )
    p_status.set_defaults(func=cmd_status)

    p_reset = sub.add_parser("reset", help="Delete the current state file")
    p_reset.set_defaults(func=cmd_reset)

    p_sessions = sub.add_parser("sessions", help="List all RLM sessions")
    p_sessions.set_defaults(func=cmd_sessions)

    p_export = sub.add_parser(
        "export-buffers", help="Export buffers list to a text file"
    )
    p_export.add_argument("out", help="Output file path")
    p_export.set_defaults(func=cmd_export_buffers)

    p_exec = sub.add_parser("exec", help="Execute Python code with persisted state")
    p_exec.add_argument(
        "-c",
        "--code",
        default=None,
        help="Inline code string. If omitted, reads code from stdin.",
    )
    p_exec.add_argument(
        "--max-output-chars",
        type=int,
        default=DEFAULT_MAX_OUTPUT_CHARS,
        help=f"Truncate stdout/stderr to this many characters (default: {DEFAULT_MAX_OUTPUT_CHARS})",
    )
    p_exec.add_argument(
        "--warn-unpickleable",
        action="store_true",
        help="Warn on stderr when variables could not be persisted",
    )
    p_exec.set_defaults(func=cmd_exec)

    return p


def main(argv: List[str]) -> int:
    # Set up interrupt handlers for graceful shutdown
    _setup_interrupt_handlers()

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except RlmReplError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
