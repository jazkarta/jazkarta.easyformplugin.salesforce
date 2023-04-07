# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.easyform.interfaces.actions import MODIFY_PORTAL_CONTENT, IAction
from collective.easyform.interfaces import IEasyFormLayer
from plone.autoform import directives
from plone.schema.jsonfield import JSONField
from . import _
import json


class IJazkartaEasyformpluginSalesforceLayer(IEasyFormLayer):
    """Marker interface that defines a browser layer."""


class ISaveToSalesforce(IAction):
    """Easyform action which saves data to Salesforce"""

    directives.read_permission(operations=MODIFY_PORTAL_CONTENT)
    operations = JSONField(
        title=_(u"label_salesforce_operations", default=u"Salesforce Operations"),
        description=_(u"help_salesforce_operations", default=u"""A JSON list of operations to perform.

    Each operation must specify:
    * sobject - name of the Salesforce sObject
    * operation - what operation to perform (`create` is currently the only supported operation)
    * fields - a mapping of Salesforce field names to expressions.

    Each field expression can be one of:
    * "form:x" -- value of the form field named `x`
    * "path:x" -- a TALES path expression
    * "python:x" -- a TALES Python expression
    * "string:x" -- a TALES string expression

    Example:
    [
        {
            "sobject": "Contact",
            "operation": "create",
            "fields": {
                "LastName": "form:last_name"
            }
        }
    ]
"""),
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
                    "operation": {"type": "string", "enum": ["create", "update"]},
                    "match_expression": {"type": "string"},
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
