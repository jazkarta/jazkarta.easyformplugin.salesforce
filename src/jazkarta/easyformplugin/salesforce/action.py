import logging

from collective.easyform.actions import Action, ActionFactory
from collective.easyform.api import get_context, get_expression
from DateTime import DateTime
from plone.supermodel.exportimport import BaseHandler
from Products.CMFCore.Expression import Expression, getExprContext
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer

from . import _
from .interfaces import ISaveToSalesforce

logger = logging.getLogger(__name__)


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
        sf = getToolByName(form, "portal_salesforcebaseconnector")

        for operation in self.operations:
            sobject = operation["sobject"]
            data = self.prepare_salesforce_data(sobject, operation["fields"], fields, expr_context)
            import pdb; pdb.set_trace()
            op_name = operation["operation"]
            if op_name == "create":
                result = sf.create(data)[0]
                if result["success"]:
                    sf_id = result["id"]
                    logger.info(u"Created {} {} in Salesforce".format(sobject, sf_id))
                else:
                    err = result["errors"][0]["message"]
                    raise Exception(u"Failed to create {} in Salesforce: {}".format(sobject, err))
            else:
                raise ValueError("Unsupported operation: {}".format(operation))

    def prepare_salesforce_data(self, sobject, fields, form_input, expr_context):
        """Collect data for one Salesforce object in the format expected by salesforcebaseconnector

        sobject - API name (developer name) of the sObject in Salesforce
        fields - mapping from Salesforce field name to an expression for calculating the value
        request - the request object containing submitted form data
        expr_context - CMFCore expression context for evaluating TALES expressions

        Several types of expression are supported:

        * "form:name" - Get the value that was entered in the form input called "name"
        """
        data = {"type": sobject}
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
