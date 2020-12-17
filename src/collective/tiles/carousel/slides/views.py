from collections import defaultdict
from collections import OrderedDict
import pdb
from collective.tiles.carousel import _
from collective.tiles.carousel.utils import parse_query_from_data
from collective.tiles.carousel.interfaces import ICollectiveTilesCarouselLayer
from operator import itemgetter
from plone import api
from plone.tiles import Tile
from plone.app.contenttypes.browser.link_redirect_view import NON_RESOLVABLE_URL_SCHEMES
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.app.querystring import queryparser
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives as form
from plone.dexterity.interfaces import IDexterityContainer
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.tiles.interfaces import IPersistentTile
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from Products.Five import BrowserView


class SlideView(BrowserView):


    def __call__(self, item, data):
        self.update(item, data)
        return self.index()

    def update(self, item, data):
        self.item = self.get_item_info(item, data)

    def get_item_info(self, obj, data):
        item = {}
        # item['obj'] = obj
        item['data'] = data
        item["title"] = obj.title
        # item["show_title"] = self.data['show_title']
        item["description"] = obj.description
        # item["show_description"] = self.data['show_description']
        item["tag"] = self.get_tag(obj, data)
        item["link"] = self.get_link(obj, data)
        item["type"] = obj.portal_type
        return item


    def get_tag(self, obj, data):
        scale_util = api.content.get_view("images", obj, self.request)
        return scale_util.tag(
            fieldname="image",
            mode=data.get("crop") and "cover" or "keep",
            scale=data.get("image_scale"),
            css_class=data.get("image_class"),
            alt=obj.description or obj.title,
        )

    def _url_uses_scheme(self, schemes, url=None):
        for scheme in schemes:
            if url.startswith(scheme):
                return True
        return False

    def get_link(self, obj, data):
        """Get target for linked slide."""

        # no linking
        if data.get("link_slides") == "disabled":
            return

        # link to parent
        if data.get("link_slides") == "collection":
            return obj.aq_parent.absolute_url()

        else:
            # link to external urls
            if getattr(obj, "remoteUrl", None):
                # Returns the url with link variables replaced.
                url = replace_link_variables_by_paths(obj, obj.remoteUrl)

                if self._url_uses_scheme(NON_RESOLVABLE_URL_SCHEMES, url=obj.remoteUrl):
                    # For non http/https url schemes, there is no path to resolve.
                    return url

                if url.startswith("."):
                    # we just need to adapt ../relative/links, /absolute/ones work
                    # anyway -> this requires relative links to start with ./ or
                    # ../
                    context_state = self.context.restrictedTraverse(
                        "@@plone_context_state"
                    )
                    url = "/".join([context_state.canonical_object_url(), url])
                else:
                    if not url.startswith(("http://", "https://")):
                        url = self.request["SERVER_URL"] + url
                return url

            # link to first related item
            if (
                len(getattr(obj, "relatedItems", [])) > 0
                and obj.relatedItems[0].to_object
            ):
                return obj.relatedItems[0].to_object.absolute_url()

            # link to object
            else:
                return obj.absolute_url()