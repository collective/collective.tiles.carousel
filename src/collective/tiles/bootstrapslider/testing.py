# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2

import collective.tiles.bootstrapslider


class CollectiveTilesBootstrapsliderLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.tiles.bootstrapslider)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.tiles.bootstrapslider:default')


COLLECTIVE_TILES_BOOTSTRAPSLIDER_FIXTURE = CollectiveTilesBootstrapsliderLayer()


COLLECTIVE_TILES_BOOTSTRAPSLIDER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_TILES_BOOTSTRAPSLIDER_FIXTURE,),
    name='CollectiveTilesBootstrapsliderLayer:IntegrationTesting',
)


COLLECTIVE_TILES_BOOTSTRAPSLIDER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_TILES_BOOTSTRAPSLIDER_FIXTURE,),
    name='CollectiveTilesBootstrapsliderLayer:FunctionalTesting',
)


COLLECTIVE_TILES_BOOTSTRAPSLIDER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_TILES_BOOTSTRAPSLIDER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveTilesBootstrapsliderLayer:AcceptanceTesting',
)
