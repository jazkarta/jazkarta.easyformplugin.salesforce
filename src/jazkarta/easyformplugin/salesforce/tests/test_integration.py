# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.easyform.tests.testDocTests import get_browser
from jazkarta.easyformplugin.salesforce.testing import (
    JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING,  # noqa: E501,
)
from plone import api
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser

import json
import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


try:
    from unittest import mock
except ImportError:
    import mock


class TestIntegration(unittest.TestCase):
    """Test that the Salesforce action works properly."""

    layer = JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING

    def test_submit_form_with_salesforce_adapter(self):
        browser = Browser(self.layer["app"])
        browser.addHeader("Authorization", "Basic {}:{}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        browser.handleErrors = False

        # Create a form
        portal_url = self.layer["portal"].absolute_url()
        browser.open(portal_url)
        browser.getLink("EasyForm").click()
        browser.getControl("Title").value = "sftest"
        browser.getControl("Save").click()

        # Delete the default mailer action
        browser.getLink("Define form actions").click()
        browser.getLink(url="/mailer/@@delete").click()

        # Add a Salesforce action
        browser.open(portal_url + "/sftest/actions/@@add-action")
        browser.getControl("Title").value = "Salesforce"
        browser.getControl("Short Name").value = "salesforce"
        browser.getControl("Send to Salesforce").selected = True
        browser.getControl("Add").click()
        browser.open(portal_url + "/sftest/actions/salesforce")
        browser.getControl("Operations").value = json.dumps([
            {
                "operation": "create",
                "sobject": "Lead",
                "fields": {
                    "Email": "form:replyto"
                }
            }
        ])
        browser.getControl("Save").click()

        # Mock salesforcebaseconnector so we don't actually call Salesforce
        with mock.patch("Products.salesforcebaseconnector.salesforcebaseconnector.SalesforceBaseConnector.create") as create:
            create.return_value = [
                {
                    "success": True,
                    "id": "xxx",
                }
            ]

            # Fill and submit the form
            browser.open(portal_url + "/sftest")
            browser.getControl("Your E-Mail Address").value = "test@example.com"
            browser.getControl("Subject").value = "test"
            browser.getControl("Comments").value = "test"
            browser.getControl("Submit").click()

            create.assert_called_once()
            self.assertIn("Thanks for your input.", browser.contents)
