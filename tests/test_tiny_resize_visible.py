# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image
from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.transformer_test_data import TestData
from thumbor.engines.pil import Engine
from thumbor.transformer import Transformer

COLORS = [
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 255),
    (0, 0, 255),
    (255, 0, 255),
    (255, 255, 255),
    (0, 0, 0),
]


def make_transparent_bars_png(width=16, height=16):
    # RGBA PNG with vertical colored bars on a transparent background,
    # like the rainbow.png source in issue #4.
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for x in range(width):
        for y in range(height):
            r, g, b = COLORS[x * len(COLORS) // width]
            img.putpixel((x, y), (r, g, b, 255))
    buffer = BytesIO()
    img.save(buffer, "PNG")
    return buffer.getvalue()


def transform_with_real_engine(data, png_bytes):
    ctx = data.to_context()
    real_engine = Engine(ctx)
    real_engine.load(png_bytes, ".png")
    real_engine.extension = ".png"
    ctx.modules.engine = real_engine
    ctx.request.engine = real_engine
    return ctx, real_engine


class TinyResizeVisibleTestCase(TestCase):
    @gen_test
    async def test_800x20_request_returns_visible_strip(self):
        data = TestData(
            source_width=16,
            source_height=16,
            target_width=800,
            target_height=20,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
        )
        ctx, real_engine = transform_with_real_engine(
            data, make_transparent_bars_png()
        )

        trans = Transformer(ctx)
        await trans.transform()

        image = real_engine.image.convert("RGBA")
        assert image.size == (800, 20)

        # Not blank: some pixels are opaque.
        alpha_extrema = image.getchannel("A").getextrema()
        assert alpha_extrema[1] > 0

        # Bars are visible: left edge and right edge differ in color.
        left = image.getpixel((0, 10))
        right = image.getpixel((799, 10))
        assert left != right

    @gen_test
    async def test_fit_in_wide_source_returns_visible_image(self):
        cases = [
            # (target_width, target_height, expected_size)
            (1, 1, (1, 1)),
            (100, 0, (100, 1)),
        ]
        for target_width, target_height, expected in cases:
            data = TestData(
                source_width=940,
                source_height=2,
                target_width=target_width,
                target_height=target_height,
                halign="center",
                valign="middle",
                focal_points=[],
                crop_left=None,
                crop_top=None,
                crop_right=None,
                crop_bottom=None,
                fit_in=True,
            )
            ctx, real_engine = transform_with_real_engine(
                data, make_transparent_bars_png(940, 2)
            )

            trans = Transformer(ctx)
            await trans.transform()

            image = real_engine.image.convert("RGBA")
            assert image.size == expected, (target_width, target_height)

            alpha_extrema = image.getchannel("A").getextrema()
            assert alpha_extrema[1] > 0, (target_width, target_height)
