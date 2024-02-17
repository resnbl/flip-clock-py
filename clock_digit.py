from enum import IntEnum
import PySimpleGUI as sg


class ClockNum(IntEnum):
    """ Used to indirectly reference ClockDigit internal objects """
    HR10 = 0
    HR01 = 1
    MIN10 = 2
    MIN01 = 3


class DispFmt(IntEnum):
    """ Clock display formats """
    HR24 = 0
    HR12 = 1
    HR12B = 2
    NUM_FMTS = 3


DEFAULT_FMT = DispFmt.HR12
IMG_PATH = './pngs'
MAX_STEP = 4                # number of steps (images) for a flip


class ClockDigit:
    """ Encapsulates a single digit of the flip clock """
    def __init__(self, key: str, digits='0123456789'):
        self.key = key          # psg Image key
        self.window: sg.Window | None = None    # psg window
        self.digits = digits    # list of digits to use (wrap around)
        self.curr_idx = 0       # index into digits for current digit
        self.next_idx = 0       # index for next digit when flipping
        self.step = 0           # flipping step

    def get_image_path(self) -> str:
        # filename format = <dir>/<current digit><next digit><step>.png
        curr_dig = self.digits[self.curr_idx]
        to_dig = self.digits[self.next_idx]
        return f'{IMG_PATH}/{curr_dig}{to_dig}{self.step}.png'

    def set(self, digit=0, window: sg.Window | None = None):
        """ Set new digit value and update display """
        if window:
            self.window = window
        self.curr_idx = digit % len(self.digits)
        self.next_idx = self.curr_idx
        self.step = 0
        self.update()

    def update(self):
        """ Re-draw digit image """
        self.window[self.key].update(filename=self.get_image_path())

    def do_step(self) -> bool:
        """ Update to next flipping image (maybe) """
        if self.curr_idx != self.next_idx:
            self.step += 1
            if self.step >= MAX_STEP:
                # flip done: draw final digit image
                self.curr_idx = self.next_idx
                self.step = 0
            self.update()
            return True
        else:
            return False

    def __str__(self):
        return f'Digit: {self.key=} {self.curr_idx=} {self.next_idx=} {self.step=}'


class ClockFace:
    """ Contain and process all 4 digits as a group """
    def __init__(self):
        self.hr10 = ClockDigit(key='-HR10s-', digits='01')      # assume DispFmt.HR12
        self.hr01 = ClockDigit(key='-HR1s-', digits='0123456789')
        self.min10 = ClockDigit(key='-MIN10s-', digits='012345')
        self.min01 = ClockDigit(key='-MIN1s-', digits='0123456789')
        self.stepping = False
        self.disp_fmt = DEFAULT_FMT
        self.set_disp_fmt(self.disp_fmt)

    def make_image(self, num: ClockNum) -> sg.Image:
        """ Called one at a time by PSG layout process """
        if num == ClockNum.HR10:
            return sg.Image(filename=self.hr10.get_image_path(), key=self.hr10.key, pad=(1, 2))
        elif num == ClockNum.HR01:
            return sg.Image(filename=self.hr01.get_image_path(), key=self.hr01.key, pad=(1, 2))
        elif num == ClockNum.MIN10:
            return sg.Image(filename=self.min10.get_image_path(), key=self.min10.key, pad=(1, 2))
        elif num == ClockNum.MIN01:
            return sg.Image(filename=self.min01.get_image_path(), key=self.min01.key, pad=(1, 2))

    def set_disp_fmt(self, fmt: DispFmt):
        """ Set display format to 24-hour, 12-hour, or 12-hour with leading blank """
        if fmt == DispFmt.HR24:
            self.hr10.digits = '012'
        elif fmt == DispFmt.HR12:
            self.hr10.digits = '01'
        else:
            self.hr10.digits = 'x1'
        self.disp_fmt = fmt

        # reset hours
        hours = self.hr10.curr_idx * 10 + self.hr01.curr_idx
        if fmt != DispFmt.HR24:
            if hours > 12:
                hours -= 12
            elif hours == 0:
                hours = 12

        self.hr10.curr_idx = self.hr10.next_idx = hours // 10
        self.hr01.curr_idx = self.hr01.next_idx = hours % 10
        self.hr10.step = self.hr01.step = 0

    def get_disp_fmt(self) -> DispFmt:
        return self.disp_fmt

    def is_stepping(self) -> bool:
        return self.stepping

    def set_digits(self, hours: int, mins: int, win: sg.Window):
        """ Override current hours/mins settings """
        if self.disp_fmt != DispFmt.HR24:
            if hours > 12:
                hours -= 12
            elif hours == 0:
                hours = 12

        self.hr10.set(hours // 10, win)
        self.hr01.set(hours % 10, win)
        self.min10.set(mins // 10, win)
        self.min01.set(mins % 10, win)

        self.stepping = False

    def update_digits(self, hours: int, mins: int):
        """ Set the .next_idx values to initiate stepping """
        if self.disp_fmt != DispFmt.HR24:
            if hours > 12:
                hours -= 12
            elif hours == 0:
                hours = 12

        self.hr10.next_idx = hours // 10
        self.hr01.next_idx = hours % 10
        self.min10.next_idx = mins // 10
        self.min01.next_idx = mins % 10

        self.hr10.step = self.hr01.step = 0
        self.min10.step = self.min01.step = 0

        self.stepping = True

    def do_step(self):
        """ Update to the next intra-digit frame """
        if self.stepping:   # check from low to high
            if (self.min01.do_step() or self.min10.do_step() or
                    self.hr01.do_step() or self.hr10.do_step()):
                pass
            else:
                self.stepping = False       # all digits flipped

    def draw_all(self):
        """ Force re-draw after significant hours/mins change """
        self.hr10.update()
        self.hr01.update()
        self.min10.update()
        self.min01.update()
