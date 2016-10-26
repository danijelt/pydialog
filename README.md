# PyDialog
[_(c) Lapis 2016_](https://www.bylapis.com)

PyDialog is PC-DA14580 interface written in Python 3 with PySerial, developed and tested on Linux.
Compatibility with other Dialog DA1458x devices is possible, but not tested.

With appropriate USB-Serial adapter (FTx232H), RTS line can be used to reset the device,
completely eliminating the need for user interaction and enabling large-scale automation (e.g. production flashing).

It's recommended to use PyDialog on Linux. It also works on Windows, but it suffers from the same COM port freezing issue as when using Dialog's Smart Snippets.  
Since PyDialog's primary goal is to enable flashing on Linux, this issue was not investigated thoroughly.

## Usage
First, make sure you have at least Python 3.4, pip and the following modules: pyserial and intelhex.
You can install everything on Debian based distribution with the following commands:
```
sudo apt install python3.5 python3-tk python3-pip
sudo pip3 install intelhex
```

In order to run PyDialog without root privileges, add yourself to the `dialout` group:
```
sudo adduser USERNAME dialout
```
You need to log in again afterwards.

Finally, just execute `pydialog-gui.py` as you would any other file:
```
./pydialog-gui.py
```

The default mode is simple and it should be enough for most cases, unless you don't use default UART and SPI pins.

#### Connecting to SoC
"Upload to RAM button" will send `flash_programmer.bin` file to RAM. This program is used for interfacing with SPI and OTP.  
If you want to send a different file, switch to advanced mode (Mode -> Advanced) and select file with RAM application button.

#### Automatic reset
PyDialog can reset the SoC with RTS line on FTx232H device. Just connect RTS to SoC reset pin on your board and it will be reset automatically when needed.

#### SPI flashing
Click on "SPI hex file" button to select firmware in IntelHex format which will be written to SPI.  
After connecting with SoC (Upload to RAM button), click "Flash SPI".

By default, bootable header will be written before firmware.

#### UID
Enter OUI and NIC parts of the MAC address and click "Write UID".

#### Bulk flashing
This functionality is intended for mass flashing. It can flash SPI, write UID or do both, and reset SoC afterwards (to boot with new data).
If "Write UID" is enabled, after each successful flash NIC will be incremented according to the number (integer) specified in the "UID increment" field.

_Average time needed to flash SPI and write UID on DA14580 with default settings is 14 seconds._


## UART boot protocol
_Described in AN-B-001 - Booting from serial interfaces_
* After SoC is reset, it sends 0x02 (STX), announcing that it's ready to accept data.
* PC responds with 3 bytes: 0x01 (SOH) and 2-byte little endian data length
* SoC responds with 0x06 (ACK) if it received correct data and it can accept the given length, or 0x15 (NACK) if something is wrong
* PC sends *exactly* the number of bytes sent above
* SoC sends 1 byte CRC checksum
* PC compares it to its own previously calculated checksum
* PC sends 0x06 (ACK) or 0x15 (NACK) depending on the received CRC

## flash_programmer.bin
flash_programmer.bin is precompiled binary taken from Smart Snippets v3.9. Latest version from SDK 5.0.3 can't be compiled in Keil uVision with UART support, and other SDK releases contain older versions.
The bundled flash_programmer is v3.0.9.529.

The interface is simple and everything applies for both sides - PC and SoC.
First two bytes represent big endian uint16 data length (including 1 byte ACTION), then 4 bytes of CRC32 checksum (big endian), then the requested action and data (if applicable).

**Length and CRC32 are mandatory for every action in both ways!** It won't be mentioned later while describing actions.

If the action and data (if applicable) is valid, SoC will always reply with 0x83 (ACTION_OK).

### SPI flash

#### Initialization
Every SPI operation begins with 0x95 (ACTION_SPI_GPIOS) which tells SoC which pins to use for SPI.
It consists of 8 bytes which configures port and pin for SPI lines: CS, CLK, DO (MOSI), DI (MISO), in that order.
Default for DA14580 is:
* CS: port 0, pin 3
* CLK: port 0, pin 0
* DO (MOSI): port 0, pin 6
* DI (MISO): port 0, pin 5

The full command for this configuration (including action byte) would be:
95 00 03 00 00 00 06 00 05


#### Erase entire SPI
SPI is erased simply by sending 0x92 (ACTION_SPI_ERASE).

#### Flash SPI
_SPI must be erased before writing._

First send 0x91 (ACTION_SPI_WRITE). This action also expects 4-byte start offset (0x00000000 for SPI) and 2-byte data length (in this order), big endian.
After that, send flash contents.

##### Bootable SPI
If you want to make the flash content bootable (so that the SoC can execute SPI flash content after reset), the boot header must be present.

It consists of the following:
* 2 fixed bytes: 70 50
* 4 dummy bytes: 00 00 00 00
* data length _after_ this header

This header must be at 0x0000 offset, before the code. Its size must be included in data length sent on the beginning (after 0x91 action byte).

### OTP memory
OTP interface doesn't require. OTP memory starts at 0x47F00 and the length is 0x100.

#### Read OTP
OTP is read by sending 0x80, 4-byte start offset and 2-byte length.

#### Write OTP
Writing OTP requires 6,6 - 6,8 volts applied to VPP pin. Write command is 0x81 which also expects start offset and length of the data being sent.

#### UID
UID (Bluetooth MAC address) is stored at 0x47FD4, little endian. PyDialog handles LE <---> BE conversion and it expects that the UID is provided as big endian by user.


