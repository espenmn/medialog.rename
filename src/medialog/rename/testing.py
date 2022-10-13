# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import medialog.rename


class MedialogRenameLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=medialog.rename)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'medialog.rename:default')


MEDIALOG_RENAME_FIXTURE = MedialogRenameLayer()


MEDIALOG_RENAME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MEDIALOG_RENAME_FIXTURE,),
    name='MedialogRenameLayer:IntegrationTesting',
)


MEDIALOG_RENAME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MEDIALOG_RENAME_FIXTURE,),
    name='MedialogRenameLayer:FunctionalTesting',
)


MEDIALOG_RENAME_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MEDIALOG_RENAME_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='MedialogRenameLayer:AcceptanceTesting',
)
