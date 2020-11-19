"""Setup tests for this package."""
from collective.tiles.carousel.testing import (  # noqa: E501,
    COLLECTIVE_TILES_CAROUSEL_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.tiles.carousel is properly installed."""

    layer = COLLECTIVE_TILES_CAROUSEL_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.tiles.carousel is installed."""
        self.assertTrue(
            self.installer.isProductInstalled("collective.tiles.carousel")
        )

    def test_browserlayer(self):
        """Test that ICollectiveTilesCarouselLayer is registered."""
        from collective.tiles.carousel.interfaces import (
            ICollectiveTilesCarouselLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(ICollectiveTilesCarouselLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_TILES_CAROUSEL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["collective.tiles.carousel"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.tiles.carousel is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled("collective.tiles.carousel")
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveTilesCarouselLayer is removed."""
        from collective.tiles.carousel.interfaces import (
            ICollectiveTilesCarouselLayer,
        )
        from plone.browserlayer import utils

        self.assertNotIn(
            ICollectiveTilesCarouselLayer, utils.registered_layers()
        )
