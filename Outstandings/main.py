import requests
from flask import Flask, render_template, url_for, request
from xml.etree import ElementTree as Et

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/ShowOutstanding", methods=["POST"])
def outstanding():
    title = request.form['ReportType']
    from_dt = request.form['fromDt']
    to_dt = request.form['toDt']
    response = get_data(get_payload(title, from_dt, to_dt))
    xml = Et.fromstring(response)
    bill_fixed = []
    bill_closing = []
    bill_due = []
    bill_days = []
    for data in xml.findall("./BILLFIXED"):
        bill_fixed.append(
            BillsFixed(data.find("./BILLDATE").text, data.find("./BILLREF").text, data.find("./BILLPARTY").text))
    for data2 in xml.findall("./BILLCL"):
        bill_closing.append(data2.text)

    for data3 in xml.findall("./BILLDUE"):
        bill_due.append(data3.text)

    for data4 in xml.findall("./BILLOVERDUE"):
        bill_days.append(data4.text)

    return render_template("Outstanding.html", Name=title, from_dt=from_dt, to_dt=to_dt, bill_fix=bill_fixed,
                           bill_cl=bill_closing, bill_due=bill_due, bill_days=bill_days)


def get_data(payload):
    req = requests.post(url="http://localhost:9000", data=payload)
    res = req.text.encode("UTF-8")
    return res


def get_payload(r_type, from_dt, to_dt):
    xml = "<ENVELOPE><HEADER><VERSION>1</VERSION><TALLYREQUEST>EXPORT</TALLYREQUEST>"
    xml += "<TYPE>DATA</TYPE><ID>" + r_type + "</ID></HEADER><BODY>"
    xml += "<DESC><STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>"
    xml += "<SVFROMDATE Type='DATE'>" + from_dt + "</SVFROMDATE><SVTODATE Type='DATE'>" + to_dt
    xml += "</SVTODATE></STATICVARIABLES></DESC></BODY></ENVELOPE>"

    return xml


class BillsFixed:
    def __init__(self, date, ref, party):
        self.date = date
        self.ref = ref
        self.party = party


if __name__ == "__main__":
    app.run(debug=True)
