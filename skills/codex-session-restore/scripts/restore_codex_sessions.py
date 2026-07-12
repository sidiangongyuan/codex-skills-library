#!/usr/bin/env python3
"""Scan and repair Codex Desktop session metadata.

Dry-run is the default. Writes require --apply, and bulk apply also requires
--yes. The script intentionally ignores archived sessions unless explicitly
requested.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STALE_TURN_REASON = "session_restore_stale_open_turn"
EDGE_CLOSED_STATUS = "closed"
GOAL_DONE_STATUS = "complete"


@dataclass(frozen=True)
class ThreadRow:
    id: str
    rollout_path: Path
    archived: bool
    model_provider: str
    title: str
    updated_at: int
    cwd: str


@dataclass
class TurnInfo:
    turn_id: str
    first_line: int
    last_context_line: int
    context_count: int = 0
    closed: bool = False
    close_type: str | None = None
    close_line: int | None = None


@dataclass
class RolloutInfo:
    path: Path
    exists: bool
    parse_errors: list[tuple[int, str]] = field(default_factory=list)
    session_provider: str | None = None
    session_id: str | None = None
    legacy_turn_contexts: int = 0
    turns: dict[str, TurnInfo] = field(default_factory=dict)
    turn_order: list[str] = field(default_factory=list)
    context_lines: list[tuple[int, str | None]] = field(default_factory=list)
    line_count: int = 0

    @property
    def open_turns(self) -> list[TurnInfo]:
        return [self.turns[tid] for tid in self.turn_order if not self.turns[tid].closed]


@dataclass
class EdgeRow:
    parent_thread_id: str
    child_thread_id: str
    status: str


@dataclass
class GoalRow:
    thread_id: str
    goal_id: str
    objective: str
    status: str
    updated_at_ms: int


@dataclass
class ScanResult:
    codex_home: Path
    provider: str
    threads: list[ThreadRow]
    active_threads: list[ThreadRow]
    archived_threads: list[ThreadRow]
    rollouts: dict[str, RolloutInfo]
    provider_mismatch_threads: list[ThreadRow]
    meta_provider_mismatches: list[tuple[ThreadRow, str | None]]
    missing_rollouts: list[ThreadRow]
    parse_bad_rollouts: list[tuple[ThreadRow, list[tuple[int, str]]]]
    stale_open_turns: list[tuple[ThreadRow, TurnInfo]]
    recent_open_turns: list[tuple[ThreadRow, TurnInfo]]
    open_edges: list[EdgeRow]
    edge_close_direct: list[tuple[EdgeRow, ThreadRow]]
    edge_need_child_abort: list[tuple[EdgeRow, ThreadRow, list[TurnInfo]]]
    edge_missing_child: list[EdgeRow]
    goals: list[GoalRow]
    stale_goals: list[GoalRow]
    provider_counts: Counter[str]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def backup_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def epoch_seconds() -> int:
    return int(time.time())


def codex_home_from_args(args: argparse.Namespace) -> Path:
    return Path(args.codex_home).expanduser().resolve()


def open_db(path: Path, *, readonly: bool) -> sqlite3.Connection:
    if readonly:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=30)
    else:
        conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_threads(codex_home: Path, include_archived: bool) -> list[ThreadRow]:
    db = open_db(codex_home / "state_5.sqlite", readonly=True)
    try:
        query = "select id, rollout_path, archived, model_provider, title, updated_at, cwd from threads"
        if not include_archived:
            query += " where archived = 0"
        rows = db.execute(query).fetchall()
    finally:
        db.close()
    return [
        ThreadRow(
            id=row["id"],
            rollout_path=Path(row["rollout_path"]),
            archived=bool(row["archived"]),
            model_provider=row["model_provider"],
            title=row["title"] or "",
            updated_at=int(row["updated_at"]),
            cwd=row["cwd"] or "",
        )
        for row in rows
    ]


def fetch_all_threads(codex_home: Path) -> list[ThreadRow]:
    return fetch_threads(codex_home, include_archived=True)


def fetch_edges(codex_home: Path) -> list[EdgeRow]:
    db = open_db(codex_home / "state_5.sqlite", readonly=True)
    try:
        rows = db.execute(
            "select parent_thread_id, child_thread_id, status from thread_spawn_edges"
        ).fetchall()
    finally:
        db.close()
    return [
        EdgeRow(
            parent_thread_id=row["parent_thread_id"],
            child_thread_id=row["child_thread_id"],
            status=row["status"],
        )
        for row in rows
    ]


def fetch_goals(codex_home: Path) -> list[GoalRow]:
    path = codex_home / "goals_1.sqlite"
    if not path.exists():
        return []
    db = open_db(path, readonly=True)
    try:
        rows = db.execute(
            "select thread_id, goal_id, objective, status, updated_at_ms from thread_goals"
        ).fetchall()
    finally:
        db.close()
    return [
        GoalRow(
            thread_id=row["thread_id"],
            goal_id=row["goal_id"],
            objective=row["objective"] or "",
            status=row["status"],
            updated_at_ms=int(row["updated_at_ms"]),
        )
        for row in rows
    ]


def parse_rollout(path: Path) -> RolloutInfo:
    info = RolloutInfo(path=path, exists=path.exists())
    if not info.exists:
        return info
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                info.line_count = line_no
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception as exc:  # noqa: BLE001 - report parser detail.
                    info.parse_errors.append((line_no, str(exc)[:160]))
                    continue

                typ = obj.get("type")
                payload = obj.get("payload") or {}
                if typ == "session_meta" and isinstance(payload, dict):
                    meta = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
                    info.session_id = meta.get("id") or info.session_id
                    info.session_provider = meta.get("model_provider") or info.session_provider
                elif typ == "turn_context" and isinstance(payload, dict):
                    turn_id = payload.get("turn_id")
                    info.context_lines.append((line_no, turn_id))
                    if not turn_id:
                        info.legacy_turn_contexts += 1
                        continue
                    if turn_id not in info.turns:
                        info.turns[turn_id] = TurnInfo(
                            turn_id=turn_id,
                            first_line=line_no,
                            last_context_line=line_no,
                        )
                        info.turn_order.append(turn_id)
                    turn = info.turns[turn_id]
                    turn.context_count += 1
                    turn.last_context_line = line_no
                elif typ == "event_msg" and isinstance(payload, dict):
                    event_type = payload.get("type")
                    turn_id = payload.get("turn_id")
                    if event_type in {"task_complete", "turn_aborted"} and turn_id in info.turns:
                        turn = info.turns[turn_id]
                        turn.closed = True
                        turn.close_type = event_type
                        turn.close_line = line_no
    except Exception as exc:  # noqa: BLE001 - report file read detail.
        info.parse_errors.append((-1, f"file read failed: {exc}"))
    return info


def scan(
    codex_home: Path,
    provider: str,
    *,
    include_archived: bool = False,
    thread_id: str | None = None,
    recent_minutes: int = 30,
) -> ScanResult:
    all_threads = fetch_all_threads(codex_home)
    by_id = {thread.id: thread for thread in all_threads}
    selected = all_threads if include_archived else [thread for thread in all_threads if not thread.archived]
    if thread_id:
        selected = [thread for thread in selected if thread.id == thread_id]

    selected_ids = {thread.id for thread in selected}
    active = [thread for thread in all_threads if not thread.archived]
    archived = [thread for thread in all_threads if thread.archived]
    rollouts = {thread.id: parse_rollout(thread.rollout_path) for thread in selected}

    provider_mismatch = [thread for thread in selected if thread.model_provider != provider]
    meta_mismatch: list[tuple[ThreadRow, str | None]] = []
    missing_rollouts: list[ThreadRow] = []
    parse_bad: list[tuple[ThreadRow, list[tuple[int, str]]]] = []
    stale_open: list[tuple[ThreadRow, TurnInfo]] = []
    recent_open: list[tuple[ThreadRow, TurnInfo]] = []
    cutoff_seconds = recent_minutes * 60
    now = time.time()

    for thread in selected:
        info = rollouts[thread.id]
        if not info.exists:
            missing_rollouts.append(thread)
            continue
        if info.parse_errors:
            parse_bad.append((thread, info.parse_errors))
            continue
        if info.session_provider != provider:
            meta_mismatch.append((thread, info.session_provider))
        for turn in info.open_turns:
            item = (thread, turn)
            if now - thread.updated_at <= cutoff_seconds:
                recent_open.append(item)
            else:
                stale_open.append(item)

    def edge_in_scope(edge: EdgeRow) -> bool:
        parent = by_id.get(edge.parent_thread_id)
        child = by_id.get(edge.child_thread_id)
        if thread_id:
            if edge.parent_thread_id != thread_id and edge.child_thread_id != thread_id:
                return False
            if include_archived:
                return True
            if parent and parent.archived:
                return False
            if child and child.archived:
                return False
            return bool(parent or child)
        if include_archived:
            return True
        if not parent or parent.archived:
            return False
        if child and child.archived:
            return False
        return True

    edges = fetch_edges(codex_home)
    open_edges = [edge for edge in edges if edge.status == "open" and edge_in_scope(edge)]
    edge_close: list[tuple[EdgeRow, ThreadRow]] = []
    edge_abort: list[tuple[EdgeRow, ThreadRow, list[TurnInfo]]] = []
    edge_missing: list[EdgeRow] = []
    child_rollout_cache: dict[str, RolloutInfo] = {}
    for edge in open_edges:
        child = by_id.get(edge.child_thread_id)
        if not child:
            edge_missing.append(edge)
            continue
        if child.id not in child_rollout_cache:
            child_rollout_cache[child.id] = rollouts.get(child.id) or parse_rollout(child.rollout_path)
        child_info = child_rollout_cache[child.id]
        child_open = child_info.open_turns
        if child_open:
            if now - child.updated_at <= cutoff_seconds:
                # A recent child turn may still be live. Report the open edge,
                # but do not plan mutation unless the caller explicitly repairs
                # recent turns in a targeted follow-up.
                continue
            edge_abort.append((edge, child, child_open))
        else:
            edge_close.append((edge, child))

    goals = fetch_goals(codex_home)
    stale_goal_statuses = {"active", "blocked", "usage_limited", "budget_limited"}
    stale_goals = [
        goal
        for goal in goals
        if goal.status in stale_goal_statuses and goal.thread_id in selected_ids
    ]
    provider_counts = Counter(thread.model_provider for thread in active)

    return ScanResult(
        codex_home=codex_home,
        provider=provider,
        threads=selected,
        active_threads=active,
        archived_threads=archived,
        rollouts=rollouts,
        provider_mismatch_threads=provider_mismatch,
        meta_provider_mismatches=meta_mismatch,
        missing_rollouts=missing_rollouts,
        parse_bad_rollouts=parse_bad,
        stale_open_turns=stale_open,
        recent_open_turns=recent_open,
        open_edges=open_edges,
        edge_close_direct=edge_close,
        edge_need_child_abort=edge_abort,
        edge_missing_child=edge_missing,
        goals=goals,
        stale_goals=stale_goals,
        provider_counts=provider_counts,
    )


def short(text: str, limit: int = 84) -> str:
    cleaned = " ".join(text.split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 3] + "..."


def print_scan(result: ScanResult, *, verbose: bool = True) -> None:
    print("SUMMARY")
    print(f"codex_home={result.codex_home}")
    print(f"target_provider={result.provider}")
    print(f"threads_selected={len(result.threads)}")
    print(f"active_total={len(result.active_threads)} archived_total={len(result.archived_threads)}")
    print(
        "active_provider_counts="
        + ", ".join(f"{provider}:{count}" for provider, count in result.provider_counts.most_common())
    )
    print(f"db_provider_mismatch={len(result.provider_mismatch_threads)}")
    print(f"session_meta_provider_mismatch={len(result.meta_provider_mismatches)}")
    print(f"missing_rollouts={len(result.missing_rollouts)}")
    print(f"jsonl_parse_bad={len(result.parse_bad_rollouts)}")
    print(f"stale_open_turns_gt_recent_window={len(result.stale_open_turns)}")
    print(f"recent_open_turns_preserved={len(result.recent_open_turns)}")
    print(f"open_spawn_edges={len(result.open_edges)}")
    print(f"edge_close_direct={len(result.edge_close_direct)}")
    print(f"edge_need_child_abort_first={len(result.edge_need_child_abort)}")
    print(f"stale_noncomplete_goals={len(result.stale_goals)}")

    if not verbose:
        return

    if result.provider_mismatch_threads:
        print("\nDB_PROVIDER_MISMATCH_SAMPLE")
        for thread in result.provider_mismatch_threads[:20]:
            print(f"{thread.id}\t{thread.model_provider}\t{short(thread.title)}")

    if result.meta_provider_mismatches:
        print("\nSESSION_META_PROVIDER_MISMATCH_SAMPLE")
        for thread, old_provider in result.meta_provider_mismatches[:20]:
            print(f"{thread.id}\tmeta={old_provider}\tdb={thread.model_provider}\t{short(thread.title)}")

    if result.stale_open_turns:
        print("\nSTALE_OPEN_TURNS")
        for thread, turn in result.stale_open_turns[:50]:
            print(
                f"{thread.id}\tline={turn.first_line}\tctx={turn.context_count}"
                f"\tturn={turn.turn_id}\t{short(thread.title)}"
            )

    if result.recent_open_turns:
        print("\nRECENT_OPEN_TURNS_PRESERVED")
        for thread, turn in result.recent_open_turns[:20]:
            print(
                f"{thread.id}\tline={turn.first_line}\tctx={turn.context_count}"
                f"\tturn={turn.turn_id}\t{short(thread.title)}"
            )

    if result.edge_close_direct:
        print("\nEDGE_CLOSE_DIRECT_SAMPLE")
        for edge, child in result.edge_close_direct[:30]:
            print(f"{edge.parent_thread_id}->{edge.child_thread_id}\t{short(child.title)}")

    if result.edge_need_child_abort:
        print("\nEDGE_NEED_CHILD_ABORT_FIRST")
        for edge, child, turns in result.edge_need_child_abort[:30]:
            last = turns[-1]
            print(
                f"{edge.parent_thread_id}->{edge.child_thread_id}"
                f"\topen_turns={len(turns)}\tlast={last.turn_id}\t{short(child.title)}"
            )

    if result.stale_goals:
        print("\nSTALE_GOALS")
        for goal in result.stale_goals:
            print(f"{goal.thread_id}\t{goal.status}\t{short(goal.objective, 120)}")

    if result.parse_bad_rollouts:
        print("\nPARSE_ERRORS")
        for thread, errors in result.parse_bad_rollouts[:20]:
            print(f"{thread.id}\t{thread.rollout_path}\t{errors[:3]}")

    if result.missing_rollouts:
        print("\nMISSING_ROLLOUTS")
        for thread in result.missing_rollouts[:20]:
            print(f"{thread.id}\t{thread.rollout_path}")


def build_abort_event(turn_id: str) -> dict[str, Any]:
    return {
        "timestamp": utc_stamp(),
        "type": "event_msg",
        "payload": {
            "type": "turn_aborted",
            "turn_id": turn_id,
            "reason": STALE_TURN_REASON,
            "completed_at": epoch_seconds(),
            "duration_ms": 0,
        },
    }


def insertion_line_for_turn(info: RolloutInfo, turn: TurnInfo) -> int | None:
    for line_no, turn_id in info.context_lines:
        if line_no > turn.last_context_line and turn_id != turn.turn_id:
            return line_no
    return None


def update_session_meta_provider(obj: dict[str, Any], provider: str) -> bool:
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return False
    meta = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if not isinstance(meta, dict):
        return False
    if meta.get("model_provider") == provider:
        return False
    meta["model_provider"] = provider
    return True


def rewrite_rollout(path: Path, provider: str, abort_turns: list[TurnInfo]) -> bool:
    info = parse_rollout(path)
    if info.parse_errors:
        raise RuntimeError(f"refusing to rewrite parse-bad rollout: {path}")

    insert_before: dict[int, list[dict[str, Any]]] = {}
    append_events: list[dict[str, Any]] = []
    for turn in abort_turns:
        event = build_abort_event(turn.turn_id)
        line = insertion_line_for_turn(info, turn)
        if line is None:
            append_events.append(event)
        else:
            insert_before.setdefault(line, []).append(event)

    changed = False
    output: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            for event in insert_before.get(line_no, []):
                output.append(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
                changed = True
            if not line.strip():
                output.append(line)
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                output.append(line)
                continue
            if obj.get("type") == "session_meta" and update_session_meta_provider(obj, provider):
                output.append(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
                changed = True
            else:
                output.append(line)
    for event in append_events:
        output.append(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        changed = True

    if changed:
        tmp = path.with_suffix(path.suffix + ".session-restore-tmp")
        tmp.write_text("".join(output), encoding="utf-8")
        tmp.replace(path)
    return changed


def backup_file(codex_home: Path, backup_dir: Path, path: Path) -> None:
    if not path.exists():
        return
    try:
        rel = path.resolve().relative_to(codex_home.resolve())
    except ValueError:
        rel = Path("external") / path.resolve().as_posix().lstrip("/")
    dest = backup_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)


def create_backup(
    codex_home: Path,
    rollout_paths: set[Path],
    *,
    include_state: bool,
    include_goals: bool,
) -> Path:
    backup_dir = codex_home / f"session-restore-backup-{backup_stamp()}"
    suffix = 1
    while backup_dir.exists():
        backup_dir = codex_home / f"session-restore-backup-{backup_stamp()}-{suffix}"
        suffix += 1
    backup_dir.mkdir(parents=True)

    for path in sorted(rollout_paths):
        backup_file(codex_home, backup_dir, path)

    if include_state:
        for path in codex_home.glob("state_5.sqlite*"):
            backup_file(codex_home, backup_dir, path)
        db = open_db(codex_home / "state_5.sqlite", readonly=True)
        try:
            consistent = sqlite3.connect(backup_dir / "state_5.sqlite.consistent-backup")
            try:
                db.backup(consistent)
            finally:
                consistent.close()
        finally:
            db.close()

    if include_goals:
        for path in codex_home.glob("goals_1.sqlite*"):
            backup_file(codex_home, backup_dir, path)
        goals_path = codex_home / "goals_1.sqlite"
        if goals_path.exists():
            db = open_db(goals_path, readonly=True)
            try:
                consistent = sqlite3.connect(backup_dir / "goals_1.sqlite.consistent-backup")
                try:
                    db.backup(consistent)
                finally:
                    consistent.close()
            finally:
                db.close()

    return backup_dir


def selected_thread_ids(result: ScanResult) -> set[str]:
    return {thread.id for thread in result.threads}


def rollout_updates_for_result(
    result: ScanResult,
    *,
    close_recent_open_turns: bool,
) -> dict[str, list[TurnInfo]]:
    updates: dict[str, list[TurnInfo]] = {}
    for thread, turn in result.stale_open_turns:
        updates.setdefault(thread.id, []).append(turn)
    if close_recent_open_turns:
        for thread, turn in result.recent_open_turns:
            updates.setdefault(thread.id, []).append(turn)
    for _edge, child, turns in result.edge_need_child_abort:
        if child.archived:
            continue
        updates.setdefault(child.id, [])
        existing = {turn.turn_id for turn in updates[child.id]}
        for turn in turns:
            if turn.turn_id not in existing:
                updates[child.id].append(turn)
                existing.add(turn.turn_id)
    return updates


def rollout_paths_to_modify(
    result: ScanResult,
    updates: dict[str, list[TurnInfo]],
) -> set[Path]:
    paths: set[Path] = set()
    for thread, _old_provider in result.meta_provider_mismatches:
        paths.add(thread.rollout_path)
    by_id = {thread.id: thread for thread in result.active_threads + result.archived_threads}
    for thread_id in updates:
        thread = by_id.get(thread_id)
        if thread:
            paths.add(thread.rollout_path)
    return paths


def ensure_safe_to_apply(result: ScanResult, *, close_recent_open_turns: bool) -> None:
    if result.missing_rollouts:
        raise RuntimeError("refusing to apply: active rollout files are missing")
    if result.parse_bad_rollouts:
        raise RuntimeError("refusing to apply: rollout JSONL parse errors were detected")
    if close_recent_open_turns:
        return
    # Recent open turns may exist, but they must not be in the mutation set.
    return


def repair(
    args: argparse.Namespace,
    *,
    thread_id: str | None,
    bulk: bool,
) -> int:
    codex_home = codex_home_from_args(args)
    result = scan(
        codex_home,
        args.provider,
        include_archived=args.include_archived,
        thread_id=thread_id,
        recent_minutes=args.recent_minutes,
    )
    print_scan(result)

    if bulk and args.apply and not args.yes:
        print("\nERROR: bulk apply requires --yes", file=sys.stderr)
        return 2

    updates = rollout_updates_for_result(result, close_recent_open_turns=args.close_recent_open_turns)
    rollout_paths = rollout_paths_to_modify(result, updates)
    state_write_needed = bool(
        result.provider_mismatch_threads or result.edge_close_direct or result.edge_need_child_abort
    )
    goal_write_needed = bool(args.complete_stale_goal and result.stale_goals)

    print("\nPLANNED_ACTIONS")
    print(f"apply={args.apply}")
    print(f"rollout_files_to_modify={len(rollout_paths)}")
    print(f"db_provider_rows_to_update={len(result.provider_mismatch_threads)}")
    print(f"turns_to_abort={sum(len(v) for v in updates.values())}")
    print(f"spawn_edges_to_close={len(result.edge_close_direct) + len(result.edge_need_child_abort)}")
    print(f"goals_to_complete={len(result.stale_goals) if args.complete_stale_goal else 0}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to write changes.")
        return 0

    fresh = scan(
        codex_home,
        args.provider,
        include_archived=args.include_archived,
        thread_id=thread_id,
        recent_minutes=args.recent_minutes,
    )
    ensure_safe_to_apply(fresh, close_recent_open_turns=args.close_recent_open_turns)
    updates = rollout_updates_for_result(fresh, close_recent_open_turns=args.close_recent_open_turns)
    rollout_paths = rollout_paths_to_modify(fresh, updates)
    state_write_needed = bool(
        fresh.provider_mismatch_threads or fresh.edge_close_direct or fresh.edge_need_child_abort
    )
    goal_write_needed = bool(args.complete_stale_goal and fresh.stale_goals)

    backup_dir = create_backup(
        codex_home,
        rollout_paths,
        include_state=state_write_needed,
        include_goals=goal_write_needed,
    )
    print(f"\nBACKUP_DIR={backup_dir}")

    by_id = {thread.id: thread for thread in fresh.active_threads + fresh.archived_threads}
    modified_rollouts: list[Path] = []
    for path in sorted(rollout_paths):
        thread = next((candidate for candidate in by_id.values() if candidate.rollout_path == path), None)
        abort_turns = updates.get(thread.id, []) if thread else []
        if rewrite_rollout(path, fresh.provider, abort_turns):
            modified_rollouts.append(path)

    if state_write_needed:
        db = open_db(codex_home / "state_5.sqlite", readonly=False)
        try:
            with db:
                if fresh.provider_mismatch_threads:
                    ids = [thread.id for thread in fresh.provider_mismatch_threads]
                    db.executemany(
                        "update threads set model_provider = ? where id = ? and archived = 0",
                        [(fresh.provider, thread_id_item) for thread_id_item in ids],
                    )
                edge_ids = {
                    edge.child_thread_id for edge, _child in fresh.edge_close_direct
                } | {
                    edge.child_thread_id for edge, _child, _turns in fresh.edge_need_child_abort
                }
                if edge_ids:
                    db.executemany(
                        "update thread_spawn_edges set status = ? where child_thread_id = ? and status = 'open'",
                        [(EDGE_CLOSED_STATUS, edge_id) for edge_id in sorted(edge_ids)],
                    )
        finally:
            db.close()

    if goal_write_needed:
        db = open_db(codex_home / "goals_1.sqlite", readonly=False)
        try:
            now_ms = int(time.time() * 1000)
            with db:
                db.executemany(
                    "update thread_goals set status = ?, updated_at_ms = ? where thread_id = ?",
                    [(GOAL_DONE_STATUS, now_ms, goal.thread_id) for goal in fresh.stale_goals],
                )
        finally:
            db.close()

    print("\nMODIFIED_ROLLOUTS")
    for path in modified_rollouts:
        print(path)
    print("\nApply complete. Restart Codex Desktop if the sidebar still shows missing sessions or systemError.")
    return 0


def verify(args: argparse.Namespace) -> int:
    codex_home = codex_home_from_args(args)
    result = scan(
        codex_home,
        args.provider,
        include_archived=args.include_archived,
        thread_id=args.thread_id,
        recent_minutes=args.recent_minutes,
    )
    print_scan(result, verbose=True)
    failures: list[str] = []
    if result.provider_mismatch_threads:
        failures.append("database provider mismatches remain")
    if result.meta_provider_mismatches:
        failures.append("rollout session_meta provider mismatches remain")
    if result.missing_rollouts:
        failures.append("rollout files are missing")
    if result.parse_bad_rollouts:
        failures.append("rollout JSONL parse errors remain")
    if result.stale_open_turns:
        failures.append("stale open turns remain")
    if result.open_edges:
        failures.append("open spawn edges remain")

    if failures:
        print("\nVERIFY_FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nVERIFY_PASSED")
    if result.recent_open_turns:
        print("Recent open turns were preserved as active continuations.")
    if result.stale_goals:
        print("Non-complete goals remain; complete them only if they block restore.")
    print("Restart Codex Desktop if the sidebar has not refreshed.")
    return 0


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
    parser.add_argument("--provider", default="krill")
    parser.add_argument("--include-archived", action="store_true")
    parser.add_argument("--recent-minutes", type=int, default=30)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Restore Codex Desktop session state.")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan", help="Read-only scan of active sessions.")
    add_common_flags(scan_parser)

    scan_thread = sub.add_parser("scan-thread", help="Read-only scan of one thread.")
    add_common_flags(scan_thread)
    scan_thread.add_argument("--thread-id", required=True)

    repair_thread = sub.add_parser("repair-thread", help="Preview or repair one thread.")
    add_common_flags(repair_thread)
    repair_thread.add_argument("--thread-id", required=True)
    repair_thread.add_argument("--apply", action="store_true")
    repair_thread.add_argument("--close-recent-open-turns", action="store_true")
    repair_thread.add_argument("--complete-stale-goal", "--complete-blocked-goal", action="store_true")

    repair_active = sub.add_parser("repair-active", help="Preview or repair active sessions.")
    add_common_flags(repair_active)
    repair_active.add_argument("--apply", action="store_true")
    repair_active.add_argument("--yes", action="store_true")
    repair_active.add_argument("--close-recent-open-turns", action="store_true")
    repair_active.add_argument("--complete-stale-goal", "--complete-blocked-goal", action="store_true")

    verify_parser = sub.add_parser("verify", help="Verify repaired session state.")
    add_common_flags(verify_parser)
    verify_parser.add_argument("--thread-id")

    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            print_scan(
                scan(
                    codex_home_from_args(args),
                    args.provider,
                    include_archived=args.include_archived,
                    recent_minutes=args.recent_minutes,
                )
            )
            return 0
        if args.command == "scan-thread":
            print_scan(
                scan(
                    codex_home_from_args(args),
                    args.provider,
                    include_archived=args.include_archived,
                    thread_id=args.thread_id,
                    recent_minutes=args.recent_minutes,
                )
            )
            return 0
        if args.command == "repair-thread":
            return repair(args, thread_id=args.thread_id, bulk=False)
        if args.command == "repair-active":
            return repair(args, thread_id=None, bulk=True)
        if args.command == "verify":
            return verify(args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
