from collective.tiles.carousel import _
from collective.tiles.carousel.base import BaseSliderTile
from collective.tiles.carousel.base import ISliderBase
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary


class ISliderTile(ISliderBase):
    """A tile that shows a slider."""

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

    namespace = schema.Choice(
        title=_("Theme"),
        description=_("Select one of the default themes."),
        default="centered-btns",
        vocabulary=SimpleVocabulary(
            [
                SimpleVocabulary.createTerm(
                    "centered-btns",
                    "centered-btns",
                    _("Centered Buttons"),
                ),
                SimpleVocabulary.createTerm(
                    "transparent-btns",
                    "transparent-btns",
                    _("Transparent Buttons"),
                ),
                SimpleVocabulary.createTerm(
                    "large-btns",
                    "large-btns",
                    _("Large Buttons"),
                ),
            ]
        ),
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


class SliderTile(BaseSliderTile):
    """A tile that shows a slider."""
