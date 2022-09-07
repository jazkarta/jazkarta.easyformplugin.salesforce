# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.easyform.tests.testDocTests import get_browser
from datetime import datetime
from dateutil.parser import parse
from jazkarta.easyformplugin.salesforce.testing import (
    JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING,  # noqa: E501,
    vcr,
)
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
import transaction

import json
import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestIntegration(unittest.TestCase):
    """Test that the Salesforce action works properly."""

    layer = JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING

    def setUp(self):
        # Create a form
        portal = self.layer["portal"]
        setRoles(portal, TEST_USER_ID, ["Manager"])
        portal.invokeFactory("Folder", "test-folder")
        folder = portal["test-folder"]
        folder.invokeFactory("EasyForm", "test-form")
        self.form = folder["test-form"]
        self.form.fields_model = """<model xmlns:easyform="http://namespaces.plone.org/supermodel/easyform" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:lingua="http://namespaces.plone.org/supermodel/lingua" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:users="http://namespaces.plone.org/supermodel/users" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="first_name" type="zope.schema.TextLine">
      <description/>
      <required>False</required>
      <title>First Name</title>
    </field>
    <field name="last_name" type="zope.schema.TextLine">
      <description/>
      <title>Last Name</title>
    </field>
    <field name="do_not_call" type="zope.schema.Bool">
      <description/>
      <required>False</required>
      <title>Do Not Call</title>
    </field>
    <field name="birthdate" type="zope.schema.Date">
      <description/>
      <required>False</required>
      <title>Birthdate</title>
    </field>
  </schema>
</model>"""
        self.form.actions_model = None
        transaction.commit()

    def test_01_submit_form_with_salesforce_adapter(self):
        # Open browser
        browser = Browser(self.layer["app"])
        browser.addHeader("Authorization", "Basic {}:{}".format(TEST_USER_NAME, TEST_USER_PASSWORD))
        browser.handleErrors = False
        form_url = self.form.absolute_url()

        # Add a Salesforce action
        browser.open(form_url + "/actions/@@add-action")
        browser.getControl("Title").value = "Create Salesforce Contact"
        browser.getControl("Short Name").value = "sf_contact"
        browser.getControl("Send to Salesforce").selected = True
        browser.getControl("Add").click()
        browser.open(form_url + "/actions/sf_contact")
        browser.getControl("Operations").value = json.dumps([
            {
                "sobject": "Contact",
                "operation": "create",
                "fields": {
                    "Description": "Created by jazkarta.easyformplugin.salesforce tests",
                    "FirstName": "form:first_name",
                    "LastName": "form:last_name",
                    "Birthdate": "form:birthdate",
                    "CreatedDate": "python:now",
                    "DoNotCall": "form:do_not_call"
                },
            },
        ])
        browser.getControl("Save").click()

        # Fill and submit the form
        browser.open(form_url)
        # first name intentionally left blank
        browser.getControl("Last Name").value = "McTesterson"
        browser.getControl("Do Not Call").selected = True
        browser.getControl(name="form.widgets.birthdate").value = "1985-09-30"

        with vcr.use_cassette("basic.yaml") as cassette:
            browser.getControl("Submit").click()

        self.assertEqual(len(cassette), 2)
        actual_data = json.loads(cassette.requests[-1].body)
        assert set(actual_data.keys()) == {"FirstName", "LastName", "Birthdate", "CreatedDate", "DoNotCall", "Description"}
        assert actual_data["FirstName"] is None
        assert actual_data["LastName"] == "McTesterson"
        assert actual_data["DoNotCall"] == True
        assert actual_data["Birthdate"] == "1985-09-30"
        created_date = parse(actual_data["CreatedDate"])
        assert isinstance(created_date, datetime)
        assert created_date.tzinfo is not None
        assert actual_data["Description"] == "Created by jazkarta.easyformplugin.salesforce tests"
        assert json.loads(cassette.responses[-1]["body"]["string"])["success"]

    def test_02_prefill_form_from_salesforce(self):
        # Note: when running without the vcr cassette,
        # this test uses the Contact that was added to Salesforce
        # in the preceding test.

        # Open browser
        browser = Browser(self.layer["app"])
        browser.addHeader("Authorization", "Basic {}:{}".format(TEST_USER_NAME, TEST_USER_PASSWORD))
        browser.handleErrors = False
        form_url = self.form.absolute_url()

        # Add a Salesforce action
        browser.open(form_url + "/actions/@@add-action")
        browser.getControl("Title").value = "Update Salesforce Contact"
        browser.getControl("Short Name").value = "sf_contact"
        browser.getControl("Send to Salesforce").selected = True
        browser.getControl("Add").click()
        browser.open(form_url + "/actions/sf_contact")
        browser.getControl("Operations").value = json.dumps([
            {
                "sobject": "Contact",
                "operation": "update",
                "match_expression": "LastName = 'McTesterson'",
                "fields": {
                    "Description": "Created by jazkarta.easyformplugin.salesforce tests",
                    "FirstName": "form:first_name",
                    "LastName": "form:last_name",
                    "Birthdate": "form:birthdate",
                    "CreatedDate": "python:now",
                    "DoNotCall": "form:do_not_call"
                },
            },
        ])
        browser.getControl("Save").click()

        # Fill and submit the form
        with vcr.use_cassette("prefill.yaml") as cassette:
            browser.open(form_url)

        # Confirm values were prefilled
        assert browser.getControl("First Name").value == ""
        assert browser.getControl("Last Name").value == "McTesterson"
        assert browser.getControl("Do Not Call").selected
        assert browser.getControl(name="form.widgets.birthdate").value == "1985-09-30"
        # TODO: add hidden field with encrypted sf_id, use it when saving
