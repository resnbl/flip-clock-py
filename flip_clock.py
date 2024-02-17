import time
import PySimpleGUI as sg
from clock_digit import ClockFace, ClockNum, DispFmt, IMG_PATH

# PSG info
COLON_KEY = '-COLON-'
TICK_KEY = '-TICK-'
TOP_BTN = '-TOP-BTN-'
BOT_BTN = '-BOT-BTN-'
BABBLE_KEY = '-BABBLE-'
THE_FONT = ('Roboto-Regular', 14)
BG_COLOR = "black"
COLON_MS = 1000
BABBLE_MS = 4000
STEP_MS = 100
DISP_FMT_LABELS = ['24-hour', '12-hour', '12-hour leading blank']

theClock = ClockFace()


def make_layout() -> list[list]:
    # orange buttons to right of digits
    top_btn = [sg.Image(filename=f'{IMG_PATH}/top_button.png', key=TOP_BTN, enable_events=True,
                        tooltip='Change display format', pad=(0, 0))]
    bot_btn = [sg.Image(filename=f'{IMG_PATH}/bottom_button.png', key=BOT_BTN, enable_events=True,
                        tooltip='Toggle DEMO mode', pad=(0, 0))]
    btn_col = sg.Column([top_btn, bot_btn])

    # logo, digits in "major" to "minor" order with colon, and buttons column
    digits_row = [
        sg.Image(filename=f'{IMG_PATH}/logo.png', pad=((1, 8), (2, 2))),

        theClock.make_image(ClockNum.HR10),
        theClock.make_image(ClockNum.HR01),

        sg.Image(filename=f'{IMG_PATH}/colon1.png', key=COLON_KEY, pad=(1, 2)),

        theClock.make_image(ClockNum.MIN10),
        theClock.make_image(ClockNum.MIN01),

        btn_col
    ]

    babble_row = [sg.Text(text='', auto_size_text=True, justification='center', expand_x=True,
                          text_color='white', background_color=BG_COLOR, key=BABBLE_KEY)]

    return [digits_row, babble_row]


def millis() -> int:
    # Emulate Arduino millis() function
    return time.time_ns() // (1000 * 1000)      # nanoseconds -> microseconds


def babble(txt: str, window: sg.Window) -> bool:
    # Draw text at bottom of screen; " " to erase it
    window[BABBLE_KEY].update(value=txt)
    return txt != ''


def set_clock(window: sg.Window, run_fast=False) -> tuple[int, int]:
    """ Initialize the clock to the current time and return hours, minutes """
    if run_fast:
        hours, mins = 12, 56
    else:
        tm = time.localtime()
        hours, mins = tm.tm_hour, tm.tm_min

    theClock.set_digits(hours, mins, window)
    return hours, mins


def clock_tick(hours: int, mins: int) -> tuple[int, int]:
    """ Update the clock by 1 minute """
    mins += 1
    if mins >= 60:
        mins = 0
        hours += 1
        if hours >= 24:
            hours = 0

    theClock.update_digits(hours, mins)
    return hours, mins


def colon_toggle(on: bool, window: sg.Window):
    """ Flash the colon between digits """
    fn = 'colon1' if on else 'colon0'
    window[COLON_KEY].update(filename=f'{IMG_PATH}/{fn}.png')


def main():
    layout = make_layout()
    window = sg.Window(f'Flip Clock', layout=layout, font=THE_FONT,
                       background_color=BG_COLOR, finalize=True)
    run_fast = False
    hours, mins = set_clock(window, run_fast)
    tick_ms = 6000 if run_fast else 60000
    colon_on = True
    babble_on = babble('Starting...', window)
    step_start = 0
    tick_start = colon_start = babble_start = millis()

    while True:
        event, values = window.read(timeout=100, timeout_key=TICK_KEY)
        if event in [sg.WIN_CLOSED]:
            break

        now = millis()
        if event == TICK_KEY:
            if now - colon_start >= COLON_MS:
                colon_on = not colon_on
                colon_toggle(colon_on, window)
                colon_start = now

            if theClock.is_stepping() and (now - step_start >= STEP_MS):
                theClock.do_step()
                step_start = now
            elif now - tick_start >= tick_ms:
                hours, mins = clock_tick(hours, mins)
                tick_start = now

            if babble_on and (now - babble_start >= BABBLE_MS):
                babble_on = babble('', window)

        elif event == TOP_BTN:
            fmt = (theClock.get_disp_fmt() + 1) % DispFmt.NUM_FMTS
            theClock.set_disp_fmt(fmt)
            theClock.draw_all()
            babble_on = babble(DISP_FMT_LABELS[fmt], window)
            babble_start = now

        elif event == BOT_BTN:
            run_fast = not run_fast
            tick_ms = 6000 if run_fast else 60000
            hours, mins = set_clock(window, run_fast)
            theClock.draw_all()
            babble_on = babble(f'Demo mode is {"ON" if run_fast else "OFF"}', window)
            babble_start = tick_start = now


if __name__ == '__main__':
    main()
