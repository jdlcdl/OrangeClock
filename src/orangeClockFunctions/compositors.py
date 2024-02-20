from gui.core.writer import Writer
from gui.widgets.label import Label

import gui.fonts.orangeClockIcons25 as iconsSmall
import gui.fonts.orangeClockIcons35 as iconsLarge
import gui.fonts.libreFranklinBold50 as large
import gui.fonts.libreFranklinSemiBold29 as small


# use _setup with an ssd instance to setup writers
wri_iconsLarge = None
wri_iconsSmall = None
wri_large = None
wri_small = None
def _setup(ssd):
    global wri_iconsLarge
    wri_iconsLarge = Writer(ssd, iconsLarge, verbose=False)

    global wri_iconsSmall
    wri_iconsSmall = Writer(ssd, iconsSmall, verbose=False)

    global wri_large
    wri_large = Writer(ssd, large, verbose=False)

    global wri_small
    wri_small = Writer(ssd, small, verbose=False)


# compose three horizontally-centered rows, each having text + icon
def composeClock(ssd, first, second, third):
    """
    pass: ssd, first, second, and third 
    where ssd is the display instance and first, second, third are
    tuples of (text, icon), where text and icon are the 
    text string and icon char to be rendered.

    returns list of Labels
    """
    # setup the writers if not already done
    if None in (wri_iconsLarge, wri_iconsSmall, wri_large, wri_small):
        _setup(ssd)

    # text and icon writers for row1, row2, row3
    icon_writers = (wri_iconsSmall, wri_iconsLarge, wri_iconsSmall)
    text_writers = (wri_small, wri_large, wri_small)

    # text and icon vertical position y-offsets for row1, row2, and row3
    text_y_offsets = (5, 44, 98) 
    icon_y_offsets = (7, 49, 99) 

    # spacing between text and icon for row1, row2, and row3
    spacings = (4, 0, 4)

    labels = []
    for i, (text, icon) in enumerate([first, second, third]):
        icon_width = icon_writers[i].stringlen(icon)
        text_width = text_writers[i].stringlen(text)

        # write the text
        labels.append(Label(
            text_writers[i],
            text_y_offsets[i],
            (ssd.width - text_width + icon_width + spacings[i]) // 2,
            text
        ))

        # write the icon
        labels.append(Label(
            icon_writers[i],
            icon_y_offsets[i],
            (ssd.width - text_width - icon_width - spacings[i]) // 2,
            icon
        ))

    return labels


# compose three left-justified rows, each having text + icon
def composeSetup(ssd, first, second, third):
    """
    pass: ssd, first, second, and third 
    where ssd is the display instance and first, second, third are
    tuples of (text, icon), where text and icon are the 
    text string and icon char to be rendered.

    returns list of Labels
    """
    # setup the writers if not already done
    if None in (wri_iconsLarge, wri_iconsSmall, wri_large, wri_small):
        _setup(ssd)

    # text and icon writers for row1, row2, row3
    icon_writer = wri_iconsSmall
    text_writer = wri_small

    # text and icon vertical position y-offsets for row1, row2, and row3
    text_y_offsets = (5, 49, 85) 
    icon_y_offsets = (7, 49, 86) 

    x_offset = 10 
    spacing = 4

    labels = []
    for i, (text, icon) in enumerate([first, second, third]):
        icon_width = icon_writer.stringlen(icon)

        # write the text
        labels.append(Label(
            text_writer,
            text_y_offsets[i],
            x_offset + icon_width + spacing,
            text
        ))

        # write the icon
        labels.append(Label(
            icon_writer,
            icon_y_offsets[i],
            x_offset,
            icon
        ))

    return labels