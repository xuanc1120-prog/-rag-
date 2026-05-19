from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from app.models import Ticket, utc_now_iso


class TicketRepository:
    """工单仓库。"""
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        # 如果数据库目录不存在，就先创建出来，方便首次运行。
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """建立数据库连接。"""
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        """在首次运行时建表。"""
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    issue TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    resolution_notes TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.commit()

    def create_ticket(self, *, title: str, issue: str, priority: str, customer_email: str) -> Ticket:
        """创建一张新工单。"""
        now = utc_now_iso()
        ticket = Ticket(
            ticket_id=f"TCK-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            issue=issue,
            priority=priority,
            status="open",
            customer_email=customer_email,
            created_at=now,
            updated_at=now,
        )
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO tickets (
                    ticket_id, title, issue, priority, status, customer_email, created_at, updated_at, resolution_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.ticket_id,
                    ticket.title,
                    ticket.issue,
                    ticket.priority,
                    ticket.status,
                    ticket.customer_email,
                    ticket.created_at,
                    ticket.updated_at,
                    ticket.resolution_notes,
                ),
            )
            conn.commit()
        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        """按工单号查询单个工单。"""
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT ticket_id, title, issue, priority, status, customer_email, created_at, updated_at, resolution_notes
                FROM tickets WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()
        return self._row_to_ticket(row) if row else None

    def list_open_tickets(self) -> list[Ticket]:
        """列出所有未关闭工单。"""
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT ticket_id, title, issue, priority, status, customer_email, created_at, updated_at, resolution_notes
                FROM tickets WHERE status != 'closed'
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [self._row_to_ticket(row) for row in rows]

    def escalate_ticket(self, ticket_id: str, reason: str) -> Ticket:
        """升级工单，并把优先级提升为 high。"""
        current = self.get_ticket(ticket_id)
        if current is None:
            raise KeyError(f"Unknown ticket_id: {ticket_id}")

        notes = current.resolution_notes.strip()
        if notes:
            notes = f"{notes}\nEscalation: {reason}"
        else:
            notes = f"Escalation: {reason}"
        updated_at = utc_now_iso()

        with closing(self._connect()) as conn:
            conn.execute(
                """
                UPDATE tickets
                SET status = ?, priority = ?, resolution_notes = ?, updated_at = ?
                WHERE ticket_id = ?
                """,
                ("escalated", "high", notes, updated_at, ticket_id),
            )
            conn.commit()

        escalated = self.get_ticket(ticket_id)
        assert escalated is not None
        return escalated

    @staticmethod
    def _row_to_ticket(row: tuple[str, str, str, str, str, str, str, str, str]) -> Ticket:
        """把数据库 row 转回项目内部的 Ticket 对象。"""
        return Ticket(
            ticket_id=row[0],
            title=row[1],
            issue=row[2],
            priority=row[3],
            status=row[4],
            customer_email=row[5],
            created_at=row[6],
            updated_at=row[7],
            resolution_notes=row[8],
        )
