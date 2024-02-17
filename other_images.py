"""
Create a few static images so the flip-clock looks like a LilyGo T-Display S3
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib

# Fill in these values:
SCREEN_BG = "black"                         # screen background (black)
DIGIT_BG = "#696969"                        # digits background (dim gray?)
OUT_PATH = 'pngs/'                          # output folder
OUT_FORM = 'png'                            # rgb565 | png | bmp | ...
BTN_FG = "orange"
BTN_PAD = 8
LOGO_COLOR = "#404040"
LOGO_FONT = "Roboto-Black.ttf"
# values from flip-digits.py
digit_w = 64
digit_h = 106


def save_image(image: Image, filename: str):
    """Save image in desired format"""
    image.save(pathlib.Path(f'{OUT_PATH}/{filename}.{OUT_FORM}'))


def make_button(top=True) -> Image:
    """ Make a orange button like the ones on the LilyGo T-Display S3 case.
        It should be 1/2 height of digit images so 1 can be stacked
        vertically next to them.
    """
    btn_img_w = digit_w // 2
    btn_img_h = digit_h // 2
    btn_w = btn_img_w - BTN_PAD * 2
    btn_h = btn_w
    btn_x0 = BTN_PAD
    btn_y0 = BTN_PAD if top else btn_img_h - BTN_PAD - btn_h
    img = Image.new("RGB", (btn_img_w, btn_img_h), color=SCREEN_BG)
    drw = ImageDraw.Draw(img)
    drw.ellipse(((btn_x0, btn_y0), (btn_x0 + btn_w, btn_y0 + btn_h)), fill=BTN_FG)
    return img


def make_logo() -> Image:
    """ Write the logo name in vertical text """
    btn_img_w = digit_h
    btn_img_h = digit_w // 2
    img = Image.new("RGB", (btn_img_w, btn_img_h), color=SCREEN_BG)
    drw = ImageDraw.Draw(img)
    fsize = btn_img_h - 4
    font = ImageFont.truetype(LOGO_FONT, fsize)
    drw.text((btn_img_w // 2, btn_img_h // 2), 'LILYGO', fill=LOGO_COLOR, font=font, anchor='mm')
    vert_img = img.transpose(Image.ROTATE_90)
    return vert_img


save_image(make_button(True), "top_button")
save_image(make_button(False), "bottom_button")
save_image(make_logo(), "logo")
