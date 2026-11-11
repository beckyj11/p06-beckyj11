from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

STORAGE_PATH = abspath(join(dirname(__file__), "../course/images/"))


def get_context():
    cfg = Config(SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines.pil")
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
    cfg.STORAGE = "thumbor.storages.no_storage"
    return Context(config=cfg)


def test_resized_gif_keeps_transparent_background():
    engine = Engine(get_context())
    with open(join(STORAGE_PATH, "sticker.gif"), "rb") as image_file:
        buffer = image_file.read()
    engine.load(buffer, ".gif")
    engine.resize(240, 160)

    # Find a pixel that is opaque in the resized source, so the output can
    # be checked for opaque pixels that turned transparent.
    alpha = engine.image.convert("RGBA").getchannel("A")
    opaque_xy = next(
        (x, y)
        for y in range(160)
        for x in range(240)
        if alpha.getpixel((x, y)) == 255
    )

    img = Image.open(BytesIO(engine.read(".gif")))
    rgba = img.convert("RGBA")

    assert "transparency" in img.info
    assert rgba.getpixel((0, 0))[3] == 0
    assert rgba.getpixel(opaque_xy)[3] == 255
