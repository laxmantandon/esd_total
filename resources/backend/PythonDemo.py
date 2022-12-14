#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""ZFPLab fiscal printer python demo"""
from datetime import datetime
from FP_core import ServerException, SErrorType
from FP import FP, Enums

try:
    import Tkinter as Tkinter
    import ttk as ttk
    import tkMessageBox as MessageBox
except Exception as exparse:
    import tkinter as Tkinter
    import tkinter.messagebox as MessageBox
    import tkinter.ttk as ttk


fp = FP()


def show_error(text):
    MessageBox.showerror(title="ERROR!", message=text)


def show_info(text):
    MessageBox.showinfo(title="Information", message=text)


def handle_exception(sx):
    msg = sx
    if hasattr(sx, 'message'):
        msg = sx.message

    if isinstance(sx, ServerException):
        show_error("ZfpLab library exception!")
        if sx.isFiscalPrinterError:
            # Possible reasons:
            # sx.STE1 =                                       sx.STE2 =
            #       0x30 OK                                          0x30 OK
            #       0x31 Out of paper, printer failure               0x31 Invalid command
            #       0x32 Registers overflow                          0x32 Illegal command
            #       0x33 Clock failure or incorrect date&time        0x33 Z daily report is not zero
            #       0x34 Opened fiscal receipt                       0x34 Syntax error
            #       0x35 Payment residue account                     0x35 Input registers overflow
            #       0x36 Opened non-fiscal receipt                   0x36 Zero input registers
            #       0x37 Payment is done but receipt is not closed   0x37 Unavailable transaction for correction
            #       0x38 Fiscal memory failure                       0x38 Insufficient amount on hand
            #       0x39 Incorrect password                          0x3A No access
            #       0x3a Missing external display
            #       0x3b 24hours block - missing Z report
            #       0x3c Overheated printer thermal head.
            #       0x3d Interrupt power supply in fiscal receipt (one time until status is read)
            #       0x3e Overflow EJ
            #       0x3f Insufficient conditions
            #
            if sx.ste1 == 0x30 and sx.ste2 == 0x32:
                show_error("sx.STE1 == 0x30 - command is OK AND sx.STE2 == 0x32"
                           "- command is Illegal in current context")
            elif sx.ste1 == 0x30 and sx.ste2 == 0x33:
                show_error("sx.STE1 == 0x30 - command is OK AND sx.STE2 == 0x33"
                           " - make Z report")
            elif sx.ste1 == 0x34 and sx.ste2 == 0x32:
                show_error("sx.STE1 == 0x34 - Opened fiscal receipt AND sx.STE2 == 0x32"
                           " - command Illegal in current context")
            else:
                show_error(sx.message + " STE1=" + str(sx.ste1) + " STE2=" + str(sx.ste2))
        elif sx.code == SErrorType.ServerDefsMismatch:
            show_error("The current library version and server definitions version do not match. " + msg)
        elif sx.code == SErrorType.ServMismatchBetweenDefinitionAndFPResult:
            show_error("The current library version and the fiscal device firmware is not matching")
        elif sx.code == SErrorType.ServerAddressNotSet:
            show_error("Specify server ServerAddress property")
        elif sx.code == SErrorType.ServerConnectionError:
            show_error("Connection from this app to the server is not established")
        elif sx.code == SErrorType.ServSockConnectionFailed:
            show_error("When the server can not connect to the fiscal device")
        elif sx.code == SErrorType.ServTCPAuth:
            show_error("Wrong device TCP password")
        elif sx.code == SErrorType.ServWaitOtherClientCmdProcessingTimeOut:
            show_error("Processing of other clients command is taking too long")
        else:
            show_error(msg)
    else:
        show_error(msg)


def fpGetLibraryVersions():
    show_info('Core version: ' + fp.getVersionCore() + '  Library definitions: ' + str(fp.getVersionDefinitions()))


def fpServerSetSettings():
    try:
        ip = TB_SERV_IP.get()
        port = int(TB_SERV_PORT.get())
        fp.serverSetSettings(ip, port)
        show_info("Setting set successfully.")
    except Exception as ex:
        handle_exception(ex)


def fpServerSetDeviceTcpSettings():
    try:
        ip = TB_DEV_IP.get()
        port = int(TB_DEV_PORT.get())
        password = TB_DEV_PASS.get()
        fp.serverSetDeviceTcpSettings(ip, port, password)
        show_info("Device set successfully.")
    except Exception as ex:
        handle_exception(ex)

def fpServerFindDevice():
    try:
        dev = fp.serverFindDevice()
        if dev:
            tblen = len(TB_DEV_COM.get())
            TB_DEV_COM.delete(0, tblen)
            TB_DEV_COM.insert('end', dev.serial_port)
            CB_DEV_BAUD.set(dev.baud_rate)
            show_info("Device found on " + dev.serial_port)
        else:
            show_error("Device not found!")
    except Exception as ex:
        handle_exception(ex)

def fpServerSetDeviceSerialSettings():
    try:
        com = TB_DEV_COM.get()
        baud = int(CB_DEV_BAUD.get())
        fp.serverSetDeviceSerialSettings(com, baud)
        show_info("Device set successfully.")
    except Exception as ex:
        handle_exception(ex)


def fpReadSerialNo():
    try:
        show_info(fp.ReadSerialAndFiscalNums().SerialNumber)
    except Exception as ex:
        handle_exception(ex)


def fpReadGSInfo():
    try:
        fp.RawWrite(bytearray([0x1D, 0x49]))
        lf_str = bytearray([0x0A]).decode('utf-8')
        raw_read_res_arr = fp.RawRead(0, lf_str)
        raw_read_res_str = raw_read_res_arr.decode('utf-8').replace(lf_str, "")
        show_info("GS info: " + str(raw_read_res_str))
    except Exception as ex:
        handle_exception(ex)


def fpDiagnostics():
    try:
        fp.PrintDiagnostics()
    except Exception as ex:
        handle_exception(ex)


def fpPrintZreport():
    try:
        fp.PrintDailyReport(Enums.OptionZeroing.Zeroing)
    except Exception as ex:
        handle_exception(ex)


def fpPrintXreport():
    try:
        fp.PrintDailyReport(Enums.OptionZeroing.Not_zeroing)
    except Exception as ex:
        handle_exception(ex)


def fpOpenFiscReceipt():
    try:
        oppass = TB_OP_PASS.get()
        fp.OpenReceipt(1, oppass, Enums.OptionReceiptFormat.Brief, Enums.OptionPrintVAT.No, Enums.OptionFiscalReceiptPrintType.Step_by_step_printing)
    except Exception as ex:
        handle_exception(ex)


def fpSellPlu():
    try:
        name = TB_ART_NAME.get()
        price = float(TB_ART_PRICE.get())
        qty = float(TB_ART_QTY.get())
        fp.SellPLUwithSpecifiedVAT(name, Enums.OptionVATClass.VAT_Class_A, price, qty)
    except Exception as ex:
        handle_exception(ex)


def fpCloseFiscalReceiptInCash():
    try:
        fp.CashPayCloseReceipt()
    except Exception as ex:
        handle_exception(ex)


def fpCancelFiscalReceipt():
    try:
        fp.CancelReceipt()
    except Exception as ex:
        handle_exception(ex)


class Form(Tkinter.Tk):
    def AddLabel(self, row_idx, col_idx, col_span, lbl_text, lbl_font):
        lbl = Tkinter.Label(self, text=lbl_text, font=lbl_font)
        lbl.grid(row=row_idx, column=col_idx, columnspan=col_span)
        return lbl

    def AddLabelTextbox(self, row_idx, col_idx, lbl_text, tb_text, lbl_sticky="w"):
        lbl = Tkinter.Label(self, text=lbl_text)
        lbl.grid(row=row_idx, column=col_idx, sticky=lbl_sticky)
        tb = Tkinter.Entry(self, width=20)
        tb.grid(row=row_idx, column=(col_idx+1))
        tb.insert('end', tb_text)
        return tb

    def AddLabelCombobox(self, row_idx, col_idx, lbl_text, cb_values, cb_selected, lbl_sticky="w"):
        lbl = Tkinter.Label(self, text=lbl_text)
        lbl.grid(row=row_idx, column=col_idx, sticky=lbl_sticky)
        cb = ttk.Combobox(self, width=17)
        cb['values'] = cb_values
        cb.grid(row=row_idx, column=(col_idx+1))
        cb.set(cb_selected)
        return cb

    def AddButton(self, row_idx, col_idx, col_span, btn_text, cmd, btn_sticky="nesw"):
        btn = Tkinter.Button(self, text=btn_text, command=cmd)
        btn.grid(row=row_idx, column=col_idx, columnspan=col_span, sticky=btn_sticky)
        return btn

    def FixGrid(self):
        col_count, row_count = self.grid_size()
        for col in range(1, col_count):
            self.grid_columnconfigure(col, minsize=20)
        for row in range(1, row_count):
            self.grid_rowconfigure(row, minsize=20)

    def Show(self):
        self.FixGrid()
        self.mainloop()


main_form = Form(screenName="ZFPLab Demo Python", baseName="ZFPLab Demo Python", className="ZFPLab Demo Python")

main_form.AddLabel(0, 0, 2, "Server settings", "Helvetica 12 bold")
TB_SERV_IP = main_form.AddLabelTextbox(1, 0, "ZfpLabServer IP Address", "localhost")
TB_SERV_PORT = main_form.AddLabelTextbox(2, 0, "ZfpLabServer TCP port", "4444")
main_form.AddButton(3, 0, 2, "Set server settings", fpServerSetSettings)

main_form.AddLabel(4, 0, 2, "Device settings", "Helvetica 12 bold")
TB_DEV_IP = main_form.AddLabelTextbox(5, 0, "Device IP Address", "10.10.5.8")
TB_DEV_PORT = main_form.AddLabelTextbox(6, 0, "Device TCP port", "8000")
TB_DEV_PASS = main_form.AddLabelTextbox(7, 0, "Device password", "123456")
main_form.AddButton(8, 0, 2, "Set device TCP settings", fpServerSetDeviceTcpSettings)
TB_DEV_COM = main_form.AddLabelTextbox(9, 0, "Device COM port", "COM1")
CB_DEV_BAUD = main_form.AddLabelCombobox(10, 0, "Device Baud rate", ("115200", "57600", "38400", "19200", "9600"), "115200")
main_form.AddButton(11, 0, 2, "Find device", fpServerFindDevice)
main_form.AddButton(12, 0, 2, "Set device Serial settings", fpServerSetDeviceSerialSettings)

main_form.AddLabel(13, 0, 2, "Operations", "Helvetica 12 bold")
main_form.AddButton(14, 0, 1, "Read serial number", fpReadSerialNo)
main_form.AddButton(14, 1, 1, "Read GS info", fpReadGSInfo)
main_form.AddButton(15, 0, 2, "Print Diagnostics", fpDiagnostics)
main_form.AddButton(16, 0, 1, "Z report", fpPrintZreport)
main_form.AddButton(16, 1, 1, "X report", fpPrintXreport)

main_form.AddLabel(17, 0, 2, "Receipt operations", "Helvetica 12 bold")
TB_OP_PASS = main_form.AddLabelTextbox(18, 0, "Operator 1 pass", "0000")
main_form.AddButton(19, 0, 2, "Open fiscal receipt", fpOpenFiscReceipt)
TB_ART_NAME = main_form.AddLabelTextbox(20, 0, "Article name", "Art 1")
TB_ART_QTY = main_form.AddLabelTextbox(21, 0, "Article quantity", "1")
TB_ART_PRICE = main_form.AddLabelTextbox(22, 0, "Article price", "2.5")
main_form.AddButton(23, 0, 2, "Sell article", fpSellPlu)
main_form.AddButton(24, 0, 2, "Close fiscal receipt in cash", fpCloseFiscalReceiptInCash)
main_form.AddButton(25, 0, 2, "Cancel fiscal receipt", fpCancelFiscalReceipt)

main_form.AddButton(26, 1, 1, "Check versions", fpGetLibraryVersions)

main_form.Show()
