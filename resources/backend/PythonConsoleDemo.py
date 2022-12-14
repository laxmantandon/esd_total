"""ZFPLab fiscal printer python console demo"""
from FP_core import ServerException, SErrorType
from FP import FP, Enums
from datetime import datetime

try:
    input = raw_input
except NameError:
    pass


def show_error(text):
    print(text)


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
            show_error("The current library version and server definitions version do not match")
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


fp = FP()

try:
    print("Setting server... fp.-serverSetSettings")
    fp.serverSetSettings("10.10.10.110", 4444)
    print("Setting set successfully.")

    if not fp.isCompatible():
        print("Server definitions and client code have different versions!")

    artCount = 50
    working = True
    while working:
        print("  ***** Choose operation *****")
        print("  '-'   Device tcp settings")
        print("  '+'   Device serial settings")
        print("  '0'   Read status")
        print("  '1'   Open fiscal receipt")
        print("  '2'   Free sale")
        print("  '3'   Sell item from device database")
        print("  '4'   Print free text")
        print("  '5'   Close fiscal receipt in cash")
        print("  '6'   Paper feed")
        print("  '7'   Read " + str(artCount) + " PLU0 (info about first " + str(artCount) + " articles)")
        print("  '8'   Print Daily report")
        print("  '9'   Print FM report by date")
        print("  'R'   RawWrite, RawRead")
        print("  'D'   DirectCommand")
        print("  'E'   Exit")
        print(" ")

        try:
            k = input("Input:")
            if len(k) == 1:
                if k == "-":
                    devIp = input("Enter device IP address: ")
                    devPass = input("Enter device TCP password: ")
                    print("fp.serverSetDeviceTcpSettings")
                    fp.serverSetDeviceTcpSettings(devIp, 8000, devPass)
                    print("Device set successfully.")

                elif k == "+":
                    devSerialPort = input("Enter device serial port: ")
                    devBaudRate = input("Enter device baud rate: ")
                    print("fp.serverSetDeviceSerialSettings")
                    fp.serverSetDeviceSerialSettings(devSerialPort, devBaudRate)
                    print("Device set successfully.")

                elif k == "0":
                    print("fp.ReadStatus")
                    st = fp.ReadStatus()
                    print("st.opened_Fiscal_Receipt " + str(st.Opened_Fiscal_Receipt))

                elif k == "1":
                    print("fp.OpenReceipt")
                    fp.OpenReceipt(1, "0", Enums.OptionReceiptFormat.Brief, Enums.OptionPrintVAT.No, Enums.OptionFiscalReceiptPrintType.Step_by_step_printing)

                elif k == "2":
                    print("fp.SellPLUwithSpecifiedVAT")
                    fp.SellPLUwithSpecifiedVAT("Article", Enums.OptionVATClass.VAT_Class_A, 1.2, 1.5)

                elif k == "3":
                    print("fp.SellPLUFromFD_DB")
                    aN = input("Enter Article number: ")
                    fp.SellPLUFromFD_DB(Enums.OptionSign.Sale, float(aN))

                elif k == "4":
                    print("fp.PrintText")
                    fp.PrintText("Free text")

                elif k == "5":
                    print("fp.CashPayCloseReceipt")
                    fp.CashPayCloseReceipt()

                elif k == "6":
                    print("fp.PaperFeed")
                    fp.PaperFeed()

                elif k == "7":
                    print("fp.ReadPLUallData")
                    for artNum in range(1, artCount):
                        art = fp.ReadPLUallData(float(artNum))
                        print("Name: " + art.PLUName + " Price: " + str(art.Price))

                elif k == "8":
                    print("fp.PrintDailyReport")
                    fp.PrintDailyReport(Enums.OptionZeroing.Zeroing)

                elif k == "9":
                    print("fp.PrintBriefFMReportByDate")
                    fp.PrintBriefFMReportByDate(datetime.now(), datetime.now())

                elif k == "R":
                    print("fp.RawWrite GS I")
                    fp.RawWrite(bytearray([0x1D, 0x49]))
                    LF = bytearray([0x0A]).decode('utf-8')
                    print("fp.RawRead")
                    RES_ARR = fp.RawRead(0, LF)
                    GS_INFO = RES_ARR.decode('utf-8').replace(LF, "")
                    print("GS info: " + str(GS_INFO))

                elif k == "D":
                    print("fp.DirectCommand")
                    dc = input("Command: ")
                    res = fp.DirectCommand(str(dc))
                    print("Result: " + res)

                elif k == "E":
                    working = False

                else:
                    print("Incorrect input")
            else:
                print("Please enter only one character")
            print(" ")
        except Exception as fpe:
            handle_exception(fpe)

except Exception as ex:
    handle_exception(ex)
    input("Press any to exit...")
