import logging

from collective.easyform.actions import Action, ActionFactory
from plone.supermodel.exportimport import BaseHandler
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

    def onSuccess(self, fields, request):
        logger.info(fields)


SendToSalesforceAction = ActionFactory(
    SendToSalesforce,
    _(u"label_salesforce_action", default=u"Send to Salesforce"),
    "jazkarta.easyformplugin.salesforce.AddSalesforceActions",
)


SendToSalesforceHandler = BaseHandler(SendToSalesforce)
