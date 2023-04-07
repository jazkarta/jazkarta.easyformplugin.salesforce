# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("jazkarta.easyformplugin.salesforce")


# Make sure migrators are registered
from . import migration
