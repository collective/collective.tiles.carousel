from collections import OrderedDict
from collective.tiles.carousel.utils import parse_query_from_data
from collective.tiles.sliders import _
from plone import api
from plone import tiles
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
from plone.supermodel.model import Schema
from plone.tiles.interfaces import IPersistentTile
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getUtilitiesFor
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def image_scales(context):
    """Return custom source for image scales.

    This source also contains the original image.
    """
    values = []
    values.append(SimpleTerm("original", "original", _("Original")))
    allowed_sizes = api.portal.get_registry_record(name="plone.allowed_sizes")
    for allowed_size in allowed_sizes:
        name = allowed_size.split()[0]
        values.append(SimpleTerm(name, name, allowed_size))
    return SimpleVocabulary(values)


class ISliderBase(Schema):
    """Basic Image Tile Schema."""

    carousel_items = RelationList(
        title=_("Carousel Items"),
        description=_(
            "Manually select images or folders of images to display in slider.",
        ),
        default=[],
        value_type=RelationChoice(
            title=u"Carousel Items", vocabulary="plone.app.vocabularies.Catalog"
        ),
        required=False,
    )

    form.widget(
        "carousel_items",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "orderable": True,
            "recentlyUsed": True,
        },
    )

    form.widget("query", QueryStringFieldWidget)
    query = schema.List(
        title=_("Search terms"),
        description=_(
            "Define the search terms for the items you want to use.",
        ),
        required=False,
        value_type=schema.Dict(
            value_type=schema.Field(),
            key_type=schema.TextLine(),
        ),
    )

    sort_on = schema.TextLine(
        description=_(u"Sort on this index"),
        required=False,
        title=_(u"Sort on"),
    )

    sort_reversed = schema.Bool(
        description=_(u"Sort the results in reversed order"),
        required=False,
        title=_(u"Reversed order"),
    )

    image_scale = schema.Choice(
        title=_("Image Scale"),
        source=image_scales,
        default="large",
    )

    crop = schema.Choice(
        title=_("Crop Images"),
        description=_("Collection will fallback to items if no collection available"),
        vocabulary=SimpleVocabulary(
            [
                SimpleVocabulary.createTerm(
                    "keep",
                    "keep",
                    _("disabled"),
                ),
                SimpleVocabulary.createTerm(
                    "scale-crop-to-fill",
                    "scale-crop-to-fill",
                    _("cover"),
                ),
                SimpleVocabulary.createTerm(
                    "scale-crop-to-fit",
                    "scale-crop-to-fit",
                    _("contain"),
                ),
            ]
        ),
    )

    image_class = schema.TextLine(
        title=_("Image Class"),
        default="d-block w-100",
        required=False,
    )


class BaseTile(tiles.Tile):
    """Base tile implementation."""

    @property
    def title(self):
        return self.data.get("title", None)

    @property
    @view.memoize
    def site(self):
        return api.portal.get()

    @property
    @view.memoize
    def catalog(self):
        return api.portal.get_tool(name="portal_catalog")


@implementer(IPersistentTile)
class BaseSliderTile(BaseTile):
    """An base slider tile."""

    sort_limit = 0

    def render(self):
        return self.index()

    @property
    def query(self):
        parsed = parse_query_from_data(self.data, self.context)
        if self.sort_limit:
            parsed["sort_limit"] = self.sort_limit
        return parsed

    @property
    @view.memoize
    def image_sizes(self):
        values = []
        allowed_sizes = api.portal.get_registry_record(
            name="plone.allowed_sizes",
        )
        for allowed_size in allowed_sizes:
            name = allowed_size.split()[0]
            values.append(name)
        return values

    def parse_query_from_data(data, context=None):
        """Parse query from data dictionary"""
        if context is None:
            context = api.portal.get()
        query = data.get("query", {}) or {}
        try:
            parsed = queryparser.parseFormquery(context, query)
        except KeyError:
            parsed = {}

        index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
        for name, modifier in index_modifiers:
            if name in parsed:
                new_name, query = modifier(parsed[name])
                parsed[name] = query
                # if a new index name has been returned, we need to replace
                # the native ones
                if name != new_name:
                    del parsed[name]
                    parsed[new_name] = query

        if data.get("sort_on"):
            parsed["sort_on"] = data["sort_on"]
        if data.get("sort_reversed", False):
            parsed["sort_order"] = "reverse"
        return parsed

    @property
    def items(self):
        items = OrderedDict()
        if "carousel_items" in self.data:
            for item in self.data["carousel_items"]:
                if ICollection.providedBy(item.to_object):
                    items.update(
                        OrderedDict.fromkeys(
                            [
                                x.getObject()
                                for x in item.to_object.results(
                                    brains=True, batch=False
                                )
                            ]
                        )
                    )
                    continue
                if IDexterityContainer.providedBy(item.to_object):
                    items.update(
                        OrderedDict.fromkeys(
                            [
                                x.getObject()
                                for x in api.content.find(
                                    path="/".join(item.to_object.getPhysicalPath()),
                                    sort_on="getObjPositionInParent",
                                    depth=1,
                                )
                            ]
                        )
                    )
                    continue
                else:
                    items[item.to_object] = None

        if getattr(self, "query", None):
            items.update(
                OrderedDict.fromkeys(
                    [x.getObject() for x in api.content.find(**self.query)]
                )
            )
        result = []
        for obj in items.keys():
            result.append(self.get_item_info(obj))
        return result

    def get_item_info(self, obj):
        item = {}
        item["title"] = obj.title
        item["description"] = obj.description
        item["tag"] = self.get_tag(obj)
        item["link"] = self.get_link(obj)
        item["type"] = obj.portal_type
        return item

    def get_tag(self, obj):
        scale_util = api.content.get_view("images", obj, self.request)
        return scale_util.tag(
            fieldname="image",
            mode=self.data.get("crop"),
            scale=self.data.get("image_scale"),
            css_class=self.data.get("image_class"),
            alt=obj.description or obj.title,
        )

    def _url_uses_scheme(self, schemes, url=None):
        for scheme in schemes:
            if url.startswith(scheme):
                return True
        return False

    def get_link(self, obj):
        """Get target for linked slide."""
        if self.data.get("link_slides") == "disabled":
            return
        if self.data.get("link_slides") == "collection":
            return obj.aq_parent.absolute_url()
        else:
            # Link object
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
            if getattr(obj, "relatedItems", None):
            if len(getattr(obj, "relatedItems", [])) > 0 and obj.relatedItems[0].to_object:
                return obj.relatedItems[0].to_object.absolute_url()
            else:
                return obj.absolute_url()
