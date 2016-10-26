#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import *
from tkinter.messagebox import *
import serial.tools.list_ports
import string
import pydialog


class GUI:
    def __init__(self, master):
        self.version = "v1.0"
        self.master = master

        def menu_bar():
            menubar = Menu(master)

            # File menu
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="Quit", command=root.quit)
            menubar.add_cascade(label="File", menu=filemenu)

            # Mode menu
            modemenu = Menu(menubar, tearoff=0)
            modemenu.add_command(label="Simple", command=self.simple_mode)
            modemenu.add_command(label="Advanced", command=self.advanced_mode)
            menubar.add_cascade(label="Mode", menu=modemenu)

            # Help menu
            helpmenu = Menu(menubar, tearoff=0)
            helpmenu.add_command(label="About", command=self.about)
            menubar.add_cascade(label="Help", menu=helpmenu)

            master.config(menu=menubar)

        def main_frames():
            self.frameControl = Frame(master)
            self.frameControl.grid(row=0, column=0, sticky=NW)
            self.frameOutput = Frame(master)
            self.frameOutput.grid(row=0, column=1, sticky=N+S+E+W)
            self.frameOutput.grid_rowconfigure(0, weight=1)
            self.frameOutput.grid_columnconfigure(0, weight=1)
            self.frameBottom = Frame(master)
            self.frameBottom.grid(row=99, column=0, columnspan=99, sticky=SE)

        def control_frames():
            self.frameControl_serialsetup = Frame(self.frameControl)
            self.frameControl_serialsetup.grid(row=0, column=0, sticky=NW)
            self.separator_horizontal_serial = ttk.Separator(self.frameControl, orient=HORIZONTAL)
            self.separator_horizontal_serial.grid(row=1, column=0, sticky=W+E)

            self.frameControl_pinsetup = Frame(self.frameControl)
            self.frameControl_pinsetup.grid(row=2, column=0, sticky=NW)
            self.separator_horizontal_pins = ttk.Separator(self.frameControl, orient=HORIZONTAL)
            self.separator_horizontal_pins.grid(row=3, column=0, sticky=W+E)

            self.frameControl_filesetup = Frame(self.frameControl)
            self.frameControl_filesetup.grid(row=4, column=0, sticky=NW)
            self.separator_horizontal_files = ttk.Separator(self.frameControl, orient=HORIZONTAL)
            self.separator_horizontal_files.grid(row=5, column=0, sticky=W+E)

            self.frameControl_actions = Frame(self.frameControl)
            self.frameControl_actions.grid(row=6, column=0, sticky=N)
            self.separator_horizontal_actions = ttk.Separator(self.frameControl, orient=HORIZONTAL)
            self.separator_horizontal_actions.grid(row=7, column=0, sticky=W+E)

        def action_frames():
            self.frameControl_actions_ram = Frame(self.frameControl_actions)
            self.frameControl_actions_ram.grid(row=0, column=0, sticky=NW)
            self.separator_vertical_actions_ram = ttk.Separator(self.frameControl_actions, orient=VERTICAL)
            self.separator_vertical_actions_ram.grid(row=0, column=1, sticky=NS)

            self.frameControl_actions_spi = Frame(self.frameControl_actions)
            self.frameControl_actions_spi.grid(row=0, column=2, sticky=NW)
            self.separator_vertical_actions_spi = ttk.Separator(self.frameControl_actions, orient=VERTICAL)
            self.separator_vertical_actions_spi.grid(row=0, column=3, sticky=NS)

            self.frameControl_actions_otp = Frame(self.frameControl_actions)
            self.frameControl_actions_otp.grid(row=0, column=4, sticky=NW)
            # self.separator_vertical_actions_otp = ttk.Separator(self.frameControl_actions, orient=VERTICAL)
            # self.separator_vertical_actions_otp.grid(row=0, column=5, sticky=NS)

            self.frameControl_bulkactions = Frame(self.frameControl)
            self.frameControl_bulkactions.grid(row=8, column=0, sticky=W+E)
            self.separator_horizontal_bulk = ttk.Separator(self.frameControl, orient=HORIZONTAL)
            self.separator_horizontal_bulk.grid(row=9, column=0, sticky=W+E)

        # Variables
        def variables():
            self.serial_ports = get_ports()
            self.port_open = False
            self.filename_ram = StringVar()
            self.filename_ram.set("flash_programmer.bin")
            self.upload_ram_retry = IntVar()
            self.upload_ram_retry.set(5)
            self.filename_spi = StringVar()
            self.filename_spi.set("")
            self.filename_dump = StringVar()
            self.filename_dump.set("dump.bin")
            self.serial_port_selected = StringVar()
            self.serial_port_selected.set(self.serial_ports[0])
            self.reset_soc = BooleanVar()
            self.port_init = BooleanVar()
            self.app_wait = BooleanVar()
            self.bootable_spi = BooleanVar()
            self.verify_flash = BooleanVar()
            self.otp_uid_oui = StringVar()
            self.otp_uid_oui.set("4C4150")
            self.otp_uid_nic = StringVar()
            self.otp_uid_nic.set("000000")
            self.spi_startoff = StringVar()
            self.spi_startoff.set("0x00000000")
            self.spi_readlen = StringVar()
            self.spi_readlen.set("0x7FFF")
            self.uart_pins = {"P0_0, P0_1, 57600": 0x00, "P0_2, P0_3, 115200": 0x02, "P0_4, P0_5, 57600": 0x04, "P0_6, P0_7, 9600": 0x06}
            self.spi_port_cs = IntVar()
            self.spi_port_cs.set(0x00)
            self.spi_cs = IntVar()
            self.spi_cs.set(0x03)
            self.spi_port_clk = IntVar()
            self.spi_port_clk.set(0x00)
            self.spi_clk = IntVar()
            self.spi_clk.set(0x00)
            self.spi_port_do = IntVar()
            self.spi_port_do.set(0x00)
            self.spi_do = IntVar()
            self.spi_do.set(0x06)
            self.spi_port_di = IntVar()
            self.spi_port_di.set(0x00)
            self.spi_di = IntVar()
            self.spi_di.set(0x05)
            self.uart_pins_selected = StringVar()
            self.uart_pins_selected.set("P0_4, P0_5, 57600")
            self.bulk_flashSPI = BooleanVar()
            self.bulk_writeUID = BooleanVar()
            self.bulk_uidincrement = IntVar()
            self.bulk_uidincrement.set(1)
            self.bulk_resetdevice = BooleanVar()
            root.wm_title("PyDialog by Lapis %s" % self.version)

        # Setup controls
        def setup_controls():
            self.serial_device_title = Label(self.frameControl_serialsetup, text="Serial device:")
            self.serial_device_title.grid(row=1, column=0, sticky=E)
            self.serial_device_list = OptionMenu(self.frameControl_serialsetup, self.serial_port_selected, *self.serial_ports)
            self.serial_device_list.grid(row=1, column=1, sticky=W+E)
            self.button_openPort = Button(self.frameControl_serialsetup,
                                          text="Open port",
                                          command=self.open_port)
            self.button_openPort.grid(row=1, column=2)
            if self.serial_ports[0] == "No devices!":
                self.button_openPort.config(state="disabled")
            self.button_closePort = Button(self.frameControl_serialsetup,
                                           text="Close port",
                                           command=self.close_port)
            self.button_closePort.grid(row=1, column=3)
            self.button_closePort.config(state="disabled")
            self.button_refreshPorts = Button(self.frameControl_serialsetup,
                                              text="Refresh",
                                              command=self.refresh_ports)
            self.button_refreshPorts.grid(row=1, column=4)
            # self.button_refreshPorts.config(state="disabled")

            # Pins configuration
            self.serial_device_title = Label(self.frameControl_pinsetup, text="UART pins:")
            self.serial_device_title.grid(row=1, column=0, sticky=E)
            self.uart_pins_list = OptionMenu(self.frameControl_pinsetup, self.uart_pins_selected, *self.uart_pins.keys())
            self.uart_pins_list.grid(row=1, column=1, columnspan=2)
            self.port_title = Label(self.frameControl_pinsetup, text="Port")
            self.port_title.grid(row=2, column=1, sticky=W)
            self.pin_title = Label(self.frameControl_pinsetup, text="Pin")
            self.pin_title.grid(row=2, column=2, sticky=W)
            self.cs_title = Label(self.frameControl_pinsetup, text="CS")
            self.cs_title.grid(row=3, column=0, sticky=E)
            self.textbox_port_cs = Entry(self.frameControl_pinsetup,
                                         text=self.spi_port_cs,
                                         width=2)
            self.textbox_port_cs.grid(row=3, column=1, sticky=W)
            self.textbox_cs = Entry(self.frameControl_pinsetup,
                                         text=self.spi_cs,
                                         width=2)
            self.textbox_cs.grid(row=3, column=2, sticky=W)
            self.clk_title = Label(self.frameControl_pinsetup, text="CLK")
            self.clk_title.grid(row=4, column=0, sticky=E)
            self.textbox_port_clk = Entry(self.frameControl_pinsetup,
                                         text=self.spi_port_clk,
                                         width=2)
            self.textbox_port_clk.grid(row=4, column=1, sticky=W)
            self.textbox_clk = Entry(self.frameControl_pinsetup,
                                     text=self.spi_clk,
                                     width=2)
            self.textbox_clk.grid(row=4, column=2, sticky=W)
            self.do_title = Label(self.frameControl_pinsetup, text="DO")
            self.do_title.grid(row=5, column=0, sticky=E)
            self.textbox_port_do = Entry(self.frameControl_pinsetup,
                                         text=self.spi_port_do,
                                         width=2)
            self.textbox_port_do.grid(row=5, column=1, sticky=W)
            self.textbox_do = Entry(self.frameControl_pinsetup,
                                    text=self.spi_do,
                                    width=2)
            self.textbox_do.grid(row=5, column=2, sticky=W)
            self.di_title = Label(self.frameControl_pinsetup, text="DI")
            self.di_title.grid(row=6, column=0, sticky=E)
            self.textbox_port_di = Entry(self.frameControl_pinsetup,
                                         text=self.spi_port_di,
                                         width=2)
            self.textbox_port_di.grid(row=6, column=1, sticky=W)
            self.textbox_di = Entry(self.frameControl_pinsetup,
                                    text=self.spi_di,
                                    width=2)
            self.textbox_di.grid(row=6, column=2, sticky=W)

            # File settings
            self.files_label = Label(self.frameControl_filesetup, text="File paths")
            self.files_label.grid(row=1, column=0)
            self.button_pickFileRAM = Button(self.frameControl_filesetup,
                                             text="RAM application",
                                             command=self.pick_file_ram)
            self.button_pickFileRAM.grid(row=3, column=0, sticky=W+E)
            self.textbox_pickFileRAM = Entry(self.frameControl_filesetup,
                                             text=self.filename_ram)
            self.textbox_pickFileRAM.grid(row=3, column=1, sticky=W+E)
            self.button_pickFileSPI = Button(self.frameControl_filesetup,
                                             text="SPI hex file",
                                             command=self.pick_file_spi)
            self.button_pickFileSPI.grid(row=5, column=0, sticky=W+E)
            self.textbox_pickFileSPI = Entry(self.frameControl_filesetup,
                                             text=self.filename_spi)
            self.textbox_pickFileSPI.grid(row=5, column=1, sticky=W+E)
            self.button_pickFileDump = Button(self.frameControl_filesetup,
                                             text="Dump file",
                                             command=self.pick_file_dump)
            self.button_pickFileDump.grid(row=7, column=0, sticky=W+E)
            self.textbox_pickFileDump = Entry(self.frameControl_filesetup,
                                             text=self.filename_dump)
            self.textbox_pickFileDump.grid(row=7, column=1, sticky=W+E)

        # SoC connection controls
        def action_controls():
            # Subsection: RAM upload
            self.actions_label_ram = Label(self.frameControl_actions_ram, text="RAM")
            self.actions_label_ram.grid(row=1, column=0, columnspan=2, sticky=W+E)
            self.button_uploadRAM = Button(self.frameControl_actions_ram,
                                           text="Upload to RAM",
                                           command=self.upload_ram)
            self.button_uploadRAM.grid(row=3, column=0, columnspan=2, sticky=W+E)
            # self.button_uploadRAM.config(state="disabled")
            self.checkbox_reset_soc = Checkbutton(self.frameControl_actions_ram,
                                                  text="Reset SoC via RTS",
                                                  variable=self.reset_soc,
                                                  onvalue=True,
                                                  offvalue=False)
            self.checkbox_reset_soc.grid(row=5, column=0, columnspan=2, sticky=W)
            self.checkbox_reset_soc.select()
            self.checkbox_port_init = Checkbutton(self.frameControl_actions_ram,
                                                 text="Send UART/OTP ports",
                                                 variable=self.port_init,
                                                 onvalue=True,
                                                 offvalue=False)
            self.checkbox_port_init.grid(row=6, column=0, columnspan=2, sticky=W)
            self.checkbox_port_init.select()
            self.checkbox_wait_app = Checkbutton(self.frameControl_actions_ram,
                                                  text="Wait app after upload",
                                                  variable=self.app_wait,
                                                  onvalue=True,
                                                  offvalue=False)
            self.checkbox_wait_app.grid(row=7, column=0, columnspan=2, sticky=W)
            # self.checkbox_wait_app.select()
            self.textbox_upload_ram_label = Label(self.frameControl_actions_ram, text="Retry count:")
            self.textbox_upload_ram_label.grid(row=9, column=0, sticky=E)
            self.textbox_upload_ram_retry = Entry(self.frameControl_actions_ram,
                                                  text=self.upload_ram_retry,
                                                  width=2)
            self.textbox_upload_ram_retry.grid(row=9, column=1, sticky=W)
            self.button_resetdevice = Button(self.frameControl_actions_ram,
                                           text="Reset device",
                                           command=self.reset_device)
            self.button_resetdevice.grid(row=10, column=0, columnspan=2, sticky=W+E)
            self.button_resetdevice.config(state="disabled")

            # Subsection: SPI flasher
            self.actions_label_spi = Label(self.frameControl_actions_spi, text="SPI")
            self.actions_label_spi.grid(row=1, column=2, columnspan=3, sticky=W+E)
            self.button_readSPI = Button(self.frameControl_actions_spi,
                                         text="Read SPI",
                                         command=self.read_spi)
            self.button_readSPI.grid(row=3, column=3, sticky=W+E)
            self.button_readSPI.config(state="disabled")
            self.textbox_readSPIstart = Entry(self.frameControl_actions_spi,
                                             text=self.spi_startoff)
            self.textbox_readSPIstart.grid(row=5, column=3, sticky=W+E)
            self.textbox_readSPIreadlen = Entry(self.frameControl_actions_spi,
                                              text=self.spi_readlen)
            self.textbox_readSPIreadlen.grid(row=6, column=3, sticky=W+E)
            self.button_flashSPI = Button(self.frameControl_actions_spi,
                                          text="Flash SPI",
                                          command=self.flash_spi)
            self.button_flashSPI.grid(row=3, column=2, sticky=W+E)
            self.button_flashSPI.config(state="disabled")
            self.button_eraseSPI = Button(self.frameControl_actions_spi,
                                          text="Erase SPI",
                                          command=self.erase_spi)
            self.button_eraseSPI.grid(row=3, column=4, sticky=W+E)
            self.button_eraseSPI.config(state="disabled")
            self.checkbox_bootable_spi = Checkbutton(self.frameControl_actions_spi,
                                                     text="Bootable SPI",
                                                     variable=self.bootable_spi,
                                                     onvalue=True,
                                                     offvalue=False)
            self.checkbox_bootable_spi.grid(row=5, column=2, sticky=W)
            self.checkbox_bootable_spi.select()
            self.checkbox_verify_flash = Checkbutton(self.frameControl_actions_spi,
                                                     text="Verify flash",
                                                     variable=self.verify_flash,
                                                     onvalue=True,
                                                     offvalue=False)
            self.checkbox_verify_flash.grid(row=6, column=2, sticky=W)
            # self.checkbox_verify_flash.select()

            # Subsection: OTP flasher
            self.actions_label_otp = Label(self.frameControl_actions_otp, text="OTP")
            self.actions_label_otp.grid(row=1, column=4, columnspan=2, sticky=W+E)
            self.button_readOTPUID = Button(self.frameControl_actions_otp,
                                          text="Read UID",
                                          command=self.read_uid)
            self.button_readOTPUID.grid(row=3, column=4)
            self.button_readOTPUID.config(state="disabled")
            self.button_writeOTPUID = Button(self.frameControl_actions_otp,
                                          text="Write UID",
                                          command=self.write_uid)
            self.button_writeOTPUID.grid(row=3, column=5)
            self.button_writeOTPUID.config(state="disabled")
            self.otp_uid_oui_label = Label(self.frameControl_actions_otp, text="OUI:")
            self.otp_uid_oui_label.grid(row=5, column=4, sticky=E)
            self.otp_uid_oui_value = Entry(self.frameControl_actions_otp,
                                       text=self.otp_uid_oui,
                                       width=6)
            self.otp_uid_oui_value.grid(row=5, column=5, sticky=W)
            self.otp_uid_nic_label = Label(self.frameControl_actions_otp, text="NIC:")
            self.otp_uid_nic_label.grid(row=6, column=4, sticky=E)
            self.otp_uid_nic_value = Entry(self.frameControl_actions_otp,
                                           text=self.otp_uid_nic,
                                           width=6)
            self.otp_uid_nic_value.grid(row=6, column=5, sticky=W)

            # The magic bulk button
            # Select all files and options and click the magic button.
            # It will automatically connect to serial adapter and perform selected actions.
            self.button_bulkButton = Button(self.frameControl_bulkactions,
                                             text="Bulk flashing",
                                             command=self.magic_button)
            self.button_bulkButton.grid(row=0, column=0, sticky=E)
            self.checkbox_bulk_flashSPI = Checkbutton(self.frameControl_bulkactions,
                                                     text="Flash SPI",
                                                     variable=self.bulk_flashSPI,
                                                     onvalue=True,
                                                     offvalue=False)
            self.checkbox_bulk_flashSPI.grid(row=0, column=1, sticky=W)
            self.checkbox_bulk_flashSPI.select()
            self.checkbox_bulk_writeUID = Checkbutton(self.frameControl_bulkactions,
                                                      text="Write UID",
                                                      variable=self.bulk_writeUID,
                                                      onvalue=True,
                                                      offvalue=False)
            self.checkbox_bulk_writeUID.grid(row=1, column=1, sticky=W)
            self.checkbox_bulk_writeUID.select()
            self.checkbox_bulk_resetdevice = Checkbutton(self.frameControl_bulkactions,
                                                         text="Reset device after flashing",
                                                         variable=self.bulk_resetdevice,
                                                         onvalue=True,
                                                         offvalue=False)
            self.checkbox_bulk_resetdevice.grid(row=2, column=1, sticky=W)
            self.checkbox_bulk_resetdevice.select()
            self.bulk_uidincrement_label = Label(self.frameControl_bulkactions, text="UID increment:")
            self.bulk_uidincrement_label.grid(row=3, column=0, sticky=E)
            self.bulk_uidincrement_value = Entry(self.frameControl_bulkactions,
                                                 text=self.bulk_uidincrement,
                                                 width=3)
            self.bulk_uidincrement_value.grid(row=3, column=1, sticky=W)

        def output_log():
            self.txtLog = ScrolledText(self.frameOutput,
                                       width=80)
            self.txtLog.grid(row=0, column=0, sticky=N+S+E+W)
            self.txtLog.tag_configure("red", foreground="red")
            self.txtLog.tag_configure("green", foreground="green")

        # Initialize everything
        menu_bar()
        main_frames()
        control_frames()
        action_frames()
        variables()
        setup_controls()
        action_controls()
        output_log()

        # Start in simple mode. It should be enough for most users.
        #
        self.simple_mode()

        # Copyright
        self.label_copyright = Label(self.frameBottom, text="PyDialog by Lapis, (c) 2016")
        self.label_copyright.grid(row=0, column=0, sticky=SE)

        sys.stdout = TextRedirector(self.txtLog, "stdout")
        sys.stderr = TextRedirector(self.txtLog, "stderr")

    def get_pins(self):
        spi_config = {}
        spi_config["port_cs"] = self.spi_port_cs.get()
        spi_config["cs"] = self.spi_cs.get()
        spi_config["port_clk"] = self.spi_port_clk.get()
        spi_config["clk"] = self.spi_clk.get()
        spi_config["port_do"] = self.spi_port_do.get()
        spi_config["do"] = self.spi_do.get()
        spi_config["port_di"] = self.spi_port_di.get()
        spi_config["di"] = self.spi_di.get()
        return spi_config

    def open_port(self):
        spi_config = self.get_pins()
        self.controls = pydialog.GUI_control(device=self.serial_port_selected.get(),
                                             uart=self.uart_pins[self.uart_pins_selected.get()],
                                             spi_config=spi_config)
        self.enable_buttons((self.button_closePort, self.button_resetdevice))
        self.disable_buttons((self.button_openPort,))
        self.port_open = True

    def close_port(self):
        retval = self.controls.disconnect()
        if retval == 0:
            self.disable_buttons((self.button_closePort,
                                  self.button_resetdevice,
                                  self.button_readSPI,
                                  self.button_flashSPI,
                                  self.button_eraseSPI,
                                  self.button_readOTPUID,
                                  self.button_writeOTPUID))
            self.enable_buttons((self.button_openPort,))
            self.port_open = False

    def pick_file_ram(self):
        old_name = self.filename_ram.get()
        self.filename_ram.set(filedialog.askopenfilename(initialdir=".",
                                                         title="Select *.bin file",
                                                         filetypes=(("Binary file", "*.bin"),)))
        if not self.filename_ram.get():
            self.filename_ram.set(old_name)
        print(self.textbox_pickFileRAM.keys())

    def pick_file_spi(self):
        old_name = self.filename_spi.get()
        self.filename_spi.set(filedialog.askopenfilename(initialdir=".",
                                                         title="Select *.hex file",
                                                         filetypes=(("IntelHex file", "*.hex"),)))
        if not self.filename_spi.get():
            self.filename_spi.set(old_name)

    def pick_file_dump(self):
        old_name = self.filename_dump.get()
        self.filename_dump.set(filedialog.asksaveasfilename(initialdir=".",
                                                            title="Select destination .bin file",
                                                            filetypes=(("Binary file", "*.bin"), ("all files", "*.*"))))
        if not self.filename_dump.get():
            self.filename_dump.set(old_name)

    def upload_ram(self):
        if self.port_open is False:
            self.open_port()
        self.disable_buttons((self.button_uploadRAM,self.button_flashSPI))
        retval = self.controls.ram_upload(filename=self.filename_ram.get(),
                                          reset=True if self.reset_soc.get() == 1 else False,
                                          port_init=True if self.port_init.get() == 1 else False,
                                          app_wait=True if self.app_wait.get() == 1 else False)
        retrycount = 1
        while (retval is 1) and (retrycount < self.upload_ram_retry.get()):
            retrycount += 1
            print("Retrying...")
            retval = self.controls.ram_upload(filename=self.filename_ram.get(),
                                              reset=True if self.reset_soc.get() == 1 else False,
                                              port_init=True if self.port_init.get() == 1 else False,
                                              app_wait=True if self.app_wait.get() == 1 else False)
        if retval is 0:
            self.enable_buttons((self.button_uploadRAM,
                                 self.button_flashSPI,
                                 self.button_uploadRAM,
                                 self.button_resetdevice,
                                 self.button_readSPI,
                                 self.button_flashSPI,
                                 self.button_eraseSPI,
                                 self.button_readOTPUID,
                                 self.button_writeOTPUID))
            return 0
        else:
            return 1

    def read_spi(self):
        outfile = open(self.filename_dump.get(), "wb")
        outfile.write(self.controls.spi_read(startoff=int(self.spi_startoff.get(), 16),
                                             readlen=int(self.spi_readlen.get(), 16)))

    def flash_spi(self):
        self.disable_buttons((self.button_uploadRAM,
                              self.button_flashSPI))
        retval = self.controls.spi_flash(filename=self.filename_spi.get(),
                                bootable=True if self.bootable_spi.get() == 1 else False,
                                verify=True if self.verify_flash.get() == 1 else False)
        self.enable_buttons((self.button_flashSPI,
                            self.button_uploadRAM))
        if retval is 0:
            return 0
        else:
            return 1

    def erase_spi(self):
        self.disable_buttons((self.button_uploadRAM,
                              self.button_flashSPI))

        retval = self.controls.spi_erase()
        self.enable_buttons((self.button_flashSPI,
                            self.button_uploadRAM))
        if retval is 0:
            return 0
        else:
            return 1

    def read_uid(self):
        uid = self.controls.uid_read()
        if uid == 1:
            return 1
        self.otp_uid_oui.set(uid[0:3].hex().upper())
        self.otp_uid_nic.set(uid[3:].hex().upper())
        return uid.hex().upper()

    def write_uid(self):
        uid = self.otp_uid_oui.get().ljust(6, "0").upper() + self.otp_uid_nic.get().rjust(6, "0").upper()
        if self.validator(uid, 12, "hex"):
            self.error("UID error", "UID field invalid!")
            return 1
        retval = self.controls.uid_write(uid=int(uid, 16))
        if retval is 0:
            if self.read_uid() == uid:
                print("UID written successfully!")
                return 0
            else:
                print("UID was not written correctly!")
                return 1
        else:
            return 1

    def reset_device(self):
        print("Resetting device...")
        self.controls.reset_device()

    def simple_mode(self):
        self.frameControl_pinsetup.grid_remove()
        self.separator_horizontal_pins.grid_remove()
        self.button_pickFileRAM.grid_remove()
        self.textbox_pickFileRAM.grid_remove()
        self.button_pickFileDump.grid_remove()
        self.textbox_pickFileDump.grid_remove()
        self.checkbox_port_init.grid_remove()
        self.button_readSPI.grid_remove()
        self.textbox_readSPIstart.grid_remove()
        self.textbox_readSPIreadlen.grid_remove()
        return 0

    def advanced_mode(self):
        self.frameControl_pinsetup.grid()
        self.separator_horizontal_pins.grid()
        self.button_pickFileRAM.grid()
        self.textbox_pickFileRAM.grid()
        self.button_pickFileDump.grid()
        self.textbox_pickFileDump.grid()
        self.checkbox_port_init.grid()
        self.button_readSPI.grid()
        self.textbox_readSPIstart.grid()
        self.textbox_readSPIreadlen.grid()
        return 0

    def validator(self, variable, length, datatype):
        if len(variable) != length:
            return 1
        if datatype == "hex":
            return 0 if all(c in string.hexdigits for c in variable) else 1

    def refresh_ports(self):
        self.serial_ports = get_ports()
        self.serial_port_selected.set("")
        self.serial_device_list["menu"].delete(0, "end")
        for port in self.serial_ports:
            self.serial_device_list['menu'].add_command(label=port)
        self.serial_port_selected.set(self.serial_ports[0])
        if self.serial_ports[0] == "No devices!":
            self.disable_buttons((self.button_openPort,))
        else:
            self.enable_buttons((self.button_openPort,))

    def about(self):
        showinfo("About PyDialog", "PyDialog by Lapis\nhttps://www.bylapis.com\nCoded by: Danijel Tudek\n(c) Lapis 2016")

    def error(self, title="unknown", action="unknown"):
        showerror("%s" % title, "An error occured:\n%s" % action)

    def infobox(self, title="unknown", action="unknown"):
        showinfo("%s" % title, "%s" % action)

    # Do-everything button
    def magic_button(self):
        if self.port_open is False:
            self.open_port()
        if not self.upload_ram():
            if self.bulk_flashSPI.get() == 1:
                if self.flash_spi():
                    self.error("SPI error", "Error in SPI flashing!")
                    return 1
            if self.bulk_writeUID.get() == 1:
                uid = self.otp_uid_oui.get().upper() + self.otp_uid_nic.get().upper()
                if not self.write_uid():
                    uid = int(uid, 16)
                    print("UID %X written, incrementing..." % uid)
                    uid = (uid + self.bulk_uidincrement.get()).to_bytes(6, byteorder="big").hex().upper()
                    self.otp_uid_oui.set(uid[0:6])
                    self.otp_uid_nic.set(uid[6:])
                else:
                    self.error("UID error", "Unable to write UID")
                    return 1
            if self.bulk_resetdevice.get() == 1:
                self.reset_device()
                self.infobox("Bulk action", "Flashing OK!")
        else:
            self.error("SPI error", "Unable to upload flasher to RAM")

    def enable_buttons(self, buttons=()):
        for button in buttons:
            button.config(state="normal")
        return 0

    def disable_buttons(self, buttons=()):
        for button in buttons:
            button.config(state="disabled")
        return 0


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, printstr):
        self.widget.configure(state="normal")
        self.widget.insert("end", printstr, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see("end")
        root.update()
        self.widget.bind('<1>', lambda event: self.widget.focus_set())


def get_ports():
    # Get all serial ports
    serial_ports = []
    for i in serial.tools.list_ports.comports():
        serial_ports.append(i.device)
    if len(serial_ports) == 0:
        serial_ports = ["No devices!"]
    return serial_ports

if __name__ == "__main__":
    root = Tk()
    app = GUI(root)
    root.mainloop()
