from enum import IntEnum
import PySimpleGUI as sg


class DispFmt(IntEnum):
    """ Clock display formats """
    HR24 = 0
    HR12 = 1
    HR12B = 2
    NUM_FMTS = 3


IMG_PATH = './pngs'
MAX_STEP = 4                # number of steps (images) for a flip


class ClockDigit:
    """ Encapsulates a single digit of the flip clock """
    def __init__(self, key: str, digits='0123456789'):
        self.key = key          # psg Image key
        self.digits = digits    # list of digits to use (wrap around)
        self.curr_idx = 0       # index into digits for current digit
        self.next_idx = 0       # index for next digit when flipping
        self.step = 0           # flipping step

    def set_digit_list(self, digits: str):
        """ Set the list of available digit characters to be displayed.
            This is always 0-9 for "units" digits, but "tens" digits are
            usually restricted to fewer characters (0-1, 0-2, 0-5).
            'x' is used to stand in for a blank to avoid filesystem issues.
        """
        self.digits = digits
        if self.curr_idx >= len(self.digits) or self.next_idx >= len(self.digits):
            # reset if currently out-of-range
            self.curr_idx = self.next_idx = self.step = 0

    def set_digit(self, digit=0, may_step=False):
        """ Set the next digit to "flip" to, and the current digit if not stepping. """
        self.next_idx = digit % len(self.digits)
        if not may_step:
            self.curr_idx = self.next_idx
        self.step = 0

    def draw(self, window: sg.Window):
        """ Load the digit's image file and display on screen """
        curr_dig = self.digits[self.curr_idx]
        to_dig = self.digits[self.next_idx]
        fname = f'{IMG_PATH}/{curr_dig}{to_dig}{self.step}.png'
        window[self.key].update(filename=fname)

    def do_step(self, window: sg.Window) -> bool:
        """ Animate a step of the flip from the current to the next digit """
        if self.curr_idx != self.next_idx:
            self.step += 1
            if self.step >= MAX_STEP:
                # flip done: draw final digit image
                self.curr_idx = self.next_idx
                self.step = 0
            self.draw(window)
            return True
        else:       # no step needed
            return False

    def __str__(self):
        return f'Digit: {self.key=} {self.curr_idx=} {self.next_idx=} {self.step=}'


class ClockFace:
    """ Contain and process all 4 digits as a group """
    def __init__(self, fmt=DispFmt.HR12):
        self.hr10 = ClockDigit(key='-HR10s-', digits='01')
        self.hr01 = ClockDigit(key='-HR1s-', digits='0123456789')
        self.min10 = ClockDigit(key='-MIN10s-', digits='012345')
        self.min01 = ClockDigit(key='-MIN1s-', digits='0123456789')
        self.stepping = False
        self.disp_fmt = fmt
        self.set_disp_fmt(self.disp_fmt)

    def set_disp_fmt(self, fmt: DispFmt):
        """ Set display format to 24-hour, 12-hour, or 12-hour with leading blank """
        if fmt == DispFmt.HR24:
            self.hr10.digits = '012'
        elif fmt == DispFmt.HR12:
            self.hr10.digits = '01'
        else:
            self.hr10.digits = 'x1'
        self.disp_fmt = fmt

    def get_disp_fmt(self) -> DispFmt:
        return self.disp_fmt

    def is_stepping(self) -> bool:
        return self.stepping

    def set_time(self, hours: int, mins: int, start_step=False):
        """ Set the current hours:mins and if should initiate a "flip" """
        if self.disp_fmt != DispFmt.HR24:
            if hours > 12:
                hours -= 12
            elif hours == 0:
                hours = 12

        self.stepping = start_step
        self.hr10.set_digit(hours // 10, self.stepping)
        self.hr01.set_digit(hours % 10, self.stepping)
        self.min10.set_digit(mins // 10, self.stepping)
        self.min01.set_digit(mins % 10, self.stepping)

    def draw_all(self, window: sg.Window):
        """ Draw all digits directly (at init or after gross time change) """
        self.hr10.draw(window)
        self.hr01.draw(window)
        self.min10.draw(window)
        self.min01.draw(window)

    def do_step(self, window: sg.Window):
        """ Update to the next intra-digit frame """
        if self.stepping:   # check from low to high
            self.stepping = (self.min01.do_step(window) or self.min10.do_step(window) or
                             self.hr01.do_step(window) or self.hr10.do_step(window))
