from collective.easyform.api import get_actions
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import IEasyFormForm
from dateutil.parser import parse
from simple_salesforce import Salesforce
from z3c.form.interfaces import IValue
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import IField
from zope.schema.interfaces import IDate

from .action import SF_CREDENTIALS
from .interfaces import IJazkartaEasyformpluginSalesforceLayer
from .interfaces import ISaveToSalesforce


@adapter(
    IEasyForm, IJazkartaEasyformpluginSalesforceLayer, IEasyFormForm, IField, Interface
)
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
                fields = operation.get("fields", {})
                for sf_field, expr in fields.items():
                    if expr == "form:%s" % field.__name__:
                        return SalesforcePrefillValue(form, field, operation, sf_field)

    # Didn't find one, so return None
    # so that the IValue adapter lookup continues to the next one
    return None


@implementer(IValue)
class SalesforcePrefillValue(object):
    def __init__(self, form, field, operation, sf_field):
        self.form = form
        self.field = field
        self.operation = operation
        self.sf_field = sf_field

        self.request = getRequest()
        if not hasattr(self.request, "_jazkarta_easyform_sf_queries"):
            self.request._jazkarta_easyform_sf_queries = {}
        self.query_cache = self.request._jazkarta_easyform_sf_queries

    def query(self):
        fields = sorted(self.operation["fields"].keys())
        if "Id" not in fields:
            fields = ["Id"] + fields
        sobject = self.operation["sobject"]
        where = self.operation["match_expression"]
        soql = "SELECT {} FROM {} WHERE {}".format(", ".join(fields), sobject, where)
        if soql not in self.query_cache:
            sf = Salesforce(**SF_CREDENTIALS)
            result = sf.query(soql)
            if result["totalSize"] != 1:
                raise Exception("Didn't find match")
            self.query_cache[soql] = result["records"][0]
        item = self.query_cache[soql]
        self.request.response.setCookie(
            "sf_id", item["Id"], path=self.form.absolute_url_path()
        )
        return item

    def get(self):
        value = self.query().get(self.sf_field)
        if value and IDate.providedBy(self.field):
            value = parse(value)
        return value


# to do:
# - sign the cookie
# - use object from cookie if form was submitted with an error
# - handle no match / multiple matches
# - handle dynamic match expressions
