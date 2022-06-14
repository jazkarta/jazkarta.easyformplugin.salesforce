# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

import json

from collective.easyform.interfaces.actions import MODIFY_PORTAL_CONTENT, IAction
from plone.autoform import directives
from plone.schema.jsonfield import JSONField
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from . import _

class IJazkartaEasyformpluginSalesforceLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISaveToSalesforce(IAction):
    """Easyform action which saves data to Salesforce"""

    directives.read_permission(operations=MODIFY_PORTAL_CONTENT)
    operations = JSONField(
        title=_(u"label_salesforce_operations", default=u"Salesforce Operations"),
        # TODO add description with instructions,
        defaultFactory=list,
        schema=json.dumps({
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "sobject",
                    "operation",
                    "fields",
                ],
                "properties": {
                    "sobject": {"type": "string"},
                    "operation": {"type": "string", "enum": ["create"]},
                    "fields": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                },
                "additionalProperties": False,
            },
        })
    )
