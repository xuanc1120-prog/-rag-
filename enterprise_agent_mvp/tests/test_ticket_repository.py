import tempfile
import unittest
from pathlib import Path

from app.db.ticket_repository import TicketRepository


class TicketRepositoryTests(unittest.TestCase):
    def test_create_and_escalate_ticket(self) -> None:
        """验证工单可以被创建，并在升级后更新状态和优先级。"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = TicketRepository(Path(tmp_dir) / "tickets.db")

            ticket = repo.create_ticket(
                title="Password reset blocked",
                issue="Customer cannot reset password after 3 attempts.",
                priority="medium",
                customer_email="user@example.com",
            )
            self.assertEqual(ticket.status, "open")

            escalated = repo.escalate_ticket(ticket.ticket_id, "VIP customer waiting for login.")

            self.assertEqual(escalated.status, "escalated")
            self.assertEqual(escalated.priority, "high")
            self.assertIn("VIP customer", escalated.resolution_notes)


if __name__ == "__main__":
    unittest.main()
