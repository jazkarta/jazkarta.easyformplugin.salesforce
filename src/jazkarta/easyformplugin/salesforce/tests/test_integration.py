# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.easyform.tests.testDocTests import get_browser
from jazkarta.easyformplugin.salesforce.testing import (
    JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING,  # noqa: E501,
    vcr,
)
from plone import api
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import json
import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


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

        # Delete the default fields
        browser.getLink("Define form fields").click()
        browser.getLink(url="/replyto/@@delete").click()
        browser.goBack()
        browser.getLink(url="/topic/@@delete").click()
        browser.goBack()
        browser.getLink(url="/comments/@@delete").click()

        # Add last name field
        browser.goBack()
        browser.getLink(id="add-field").click()
        browser.getControl("Title").value = "Last Name"
        browser.getControl("Short Name").value = "last_name"
        browser.getControl("String").selected = True
        browser.getControl("Add").click()

        # Delete the default mailer action
        browser.open(portal_url + "/sftest/actions")
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
                "sobject": "Contact",
                "fields": {
                    "LastName": "form:last_name"
                }
            }
        ])
        browser.getControl("Save").click()

        # Fill and submit the form
        browser.open(portal_url + "/sftest")
        browser.getControl("Last Name").value = "McTesterson"

        with vcr.use_cassette("basic.yaml") as cassette:
            browser.getControl("Submit").click()

        self.assertEqual(len(cassette), 2)
        assert cassette.requests[-1].body == json.dumps({"LastName": "McTesterson"})
        assert json.loads(cassette.responses[-1]["body"]["string"])["success"]
