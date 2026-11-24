"""Draws the OrcaAudioCleanup app icon (the Windows app's clay waveform on a dark tile) on the macOS icon grid
and writes app/Resources/OrcaAudioCleanup.icns plus a 1024 px preview. Runs anywhere with Pillow:

    python packaging/icon/make_icns.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parents[2]
ICNS = REPO / "app" / "Resources" / "OrcaAudioCleanup.icns"
PREVIEW = REPO / "packaging" / "icon" / "OrcaAudioCleanup-1024.png"

CANVAS = 1024
TILE_INSET = 100  # the macOS grid: an 824 px tile centred on 1024, room for the shadow
TILE_RADIUS = 0.225
TILE = (20, 22, 26, 255)
CLAY = (217, 119, 87, 255)
# Bars of the Windows icon (windows_app/ui/icon.png), as fractions of its 241 px tile: centre x, top, bottom.
BAR_WIDTH = 21 / 241
BARS = ((38, 110, 146), (68, 95, 161), (98, 68, 188), (128, 87, 169), (158, 57, 199), (188, 83, 173), (218, 102, 154))
SOURCE_TILE_ORIGIN = 8
SOURCE_TILE_SIZE = 241


def draw(size: int = CANVAS) -> Image.Image:
    scale = size / CANVAS
    inset, tile = TILE_INSET * scale, (CANVAS - 2 * TILE_INSET) * scale
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (inset, inset + 0.02 * tile, inset + tile, inset + tile + 0.02 * tile), TILE_RADIUS * tile, fill=(0, 0, 0, 90))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(0.03 * tile)))

    pen = ImageDraw.Draw(image)
    pen.rounded_rectangle((inset, inset, inset + tile, inset + tile), TILE_RADIUS * tile, fill=TILE)
    width = BAR_WIDTH * tile
    for centre, top, bottom in BARS:
        x = inset + (centre - SOURCE_TILE_ORIGIN) / SOURCE_TILE_SIZE * tile
        y0 = inset + (top - SOURCE_TILE_ORIGIN) / SOURCE_TILE_SIZE * tile
        y1 = inset + (bottom - SOURCE_TILE_ORIGIN) / SOURCE_TILE_SIZE * tile
        pen.rounded_rectangle((x - width / 2, y0, x + width / 2, y1), width / 2, fill=CLAY)
    return image


def main() -> None:
    icon = draw()
    icon.save(PREVIEW)
    icon.save(ICNS, sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)])
    print(ICNS)


if __name__ == "__main__":
    main()
