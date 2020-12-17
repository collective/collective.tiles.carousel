from collections import defaultdict
from collections import OrderedDict
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


class ISliderTile(Schema):
    """A tile that shows a slider."""

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

    crop = schema.Bool(title=_("Crop Images"), required=False, default=True)

    image_class = schema.TextLine(
        title=_("Image Class"),
        default="d-block w-100",
        required=False,
    )

    controls = schema.Bool(
        title=_("Show Controls"),
        required=False,
        default=False,
    )

    indicators = schema.Bool(
        title=_("Show Indicators"),
        required=False,
        default=False,
    )

    darkvariant = schema.Bool(
        title=_("Use Dark Variant"),
        required=False,
        default=False,
    )

    crossfade = schema.Bool(
        title=_("Use Crossfade"),
        required=False,
        default=False,
    )

    carousel_speed = schema.Int(
        title=_("Carousel Speed"),
        description=_("Carousel speed in milliseconds, enter 0 to disable autoplay."),
        default=0,
    )

    show_title = schema.Bool(
        title=_("Show Title"),
        required=False,
        default=False,
    )

    show_description = schema.Bool(
        title=_("Show Description"),
        required=False,
        default=False,
    )

    link_slides = schema.Choice(
        title=_("Link slide"),
        description=_("Collection will fallback to items if no collection available"),
        default="item",
        vocabulary=SimpleVocabulary(
            [
                SimpleVocabulary.createTerm(
                    "item",
                    "item",
                    _("to Item"),
                ),
                SimpleVocabulary.createTerm(
                    "collection",
                    "collection",
                    _("to Collection"),
                ),
                SimpleVocabulary.createTerm(
                    "disabled",
                    "disabled",
                    _("Disable"),
                ),
            ]
        ),
    )

    slider_template = schema.Choice(
        title=_(u"Display mode"),
        source=_(u"Available Slider Views"),
        default="slider_view",
        required=True,
    )


@implementer(IPersistentTile)
class SliderTile(Tile):
    """A tile that shows a slider."""

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
        # item['obj'] = obj
        item['data'] = self.data
        item["title"] = obj.title
        # item["show_title"] = self.data['show_title']
        item["description"] = obj.description
        # item["show_description"] = self.data['show_description']
        item["tag"] = self.get_tag(obj)
        item["link"] = self.get_link(obj)
        item["type"] = obj.portal_type
        return item

    def get_tag(self, obj):
        scale_util = api.content.get_view("images", obj, self.request)
        return scale_util.tag(
            fieldname="image",
            mode=self.data.get("crop") and "cover" or "keep",
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

        # no linking
        if self.data.get("link_slides") == "disabled":
            return

        # link to parent
        if self.data.get("link_slides") == "collection":
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

    def item_view(self, item):

        # view = self.view_template or "slide_view"
        # import pdb; pdb.set_trace()
        view = "slide_view"
        options = dict(original_context=self.context)
        options['item'] = item
        options['item'] = item
        alsoProvides(self.request, ICollectiveTilesCarouselLayer)
        return getMultiAdapter((self.context, self.request), name=view)(**options)


@provider(IVocabularyFactory)
def availableSliderViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""

    registry = getUtility(IRegistry)
    listing_views = registry.get("collective.tiles.carousel.slider_views", {})
    if len(listing_views) == 0:
        listing_views = {
            "slider_view": u"Slider view",
            "full_view": u"Full view",
        }
    voc = []
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)
