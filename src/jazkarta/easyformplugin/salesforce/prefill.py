from collective.easyform.api import get_actions
from collective.easyform.api import get_expression
from collective.easyform.interfaces import IEasyForm
from collective.easyform.interfaces import IEasyFormForm
from collective.easyform.fields import superAdapter
from DateTime import DateTime
from dateutil.parser import parse
from simple_salesforce import Salesforce
from z3c.form.interfaces import IGroup
from z3c.form.interfaces import IValue
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import IField
from zope.schema.interfaces import IDate
from zope.schema.interfaces import ISet

from .action import SF_CREDENTIALS
from .interfaces import IJazkartaEasyformpluginSalesforceLayer
from .interfaces import ISaveToSalesforce


def _prefill_value_factory(adapter, context, request, view, field, widget):
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
                        adapter = SalesforcePrefillValue(form, field, operation, sf_field)

    value = adapter.get()
    if value is not None:
        return adapter

    # Didn't find a value, fall back to less specific adapter
    adapter = superAdapter(
        IJazkartaEasyformpluginSalesforceLayer,
        adapter,
        (context, request, view, field, widget),
        name="default",
    )
    if adapter is not None:
        return adapter


# Register default value adapter for easyform forms
@adapter(IEasyForm, IJazkartaEasyformpluginSalesforceLayer, IEasyFormForm, IField, Interface)
def form_prefill_value_factory(context, request, view, field, widget):
    return _prefill_value_factory(form_prefill_value_factory, context, request, view, field, widget)


# Register the same thing for fields in fieldsets
@adapter(IEasyForm, IJazkartaEasyformpluginSalesforceLayer, IGroup, IField, Interface)
def group_prefill_value_factory(context, request, view, field, widget):
    return _prefill_value_factory(group_prefill_value_factory, context, request, view, field, widget)


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
        fields = sorted(f for f in self.operation["fields"].keys() if f)
        if "Id" not in fields:
            fields = ["Id"] + fields
        sobject = self.operation["sobject"]
        where = self.operation["match_expression"]
        if where.startswith("python:"):
            where = get_expression(self.form, where, now=DateTime().ISO8601(), sanitize_soql=sanitize_soql)
        if not where:
            if self.operation.get("action_if_no_existing_object") == "create":
                return {}
            else:
                raise Exception("Not querying Salesforce, because match_expression is empty")
        soql = "SELECT {} FROM {} WHERE {}".format(", ".join(fields), sobject, where)
        item = self.query_cache.get(soql)
        if item is None:
            sf = Salesforce(**SF_CREDENTIALS)
            result = sf.query(soql)
            if result["totalSize"] > 1:
                raise Exception("Found multiple matches: %s" % soql)
            elif result["totalSize"] == 0:
                if self.operation.get("action_if_no_existing_object") == "create":
                    item = {}
                else:
                    raise Exception("Didn't find match: %s" % soql)
            else:
                item = result["records"][0]
                self.request.response.setCookie(
                    "sf_id", item["Id"], path=self.form.absolute_url_path()
                )
            self.query_cache[soql] = item
        return item

    def get(self):
        value = self.query().get(self.sf_field)
        if value:
            if IDate.providedBy(self.field):
                value = parse(value)
            elif ISet.providedBy(self.field):
                value = set(value.split(';'))
        return value


def sanitize_soql(s):
    """ Sanitizes a string that will be interpolated into single quotes
        in a SOQL expression.
    """
    return s.replace("'", "\\'")

# to do:
# - sign the cookie
# - use object from cookie if form was submitted with an error
