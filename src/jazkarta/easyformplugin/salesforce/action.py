import logging
import os

from collective.easyform.actions import Action, ActionFactory
from collective.easyform.api import get_context, get_expression
from DateTime import DateTime
from plone.supermodel.exportimport import BaseHandler
from Products.CMFCore.Expression import Expression, getExprContext
from Products.CMFCore.utils import getToolByName
from simple_salesforce import Salesforce
from zope.interface import implementer

from . import _
from .interfaces import ISaveToSalesforce

logger = logging.getLogger(__name__)

SF_CREDENTIALS = {
    "username": os.environ.get("SALESFORCE_USERNAME"),
    "password": os.environ.get("SALESFORCE_PASSWORD"),
    "security_token": os.environ.get("SALESFORCE_TOKEN"),
    "domain": os.environ.get("SALESFORCE_DOMAIN"),
}

@implementer(ISaveToSalesforce)
class SendToSalesforce(Action):

    def __init__(self, **kw):
        for name, field in ISaveToSalesforce.namesAndDescriptions():
            setattr(self, name, kw.pop(name, field.default))
        super(SendToSalesforce, self).__init__(**kw)

    def get_form(self):
        return get_context(self)

    def onSuccess(self, fields, request):
        form = self.get_form()
        expr_context = getExprContext(form, form)
        sf = Salesforce(**SF_CREDENTIALS)

        for operation in self.operations:
            sobject_name = operation["sobject"]
            data = self.prepare_salesforce_data(operation["fields"], fields, expr_context)
            sobject = getattr(sf, sobject_name)
            op_name = operation["operation"]
            if op_name == "create":
                result = sobject.create(data)
                if result["success"]:
                    sf_id = result["id"]
                    logger.info(u"Created {} {} in Salesforce".format(sobject_name, sf_id))
                else:
                    raise Exception(u"Failed to create {} in Salesforce: {}".format(sobject_name, result["errors"]))
            else:
                raise ValueError("Unsupported operation: {}".format(operation))

    def prepare_salesforce_data(self, fields, form_input, expr_context):
        """Collect data for one Salesforce object in the format expected by simple-salesforce

        sobject - API name (developer name) of the sObject in Salesforce
        fields - mapping from Salesforce field name to an expression for calculating the value
        request - the request object containing submitted form data
        expr_context - CMFCore expression context for evaluating TALES expressions

        Several types of expression are supported:

        * "form:name" - Get the value that was entered in the form input called "name"
        """
        data = {}
        for sf_fieldname, value in fields.items():
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
            data[sf_fieldname] = value
        return data


SendToSalesforceAction = ActionFactory(
    SendToSalesforce,
    _(u"label_salesforce_action", default=u"Send to Salesforce"),
    "jazkarta.easyformplugin.salesforce.AddSalesforceActions",
)


SendToSalesforceHandler = BaseHandler(SendToSalesforce)
