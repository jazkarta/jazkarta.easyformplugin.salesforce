# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import jazkarta.easyformplugin.salesforce


class JazkartaEasyformpluginSalesforceLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        z2.installProduct(app, "Products.salesforcebaseconnector")
        self.loadZCML(package=jazkarta.easyformplugin.salesforce)

    def setUpPloneSite(self, portal):
        portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        applyProfile(portal, "jazkarta.easyformplugin.salesforce:default")


JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FIXTURE = JazkartaEasyformpluginSalesforceLayer()


JAZKARTA_EASYFORMPLUGIN_SALESFORCE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FIXTURE,),
    name="JazkartaEasyformpluginSalesforceLayer:IntegrationTesting",
)


JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FIXTURE,),
    name="JazkartaEasyformpluginSalesforceLayer:FunctionalTesting",
)


JAZKARTA_EASYFORMPLUGIN_SALESFORCE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        JAZKARTA_EASYFORMPLUGIN_SALESFORCE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="JazkartaEasyformpluginSalesforceLayer:AcceptanceTesting",
)
