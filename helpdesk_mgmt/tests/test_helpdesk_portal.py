# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# import odoo.tests
from odoo import http
from odoo.tests.common import new_test_user, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT, HttpCaseWithUserPortal


@tagged("post_install", "-at_install")
class TestHelpdeskPortalBase(HttpCaseWithUserPortal):
    """Test controllers defined for portal mode.
    This is mostly for basic coverage; we don't go as far as fully validating
    HTML produced by our routes.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.new_ticket_title = "portal-new-submitted-ticket-subject"
        cls.new_ticket_desc_lines = (  # multiline description to check line breaks
            "portal-new-submitted-ticket-description-line-1",
            "portal-new-submitted-ticket-description-line-2",
        )
        cls.company = cls.env.ref("base.main_company")
        cls.partner_portal.parent_id = cls.company.partner_id
        # Create a basic user with no helpdesk permissions.
        cls.basic_user = new_test_user(cls.env, login="test-basic-user")
        cls.basic_user.parent_id = cls.company.partner_id
        # Create a ticket submitted by our portal user.
        cls.portal_ticket = cls._create_ticket(
            cls.partner_portal, "portal-ticket-title"
        )

    def get_new_tickets(self, user):
        return self.env["helpdesk.ticket"].with_user(user).search([])

    @classmethod
    def _create_ticket(cls, partner, ticket_title, **values):
        """Create a ticket submitted by the specified partner."""
        data = {
            "name": ticket_title,
            "description": "portal-ticket-description",
            "partner_id": partner.id,
            "partner_email": partner.email,
            "partner_name": partner.name,
        }
        data.update(**values)
        return cls.env["helpdesk.ticket"].create(data)

    def _submit_ticket(self, files=None, **values):
        data = {
            "category": self.env.ref("helpdesk_mgmt.helpdesk_category_1").id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": "\n".join(self.new_ticket_desc_lines),
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data, files=files)
        self.assertEqual(resp.status_code, 200)


class TestHelpdeskPortal(TestHelpdeskPortalBase):
    def test_submit_ticket_01(self):
        self.authenticate("test-basic-user", "test-basic-user")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.basic_user)
        self.assertNotIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))
        self.assertIn(
            "<p>" + "<br>".join(self.new_ticket_desc_lines) + "</p>",
            tickets.mapped("description"),
        )

    def test_submit_ticket_02(self):
        self.authenticate("portal", "portal")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.user_portal)
        self.assertIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))
        self.assertIn(
            "<p>" + "<br>".join(self.new_ticket_desc_lines) + "</p>",
            tickets.mapped("description"),
        )

    def test_ticket_list(self):
        """List tickets in portal mode, ensure it contains our test ticket."""
        self.authenticate("portal", "portal")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("portal-ticket-title", resp.text)

    def test_ticket_form(self):
        """Open our test ticket in portal mode."""
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("portal-ticket-title", resp.text)
        self.assertIn("portal-ticket-description", resp.text)

    def test_close_ticket(self):
        """Close a ticket from the portal."""
        self.assertFalse(self.portal_ticket.closed)
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(self._count_close_buttons(resp), 2)  # 2 close stages in data/
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self._call_close_ticket(self.portal_ticket, stage)
        self.assertTrue(self.portal_ticket.closed)
        self.assertEqual(self.portal_ticket.stage_id, stage)
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(self._count_close_buttons(resp), 0)  # no close buttons now

    def test_close_ticket_invalid_stage(self):
        """Attempt to close a ticket from the portal with an invalid target stage."""
        self.authenticate("portal", "portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_awaiting")
        self._call_close_ticket(self.portal_ticket, stage)
        self.assertFalse(self.portal_ticket.closed)
        self.assertNotEqual(self.portal_ticket.stage_id, stage)

    def test_ticket_list_unauthenticated(self):
        """Attempt to list tickets without auth, ensure we get sent back to login."""
        resp = self.url_open("/my/tickets", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        # http://127.0.0.1:8069/web/login?redirect=http%3A%2F%2F127.0.0.1%3A8069%2Fmy%2Ftickets
        self.assertIn("/web/login", resp.headers["Location"])

    def test_ticket_list_authorized(self):
        """Attempt to list tickets without helpdesk permissions."""
        self.authenticate("test-basic-user", "test-basic-user")
        resp = self.url_open("/my/tickets", allow_redirects=False)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.is_redirect)

    def test_tickets_2_users(self):
        """Check tickets between 2 portal users; ensure they can't access each
        others' tickets.
        """
        self.partner_portal.parent_id = False
        portal_user_1 = self.user_portal  # created by HttpCaseWithUserPortal
        portal_user_2 = self.user_portal.copy(
            default={"login": "portal2", "password": "portal2"}
        )

        ticket_1 = self._create_ticket(portal_user_1.partner_id, "ticket-user-1")
        ticket_2 = self._create_ticket(portal_user_2.partner_id, "ticket-user-2")

        # Portal ticket list: portal_user_1 only sees ticket_1
        self.authenticate("portal", "portal")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-1", resp.text)
        self.assertNotIn("ticket-user-2", resp.text)

        # Portal ticket list: portal_user_2 only sees ticket_2
        self.authenticate("portal2", "portal2")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("ticket-user-1", resp.text)
        self.assertIn("ticket-user-2", resp.text)

        # Portal ticket form: portal_user_1 can open ticket_1 but not ticket_2
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/my/ticket/{ticket_1.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-1", resp.text)
        resp = self.url_open(f"/my/ticket/{ticket_2.id}", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        self.assertTrue(resp.headers["Location"].endswith("/my"))

        # Portal ticket form: portal_user_2 can open ticket_2 but not ticket_1
        self.authenticate("portal2", "portal2")
        resp = self.url_open(f"/my/ticket/{ticket_1.id}", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        self.assertTrue(resp.headers["Location"].endswith("/my"))
        resp = self.url_open(f"/my/ticket/{ticket_2.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-2", resp.text)

    def _count_close_buttons(self, resp) -> int:
        """Count close buttons in a form by counting forms with that target."""
        return resp.text.count('action="/ticket/close"')

    def _call_close_ticket(self, ticket, stage):
        """Call /ticket/close with the specified target stage, check redirect."""
        resp = self.url_open(
            "/ticket/close",
            data={
                "csrf_token": http.Request.csrf_token(self),
                "stage_id": stage.id,
                "ticket_id": ticket.id,
            },
            allow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.is_redirect)  # http://127.0.0.1:8069/my/ticket/<ticket-id>
        self.assertTrue(resp.headers["Location"].endswith(f"/my/ticket/{ticket.id}"))
        return resp

    def test_submit_ticket_with_attachments(self):
        self.authenticate("test-basic-user", "test-basic-user")
        self._submit_ticket(
            files=[
                (
                    "attachment",
                    ("test.txt", b"test", "plain/text"),
                ),
                (
                    "attachment",
                    ("test.svg", b"<svg></svg>", "image/svg+xml"),
                ),
            ]
        )
        ticket_id = self.get_new_tickets(self.basic_user)
        self.assertEqual(len(ticket_id), 1)
        # check that both files have been linked to the newly created ticket
        attachment_ids = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "helpdesk.ticket"),
                ("res_id", "=", ticket_id.id),
            ]
        )
        self.assertEqual(len(attachment_ids), 2)
        # check that both files have kept their names
        self.assertIn("test.txt", attachment_ids.mapped("name"))
        self.assertIn("test.svg", attachment_ids.mapped("name"))
        # check that both files are public (access_token is set)
        self.assertTrue(attachment_ids[0].access_token)
        self.assertTrue(attachment_ids[1].access_token)
