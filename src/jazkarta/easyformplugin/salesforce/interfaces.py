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
        description=_(u"help_salesforce_operations", default=u"""<p>A JSON list of operations to perform.</p>

    <p>Each operation must specify:</p>
    <ul>
      <li>sobject - name of the Salesforce sObject</li>
      <li>operation - what operation to perform (`create` is currently the only supported operation)</li>
      <li>fields - a mapping of Salesforce field names to expressions.</li>

    <p>Each field expression can be one of:</p>
    <ul>
      <li>"form:x" -- value of the form field named `x`</li>
      <li>"path:x" -- a TALES path expression</li>
      <li>"python:x" -- a TALES Python expression</li>
      <li>"string:x" -- a TALES string expression</li>
    </ul>

    <p>Example:</p>
    <pre>
    [
        {
            "sobject": "Contact",
            "operation": "create",
            "fields": {
                "LastName": "form:last_name"
            }
        }
    ]
    </pre>
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
                    "action_if_no_existing_object": {"type": "string", "enum": ["abort", "create"]},
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
