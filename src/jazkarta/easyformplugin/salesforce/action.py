from datetime import date, datetime
import json
import logging
import os

from collective.easyform.actions import Action, ActionFactory
from collective.easyform.api import get_context, get_expression
from DateTime import DateTime
from plone.app.event.base import default_timezone
from plone.supermodel.exportimport import BaseHandler
from simple_salesforce import Salesforce
from zope.interface import implementer

from . import _
from .interfaces import ISaveToSalesforce

logger = logging.getLogger(__name__)

SF_CREDENTIALS = {
    "username": os.environ.get("SALESFORCE_USERNAME"),
    "password": os.environ.get("SALESFORCE_PASSWORD"),
    "security_token": os.environ.get("SALESFORCE_TOKEN"),
    "domain": os.environ.get("SALESFORCE_DOMAIN")
    or (
        "test"
        if os.environ.get("SALESFORCE_SANDBOX", "true").lower() in ("true", "1")
        else "login"
    ),
    "version": "55.0",
}


@implementer(ISaveToSalesforce)
class SendToSalesforce(Action):
    """easyform action which creates or updates a record in Salesforce

    Configured with one field, `operations`, which is a JSON list of operations to perform.
    Each operation specifies:
    * sobject - name of the Salesforce sObject
    * operation - what operation to perform (`create` is currently the only supported operation)
    * fields - a mapping of Salesforce field names to expressions.

    Each field expression can be one of:
    * "form:x" -- value of the form field named `x`
    * "path:x" -- a TALES path expression
    * "python:x" -- a TALES Python expression
    * "string:x" -- a TALES string expression
    """

    def __init__(self, **kw):
        for name, field in ISaveToSalesforce.namesAndDescriptions():
            setattr(self, name, kw.pop(name, field.default))
        super(SendToSalesforce, self).__init__(**kw)

    def get_form(self):
        return get_context(self)

    def onSuccess(self, fields, request):
        """Call Salesforce after a valid form submission.

        `fields` contains a mapping of the extracted form data.
        """
        form = self.get_form()
        sf = Salesforce(**SF_CREDENTIALS)

        for operation in self.operations:
            sobject_name = operation["sobject"]
            data = self.prepare_salesforce_data(operation["fields"], fields, form)
            logger.info(json.dumps(data, indent=4))
            sobject = getattr(sf, sobject_name)
            op_name = operation["operation"]
            if op_name == "create":
                self._create_sf_object(sobject, data)
            elif op_name == "update":
                sf_id = request.cookies.get("sf_id")
                if sf_id:
                    status = sobject.update(sf_id, data)
                    if status == 204:
                        request.response.expireCookie(
                            "sf_id", path=form.absolute_url_path()
                        )
                        logger.info(
                            "Updated {} {} in Salesforce".format(sobject_name, sf_id)
                        )
                    else:
                        raise Exception(
                            "Failed to update {} {} in Salesforce: {}".format(
                                sobject_name, sf_id, status
                            )
                        )
                else:
                    if operation.get("action_if_no_existing_object") == "create":
                        self._create_sf_object(sobject, data)
                    else:
                        raise Exception("No Salesforce object matched for update")
            else:
                raise ValueError("Unsupported operation: {}".format(operation))

    def _create_sf_object(self, sobject, data):
        result = sobject.create(data)
        if result["success"]:
            sf_id = result["id"]
            logger.info(
                "Created {} {} in Salesforce".format(sobject.name, sf_id)
            )
        else:
            raise Exception(
                "Failed to create {} in Salesforce: {}".format(
                    sobject.name, result["errors"]
                )
            )
        return sf_id

    def prepare_salesforce_data(self, fields, form_input, expr_context):
        """Collect data for one Salesforce object in the format expected by simple-salesforce

        sobject - API name (developer name) of the sObject in Salesforce
        fields - mapping from Salesforce field name to an expression for calculating the value
        request - the request object containing submitted form data
        expr_context - context object for evaluating TALES expressions
        """
        data = {}
        for sf_fieldname, value in fields.items():
            if not sf_fieldname:
                continue
            # evaluate expressions
            expr = None
            if value.startswith("form:"):
                form_fieldname = value[5:]
                value = form_input.get(form_fieldname)
            elif value.startswith("path:"):
                expr = value[5:]
            elif value.startswith(("python:", "string:")):
                expr = value
            if expr is not None:
                value = get_expression(expr_context, expr, now=DateTime().ISO8601())

            if isinstance(value, datetime):
                # convert to timezone-aware datetime if necessary
                if value.tzinfo is None:
                    tzinfo = default_timezone(as_tzinfo=True)
                    value = tzinfo.localize(value)
            if isinstance(value, (date, datetime)):
                # serialize dates and datetimes (not handled by json.dumps)
                value = value.isoformat()
            elif isinstance(value, set):
                value = ";".join(value)

            data[sf_fieldname] = value
        return data


# Action factory used by the UI for adding a new easyform action
SendToSalesforceAction = ActionFactory(
    SendToSalesforce,
    _("label_salesforce_action", default="Send to Salesforce"),
    "jazkarta.easyformplugin.salesforce.AddSalesforceActions",
)


# Supermodel handler for serializing the action configuration to an XML model
SendToSalesforceHandler = BaseHandler(SendToSalesforce)
