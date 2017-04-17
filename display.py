import argparse
import tm1637
import utils

CONFIG = "config"
PARAMS = utils.read_config(CONFIG, "display")

def init_display():
    display = tm1637.TM1637(int(PARAMS.clk), int(PARAMS.dio), tm1637.BRIGHT_TYPICAL)
    display.Clear()
    display.SetBrightnes(1)
    display.ShowDoublepoint(True)
    return display

def form_number(num, digits):
    n = int(PARAMS.digits)
    res = []
    while num != 0:
        dig = num % 10
        num = num / 10
        res.append(dig)
    res.reverse()
    if len(res) < digits:
        res = [0] * (digits-len(res)) + res
    return res

def output(display, temp, hum):
    digits = int(PARAMS.digits) / 2
    digits_temp = form_number(int(temp),digits)
    digits_hum = form_number(int(hum), digits)
    display.Show(digits_temp + digits_hum)

def main():
    display = init_display()
    output(display, 9.0, 43.2)

if __name__ == "__main__":
    main()
