# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.easyform.interfaces.actions import MODIFY_PORTAL_CONTENT, IAction
from plone.autoform import directives
from plone.schema.jsonfield import JSONField
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from . import _

class IJazkartaEasyformpluginSalesforceLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISaveToSalesforce(IAction):
    """Easyform action which saves data to Salesforce"""

    directives.read_permission(mapping=MODIFY_PORTAL_CONTENT)
    mapping = JSONField(
        title=_(u"label_salesforce_mapping", default=u"Field Mapping"),
        # TODO add description with instructions,
        defaultFactory=dict,
    )
