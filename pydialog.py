#!/usr/bin/env python3
import serial
from intelhex import IntelHex
import os.path
import time
import binascii


class dialog_protocol():
    def __init__(self, master):
        self.master = master

        self.NULL = 0x00.to_bytes(1, byteorder="big")
        # Sent from SoC to PC to announce that it's ready
        self.STX = 0x02.to_bytes(1, byteorder="big")
        # Sent from PC to SoC to announce sending code
        self.SOH = 0x01.to_bytes(1, byteorder="big")
        # ACK_OK sent by PC or SoC after receiving command - everything is OK
        self.ACK = 0x06.to_bytes(1, byteorder="big")
        # ACK_NOT sent by PC or SoC after receiving command - something is wrong
        self.NACK = 0x15.to_bytes(1, byteorder="big")
        # Dialog's programs will respond to 0x10 with version
        self.APP_VERSION = 0x10.to_bytes(1, byteorder="big")

    def arrange_bytes(self, data=None, endianness="big"):
        if data is None:
            return "No data!"
        shift = 8 * len(data) - 8
        arranged = 0
        for i in data:
            arranged += i << shift
            shift -= 8
        arranged = arranged.to_bytes(len(data), byteorder=endianness)
        return arranged

    def generate_command(self, data=None):
        if data is None:
            return "No data!"
        length = len(data).to_bytes(2, byteorder="big")
        crc32 = self.crc32_calc(data)
        command = length + crc32 + data
        return command

    def crc32_calc(self, data=None):
        if data is None:
            return "No data!"
        crc32 = binascii.crc32(data) % (1 << 32)
        crc32 = crc32.to_bytes(4, byteorder="big")
        return crc32

    def crc8_calc(self, data=None):
        if data is None:
            return "No data!"
        crc8 = 0x00
        for i in data:
            crc8 = crc8 ^ i
        crc8 = crc8.to_bytes(1, byteorder="big")
        return crc8

    def parse_response(self):
        length = self.master.ser.read(2)
        received_crc32 = self.master.ser.read(4)
        data = self.master.ser.read(int.from_bytes(length, byteorder="big"))
        calculated_crc32 = self.crc32_calc(data)
        if received_crc32 == calculated_crc32:
            return ("OK", length, data)
        else:
            return ("Response CRC error!", length, data)


# SPI over UART handler
class SPI_UART_interface():
    def __init__(self, master,
                 port_cs=0x00,
                 cs=0x03,
                 port_clk=0x00,
                 clk=0x00,
                 port_do=0x00,
                 do=0x06,
                 port_di=0x00,
                 di=0x05):
        self.master = master
        self.arrange_bytes = self.master.dialog_protocol.arrange_bytes

        # SPI init command is 0x95 followed by SPI pins configuration, appended later
        self.init_cmd = 0x95

        self.init_config = self.arrange_bytes((self.init_cmd, port_cs, cs, port_clk, clk, port_do, do, port_di, di))

        # SPI read command - required data will be appended later
        self.read_cmd = 0x90

        # SPI write command - required data will be appended later
        self.write_cmd = 0x91

        # SPI full erase command is just 0x92
        self.erase_cmd = 0x92

        # Bootable SPI header
        self.bootable_header = self.arrange_bytes((0x70, 0x50, 0x00, 0x00, 0x00, 0x00))

        # SPI responses
        self.response_ok = 0x83
        self.response_invalid_command = 0x86
        self.response_data = 0x82

    def init_spi(self):
        print("Sending SPI init command")
        init_cmd = self.master.dialog_protocol.generate_command(self.init_config)
        self.master.ser.write(init_cmd)
        (parser, length, data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if data[0] == self.response_ok:
                print("OK")
                return 0
            else:
                print("Bad response! (%s)" % hex(data[0]))
                return 1
        else:
            print(parser)
            return 1

    def read_spi(self,
                 startoff=0x00000000,
                 readlen=0x7FFF):
        print("Reading SPI...")
        read_cmd = self.read_cmd.to_bytes(1, byteorder="big") \
                   + startoff.to_bytes(4, byteorder="big") \
                   + readlen.to_bytes(2, byteorder="big")
        read_cmd = self.master.dialog_protocol.generate_command(read_cmd)
        if self.init_spi() == 1:
            return 1
        print("Sending SPI read command...")
        self.master.ser.write(read_cmd)
        (parser, length, data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if data[0] == self.response_data:
                print("OK")
                return data[1:]
            else:
                print("Bad response! (%s)" % hex(data[0]))
                return 1
        else:
            return 1

    def write_spi(self,
                  data=None,
                  startoff=0x00000000,
                  bootable=True,
                  verify=True):
        if data is None:
            print("No data!")
            return 1
        flashlen = len(data)
        print("Writing SPI...")
        if bootable is True:
            print("SPI will be bootable")
            datalen = flashlen
            data = self.bootable_header + datalen.to_bytes(2, byteorder="big") + data
            flashlen += len(self.bootable_header) + 2
        write_pre = self.write_cmd.to_bytes(1, byteorder="big") \
                    + startoff.to_bytes(4, byteorder="big")     \
                    + flashlen.to_bytes(2, byteorder="big")
        write_cmd = write_pre + data
        write_cmd = self.master.dialog_protocol.generate_command(write_cmd)
        if self.erase_spi() == 1:
            return 1
        print("Sending flash content...")
        self.master.ser.write(write_cmd)
        (parser, length, response_data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if response_data[0] == self.response_ok:
                print("OK")
            else:
                print("Bad response! (%s)" % hex(response_data[0]))
                return 1
        else:
            return 1
        if verify is True:
            flash_content = self.read_spi(startoff=startoff, readlen=flashlen)
            if flash_content == data:
                print("Flash verification OK")
                return 0
            else:
                print("Error: bad flash content!")
                return 1
        else:
            return 0

    def erase_spi(self):
        print("Erasing SPI...")
        erase_cmd = self.arrange_bytes((self.erase_cmd,))  # comma is not a typo, we need a tuple
        erase_cmd = self.master.dialog_protocol.generate_command(erase_cmd)
        if self.init_spi() == 1:
            return 1
        print("Sending SPI erase command")
        self.master.ser.write(erase_cmd)
        (parser, length, data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if data[0] == self.response_ok:
                print("OK")
                return 0
            else:
                print("Bad response! (%s)" % hex(data[0]))
                return 1
        else:
            print(response)
            return 1


# OTP over UART handler
class OTP_UART_interface():
    def __init__(self, master):
        self.master = master
        self.arrange_bytes = self.master.dialog_protocol.arrange_bytes

        # OTP read command
        self.read_cmd = 0x80

        # OTP write command - required data will be appended later
        self.write_cmd = 0x81

        # OTP responses
        self.response_ok = 0x83
        self.response_invalid_command = 0x86
        self.response_data = 0x82

    def read_otp(self,
                 startoff=0x00047F00,
                 readlen=0x0100):
        print("Reading OTP...")
        read_cmd = self.read_cmd.to_bytes(1, byteorder="big") \
                   + startoff.to_bytes(4, byteorder="big")    \
                   + readlen.to_bytes(2, byteorder="big")
        read_cmd = self.master.dialog_protocol.generate_command(read_cmd)
        self.master.ser.write(read_cmd)
        print("Waiting for %s bytes of data..." % hex(readlen))
        (parser, length, data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if data[0] == self.response_data:
                print("OK")
                return data[1:]
            else:
                print("Bad response! (%s)" % hex(data[0]))
                return 1
        else:
            return 1

    def write_otp(self,
                  data=None,
                  startoff=0x00047F00):
        if data is None:
            print("No data!")
            return 1
        print("Writing OTP...")
        if startoff == 0x47FD4 and self.read_otp(startoff=startoff, readlen=0x6) != bytes.fromhex("000000000000"):
            print("UID is already programmed!")
            return 1
        length = len(data)
        write_pre = self.write_cmd.to_bytes(1, byteorder="big") \
                    + startoff.to_bytes(4, byteorder="big") \
                    + length.to_bytes(2, byteorder="big")
        write_cmd = write_pre + data
        write_cmd = self.master.dialog_protocol.generate_command(write_cmd)
        self.master.ser.write(write_cmd)
        (parser, length, data) = self.master.dialog_protocol.parse_response()
        if parser == "OK":
            if data[0] == self.response_ok:
                print("OK")
                return 0
            else:
                print("Bad response! (%s)" % data.hex())
                return 1
        else:
            return 1


# UART commands handler
class UART_interface():
    def __init__(self, device, uart=0x04, spi_config={}):
        self.dialog_protocol = dialog_protocol(self)
        if uart == 0x00:
            self.TX = 0x00.to_bytes(1, byteorder="big")
            # self.RX = 0x01.to_bytes(1, byteorder="big")
            baud = 57600
        elif uart == 0x02:
            self.TX = 0x02.to_bytes(1, byteorder="big")
            # self.RX = 0x03.to_bytes(1, byteorder="big")
            baud = 115200
        elif uart == 0x04:
            # Default UART GPIO ports and baud rate
            self.TX = 0x04.to_bytes(1, byteorder="big")
            # self.RX = 0x05.to_bytes(1, byteorder="big")
            baud = 57600
        elif uart == 0x06:
            self.TX = 0x06.to_bytes(1, byteorder="big")
            # self.RX = 0x07.to_bytes(1, byteorder="big")
            baud = 9600
        self.OTP = self.dialog_protocol.arrange_bytes((0x01, 0x02))

        self.ser = serial.Serial(device, baud, rtscts=False, timeout=15)
        self.spi = SPI_UART_interface(self, **spi_config)
        self.otp = OTP_UART_interface(self)
        print("PyDialog ready, using %s" % device)

    def disconnect(self):
        try:
            print("Closing port...")
            self.ser.close()
            return 0
        except Exception as e:
            print("Disconnect error: " + str(e))
            return 1

    def calculate_length(self, filename, port_init=None):
        length = len(filename)
        if port_init is True:
            length += 3
        d1 = length & 0xff
        d2 = length >> 8
        length = self.dialog_protocol.arrange_bytes((d1, d2))
        return length

    def reset_device(self):
        # it's $#%&@ inverted
        self.ser.rts = False
        time.sleep(1)
        self.ser.rts = True
        return 0

    def wait_soc(self, reset=False):
        if reset is True:
            print("Resetting device...")
            self.reset_device()
        else:
            print("Please reset the device!")
        print("Waiting for SoC...")
        status = 0
        while status != self.dialog_protocol.STX:
            status = self.ser.read(1)
        self.ser.reset_input_buffer()
        print("SoC ready!")
        return 0

    def send_file(self, reset=False, binfile=None, port_init=True, app_wait=True):
        if port_init is True:
            binfile = binfile + self.OTP + self.TX
        length = len(binfile).to_bytes(2, byteorder="little")
        local_crc = self.dialog_protocol.crc8_calc(binfile)
        print("Length (LE): 0x%s\nCRC8: 0x%s" % (length.hex(), local_crc.hex()))
        if self.wait_soc(reset):
            return 1
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        print("Sending file length...")
        self.ser.write(self.dialog_protocol.SOH)
        self.ser.write(length)
        self.ser.reset_input_buffer()
        response = self.ser.read(1)
        while response == self.dialog_protocol.NULL:
            print("Got 0x00! Retry...")
            response = self.ser.read(1)
        if response == self.dialog_protocol.ACK:
            print("Sending file...")
            self.ser.write(binfile)
            print("File sent!")
            remote_crc = self.ser.read(1)
            if remote_crc == local_crc:
                print("CRC OK (0x%s)" % remote_crc.hex())
                self.ser.write(self.dialog_protocol.ACK)
                if app_wait is True:
                    # Workaround for "invalid command" initial output.
                    # Flasher outputs "invalid command" on initialization
                    # because the input buffer is empty on startup.
                    # We use this to detect that the application is ready.
                    # However, we don't fail if 0x86 is somehow missed, because
                    # the flasher is operational even without that.
                    data = self.ser.read(6)
                    if data[0] == 0x86:
                        print("Application ready")
                    else:
                        print("Error: application did not respond!")
                time.sleep(0.5)
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                return 0
            else:
                print("CRC mismatch! Got: 0x%s, expected: 0x%s" % (remote_crc.hex(), local_crc.hex()))
                self.ser.write(self.dialog_protocol.NACK)
                return 1
        elif response == self.dialog_protocol.STX:
            print("SoC was reset unexpectedly! Restarting...")
            return 1
        else:
            print("Error: bad response! (0x%s, expected: 0x%s, restarting...)" %
                  (response.hex(), self.dialog_protocol.ACK.hex()))
            return 1


class GUI_control:
    def __init__(self, device, uart, spi_config):
        self.flasher = UART_interface(device=device, uart=uart, spi_config=spi_config)

    def disconnect(self):
        retval = self.flasher.disconnect()
        return retval

    def ram_upload(self, reset=True, filename=None, port_init=True, app_wait=True):
        if filename is None:
            print("Error: no file specified!")
            return 1
        try:
            binfile = open(filename, "rb").read()
            print("Filename: {0[1]}".format(os.path.split(filename)))
        except Exception as e:
            print("File open error: " + str(e))
            return 1
        retval = self.flasher.send_file(reset=reset, binfile=binfile, port_init=port_init, app_wait=app_wait)
        return retval

    def spi_flash(self, filename=None, bootable=True, verify=True):
        if filename is None:
            print("Error: no file specified!")
            return 1
        try:
            ih = IntelHex(filename)
            binfile = ih.tobinstr()
            print("Filename: {0[1]}".format(os.path.split(filename)))
        except Exception as e:
            print("File open error: " + str(e))
            return 1
        retval = self.flasher.spi.write_spi(data=binfile, bootable=bootable, verify=verify)
        return retval

    def spi_read(self, startoff=0x00000000, readlen=0x7FFF):
        retval = self.flasher.spi.read_spi(startoff=startoff, readlen=readlen)
        return retval

    def spi_erase(self):
        retval = self.flasher.spi.erase_spi()
        return retval

    def uid_read(self):
        retval = self.flasher.otp.read_otp(startoff=0x47FD4, readlen=0x6)
        if retval == 1:
            return retval
        retval = bytearray(retval)
        retval.reverse()
        return retval

    def uid_write(self, uid=0x00):
        uid = uid.to_bytes(6, byteorder="little")
        print("Writing UID: %s" % uid.hex().upper())
        retval = self.flasher.otp.write_otp(startoff=0x47FD4, data=uid)
        return retval

    def reset_device(self):
        self.flasher.reset_device()
        print("OK")
        return 0

if __name__ == "__main__":
    app = GUI_control("/dev/ttyUSB0", 0x04, {})
    app.ram_upload(filename="flash_programmer.bin", reset=True, port_init=False)
