# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from jazkarta.easyformplugin.salesforce.testing import (
    JAZKARTA_EASYFORMPLUGIN_SALESFORCE_INTEGRATION_TESTING,  # noqa: E501,
)
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that jazkarta.easyformplugin.salesforce is properly installed."""

    layer = JAZKARTA_EASYFORMPLUGIN_SALESFORCE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if jazkarta.easyformplugin.salesforce is installed."""
        self.assertTrue(
            self.installer.isProductInstalled("jazkarta.easyformplugin.salesforce")
        )

    def test_browserlayer(self):
        """Test that IJazkartaEasyformpluginSalesforceLayer is registered."""
        from jazkarta.easyformplugin.salesforce.interfaces import (
            IJazkartaEasyformpluginSalesforceLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(IJazkartaEasyformpluginSalesforceLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = JAZKARTA_EASYFORMPLUGIN_SALESFORCE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["jazkarta.easyformplugin.salesforce"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if jazkarta.easyformplugin.salesforce is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled("jazkarta.easyformplugin.salesforce")
        )

    def test_browserlayer_removed(self):
        """Test that IJazkartaEasyformpluginSalesforceLayer is removed."""
        from jazkarta.easyformplugin.salesforce.interfaces import (
            IJazkartaEasyformpluginSalesforceLayer,
        )
        from plone.browserlayer import utils

        self.assertNotIn(
            IJazkartaEasyformpluginSalesforceLayer, utils.registered_layers()
        )
