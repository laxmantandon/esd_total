import datetime
from flask import Flask, request, jsonify
from FP import FP
import json

app = Flask(__name__)
fp = FP()

@app.route('/')
def test():
    msg = {"msg": "ESD APP runnning ..."}
    return jsonify(msg)

VAT_CLASSES = [
    "C","D","E"
]

@app.route('/total_api', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        msg = {"msg": "ESD APP runnning ...", "Status": "OK"}
        return jsonify(msg)

    if request.method == "POST":
        errors = ""
        payload = request.get_json()
        items = payload.get("items_list")
        led = payload.get("led_list")
        vouchertype = payload.get("vouchertype")
        try:
            ip = request.headers.get("Ip")
            printhost = request.headers.get("Printhost")
            port = request.headers.get("Port")
            pw = request.headers.get("Pw")

            try:
                printhost = str(printhost).split(":")
                print_host = printhost[1].replace("//", "")
                print_port = printhost[2].replace("/", "")
            except Exception as e:
                return jsonify("Invalid parameter format (http://localhost:4444/)")
            fp.serverSetSettings(ipaddress=str(print_host), tcp_port=int(print_port))
            fp.serverSetDeviceTcpSettings(ip, port, pw)
            status = fp.ReadStatus()
            if status:
                # CompanyName, ClientPINnum, HeadQuarters, Address, PostalCodeAndCity, ExemptionNum, TraderSystemInvNum
                if vouchertype == "Tax Invoice":
                    fp.OpenInvoiceWithFreeCustomerData(CompanyName=payload.get("CompanyName") or "",  ClientPINnum=payload.get("customer_pin") or "", HeadQuarters=payload.get("HeadQuarters") or "", Address=payload.get("Address") or "", PostalCodeAndCity=payload.get("PostalCodeAndCity") or "", ExemptionNum=payload.get("customer_exid"), TraderSystemInvNum=payload.get("invoice_number"))
                elif vouchertype == "Credit Note":
                    fp.OpenCreditNoteWithFreeCustomerData(CompanyName=payload.get("CompanyName") or "",  ClientPINnum=payload.get("customer_pin") or "", HeadQuarters=payload.get("HeadQuarters") or "", Address=payload.get("Address") or "", PostalCodeAndCity=payload.get("PostalCodeAndCity") or "", ExemptionNum=payload.get("customer_exid"), RelatedInvoiceNum=payload.get("rel_doc_number"), TraderSystemInvNum=payload.get("invoice_number"))
                elif vouchertype == "Debit Note":
                    fp.OpenDebitNoteWithFreeCustomerData(CompanyName=payload.get("CompanyName") or "",  ClientPINnum=payload.get("customer_pin") or "", HeadQuarters=payload.get("HeadQuarters") or "", Address=payload.get("Address") or "", PostalCodeAndCity=payload.get("PostalCodeAndCity") or "", ExemptionNum=payload.get("customer_exid"), RelatedInvoiceNum=payload.get("rel_doc_number"), TraderSystemInvNum=payload.get("invoice_number"))
                else:
                    errors = {"msg": "Voucher type is not defined (vouchertype)"}
                    handleException()
                    return jsonify({
                        "error_status": str(errors),
                        "verify_url": ""
                    })

                if items:
                    for val in items:
                        # Validated HSCode
                        option_class = val.get("OptionVATClass")
                        if option_class in VAT_CLASSES:
                            if val.get("hscode"):
                                errors = {"msg": "Missing parameter hscode"}
                            if len(val.get("hscode")) != 10:
                                errors = {"msg": "Invalid parameter hscode"}
                            continue
                        # Check parameter NamePLU
                        if len(val.get("stockitemname")) > 30:
                            errors = {"msg": "Parameter stockitemname exceeds max character limit (30)"}
                            
                        # Check if errors exist
                        if errors != "":
                            handleException()
                            return jsonify({
                                "error_status": str(errors),
                                "verify_url": ""
                            })

                        fp.SellPLUfromExtDB(NamePLU=val.get("stockitemname"),OptionVATClass=val.get("vatclass"),Price=val.get("rate"),MeasureUnit=val.get("MeasureUnit"),HSCode=val.get("hscode"),HSName=val.get("HSName"),VATGrRate=val.get("taxrate"),Quantity=val.get("qty"),DiscAddP=val.get("DiscAddP"))
                    
                if led:
                    for val in led:
                        fp.SellPLUfromExtDB(NamePLU=val.get("stockitemname"),OptionVATClass=val.get("vatclass"),Price=val.get("rate"),MeasureUnit=val.get("MeasureUnit"),HSCode=val.get("hscode"),HSName=val.get("HSName"),VATGrRate=val.get("taxrate"),Quantity=val.get("qty"),DiscAddP=val.get("DiscAddP"))


                if items is None and led is None:
                    errors = {
                        "msg": "Missing items list and ledger items"
                    }
                    handleException()
                    return jsonify({
                        "error_status": str(errors),
                        "verify_url": ""
                    })
                fp.ReadVATrates()
                close = fp.CloseReceipt()
                dateTime = fp.ReadDateTime()

                result = {
                    "error_status": "",
                    "invoice_number": payload.get("invoice_number"),
                    "cu_serial_number": payload.get("deviceno")  + " " + str(datetime.datetime.strftime(dateTime, "%d-%m-%Y, %H:%M:%S")),
                    "cu_invoice_number": close.InvoiceNum,
                    "verify_url": close.QRcode,
                    "description": "Invoice Signed Successfully"
                }

                return jsonify(result)

            fp.CancelReceipt()
            fp.serverCloseDeviceConnection()
        except Exception as e:
            handleException()
            return jsonify({
                "error_status": json.dumps({"msg": str(e)}),
                "verify_url": ""
            }
            )

# Try closing receipt if still processing
def handleException() -> None:
    try:
        fp.CloseReceipt()
    except Exception as e:
        ...
    try:
        fp.serverCloseDeviceConnection()
    except Exception as e:
        ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35040)

