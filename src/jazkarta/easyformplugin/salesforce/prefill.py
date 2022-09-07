from collective.easyform.api import get_actions
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import IEasyFormForm
from z3c.form.interfaces import IValue
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import IField

from .interfaces import IJazkartaEasyformpluginSalesforceLayer
from .interfaces import ISaveToSalesforce


@adapter(IEasyForm, IJazkartaEasyformpluginSalesforceLayer, IEasyFormForm, IField, Interface)
def prefill_value_factory(context, request, view, field, widget):
    """Return a SalesforcePrefillValue if and only if there is a
    Salesforce action mapping the field
    """
    form = context
    # todo: This is repeated for each field;
    # would be good to cache the actions
    for action in getFields(get_actions(form)).values():
        if ISaveToSalesforce.providedBy(action):
            for operation in action.operations:
                if operation.get("operation") != "update":
                    continue
                mapping_targets = operation.get("fields", {}).values()
                if "form:%s" % field.__name__ not in mapping_targets:
                    continue
                return SalesforcePrefillValue(form, field, operation)

    # Didn't find one, so return None
    # so that the IValue adapter lookup continues to the next one
    return None


from datetime import date

@implementer(IValue)
class SalesforcePrefillValue(object):

    def __init__(self, form, field, operation):
        self.form = form
        self.field = field
        self.operation = operation

    def get(self):
        return {
            "first_name": "",
            "last_name": "McTesterson",
            "do_not_call": True,
            "birthdate": date(1985, 9, 30),
        }.get(self.field.__name__)
