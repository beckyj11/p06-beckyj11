# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerFringeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_round_corner_edge_is_antialiased(self):
        # With the transparent flag, the arc must fade through the alpha
        # channel. A hard, fully opaque edge means the arc is not smoothed.
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(60,255,255,255,1)",
            mode="RGBA",
        )

        alpha_histogram = image.getchannel("A").histogram()
        partial_alpha_pixels = sum(alpha_histogram[1:255])

        assert partial_alpha_pixels > 0, (
            "no partially transparent pixels on the rounded edge"
        )
