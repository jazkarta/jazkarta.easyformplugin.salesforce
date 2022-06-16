# -*- coding: utf-8 -*-
import os
import re

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2
import vcr

import jazkarta.easyformplugin.salesforce


class JazkartaEasyformpluginSalesforceLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=jazkarta.easyformplugin.salesforce)

    def setUpPloneSite(self, portal):
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


def scrub_login_request(request):
    request.body = re.sub(
        r"<n1:(username|password)>.*?</n1:\1>",
        lambda m: "<n1:" + m.group(1) + ">REDACTED</n1:" + m.group(1) + ">",
        request.body,
    )
    return request


def scrub_login_response(response):
    response["body"]["string"] = re.sub(
        r"<sessionId>.*?</sessionId>",
        "<sessionId>FAKE_SESSION</sessionId>",
        response["body"]["string"],
    )
    return response


vcr = vcr.VCR(
    cassette_library_dir=os.path.dirname(__file__) + "/tests/cassettes",
    before_record_request=scrub_login_request,
    before_record_response=scrub_login_response,
    decode_compressed_response=True,
    filter_headers=["authorization"],
)
