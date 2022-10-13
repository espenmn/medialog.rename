# -*- coding: utf-8 -*-
from medialog.rename.testing import MEDIALOG_RENAME_FUNCTIONAL_TESTING
from medialog.rename.testing import MEDIALOG_RENAME_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletType
from zope.component import getUtility

import unittest


class PortletIntegrationTest(unittest.TestCase):

    layer = MEDIALOG_RENAME_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.app.REQUEST
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_rename_is_registered(self):
        portlet = getUtility(
            IPortletType,
            name='medialog.rename.portlets.Rename',
        )
        self.assertEqual(portlet.addview, 'medialog.rename.portlets.Rename')


class PortletFunctionalTest(unittest.TestCase):

    layer = MEDIALOG_RENAME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
