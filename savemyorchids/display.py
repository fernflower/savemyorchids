import tm1637

from savemyorchids import extdevinterface


class FourDigitDisplay(extdevinterface.ExternalDevice):
    def __init__(self):
        super(FourDigitDisplay, self).__init__(config_section="display")

    def init(self):
        display = tm1637.TM1637(int(self.params.clk),
                int(self.params.dio), tm1637.BRIGHT_TYPICAL)
        display.Clear()
        display.SetBrightnes(1)
        display.ShowDoublepoint(True)
        self._device = display
        return self._device

    def _form_number(self, num, digits):
        n = int(self.params.digits)
        res = []
        while num != 0:
            dig = num % 10
            num = num / 10
            res.append(dig)
        res.reverse()
        if len(res) < digits:
            res = [0] * (digits-len(res)) + res
        return res

    def output(self, temp, hum):
        digits = int(self.params.digits) / 2
        digits_temp = self._form_number(int(temp),digits)
        digits_hum = self._form_number(int(hum), digits)
        self._device.Show(digits_temp + digits_hum)


def main():
    display = FourDigitDisplay()
    display.output(9.0, 43.2)

if __name__ == "__main__":
    main()
