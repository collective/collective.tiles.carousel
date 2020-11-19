from collective.tiles.bootstrapslider import _
from collective.tiles.bootstrapslider.base import BaseSliderTile
from collective.tiles.bootstrapslider.base import ISliderBase
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

    link = schema.Choice(
        title=_("Slides with Links"),
        description=_("Collection will fallback to items if no collection available"),
        default="items",
        vocabulary=SimpleVocabulary(
            [
                SimpleVocabulary.createTerm(
                    "items",
                    "items",
                    _("to Items"),
                ),
                SimpleVocabulary.createTerm(
                    "collection",
                    "collection",
                    _("to Collection"),
                ),
                SimpleVocabulary.createTerm(
                    "disable",
                    "disable",
                    _("Disable"),
                ),
            ]
        ),
    )


class SliderTile(BaseSliderTile):
    """A tile that shows a slider."""
