from flask import Flask, request, render_template, send_file
import pandas as pd
import xml.etree.ElementTree as ET
import io
from utils import ConvertDateFormat
import datetime
import os
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error="No file part in the request")

    file = request.files['file']
    #file_name = request.form['filename']
    renumber = request.form['renumber']
    file_name = f"TTR-MSB{str(pd.Timestamp.now().strftime('%Y%m%d%H%M'))}.xml"

    if file.filename == '':
        return render_template('index.html', error="No file selected")

    if file:
        # Determine if the file is CSV or Excel
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return render_template('index.html', error="Invalid file format. Please upload a CSV or Excel file.")

        # Convert DataFrame to XML
        xml_data = convert_to_xml(df,file_name,renumber)

        # Save XML data in a temporary file for download
        xml_file = io.BytesIO(xml_data.encode())
        xml_file.seek(0)

        return render_template('index.html', xml_data=xml_data)

    return render_template('index.html', error="An error occurred while processing the file")

def convert_to_xml(dataframe,file_name,renumber):
    root = ET.Element('ttr-msbList', xmlns="http://austrac.gov.au/schema/reporting/TTR-MSB-2-0")
    ET.SubElement(root,"reNumber").text = str(renumber)
    ET.SubElement(root,"fileName").text = str(file_name)
    

    dataframe.columns = dataframe.columns.str.strip().str.lower().str.replace(" ","")
    

    d = dataframe["receiptno."]
    num_dict = {}
    num_list = []

    for num in list(d):
        if num in num_dict:
            num_dict[num] += 1
        else:
            num_dict[num] = 1
        
        if num in num_list:
            pass
        else:
            num_list.append(num)

    ET.SubElement(root,"reportCount").text = str(rpt)
    
    rpt = 1

    for i in range(len(num_list)):
        
    # for k,v in num_dict.items():
        
        # filtered_rows = dataframe[dataframe["receiptno."] == k]
        filtered_rows = dataframe[dataframe["receiptno."] == num_list[i]]

        if filtered_rows["localamount"].sum() > 10000:
            row = filtered_rows.iloc[0]
          
            ttr_msb = ET.SubElement(root, 'ttr-msb')
            ttr_msb.set('id', str("rpt-")+str(rpt).zfill(2))
            rpt += 1

            ''' --> header  '''
            header = ET.SubElement(ttr_msb, 'header')
            header.set('id', "hdr-01-01")

            ''' --> header 
                    --> header tree
            '''
            ET.SubElement(header, 'txnRefNo').text = str(row["comments"])

            reportingBranch = ET.SubElement(header, 'reportingBranch')
            reportingBranch.set('id', "rbr-01-01")

            '''
                --> header
                    --> header tree (reportingBranch)
                        -->  reportingBranch tree
            '''
            
            ET.SubElement(reportingBranch, 'name').text = str(row["firstname"])

            header_address = ET.SubElement(reportingBranch, 'address')
            header_address.set('id', "adr-01-01")

            '''
                --> header
                    --> header tree (header address)
                        --> header address tree
            '''
            ET.SubElement(header_address, 'addr').text = str(row["address1"])
            s = row["citytown"]
            suburb = str(s).split()
            try:
                s1 = suburb[0]
            except:
                s1 = None
            
            try:
                s2 = suburb[1]
            except:
                s2 = None

            try:
                s3 = suburb[2]
            except:
                s3 = None
            
            suburb = ET.SubElement(header_address, 'suburb').text = str(s1)

            state = ET.SubElement(header_address, 'state').text = str(s2)

            postcode = ET.SubElement(header_address, 'postcode').text = str(s3)
            
            ''' 
                --> customer
            '''
            customer = ET.SubElement(ttr_msb, 'customer')
            customer.set('id', "cst-01-01")

            '''
                --> customer
                    --> customer tree
            '''
            ET.SubElement(customer, 'fullName').text = str(row["lastname"])

            customer_mainAddress = ET.SubElement(customer, 'mainAddress')
            customer_mainAddress.set('id', "adr-01-02")

            indOcc = ET.SubElement(customer, 'indOcc')
            indOcc.set('id', "ioc-01-01")

            dobt = row["dateofbirth"]
            dobtconv = datetime.datetime.strptime(dobt, "%d/%m/%Y").strftime("%Y-%m-%d")

            ET.SubElement(customer, 'dob').text = str(dobtconv)

            identification = ET.SubElement(customer, 'identification')
            identification.set('id', "idt-01-01")

            customeridtype = str(row["customeridtype"]).strip().lower().replace(" ","")
            if customeridtype == "passport":
                ET.SubElement(customer, 'electDataSrc').text = str("P")
            if customeridtype == "drivinglicense":
                ET.SubElement(customer, 'electDataSrc').text = str("D")
            else:
                _type = ET.SubElement(customer, 'electDataSrc')



            ''' --> customer
                    -- > customer address tree (customer_mainAddress)
            '''
            ET.SubElement(customer_mainAddress, 'addr').text = str(row["address1"])

            ET.SubElement(customer_mainAddress, 'suburb').text = str(s1)

            ET.SubElement(customer_mainAddress, 'state').text = str(s2)

            ET.SubElement(customer_mainAddress, 'postcode').text = str(s3)

            ET.SubElement(customer_mainAddress, 'country').text = str(row["country"])

        

            '''
                --> customer
                    --> custom ind doc tree (indOcc)
            '''
            ET.SubElement(indOcc, 'description').text = str(row["occupation"])


            '''
                --> customer
                    -->  identification tree (identification)
            '''
            customeridtype = str(row["customeridtype"]).strip().lower().replace(" ","")
            if customeridtype == "passport":
                ET.SubElement(identification, 'type').text = str("P")
            if customeridtype == "drivinglicense":
                ET.SubElement(identification, 'type').text = str("D")
            else:
                _type = ET.SubElement(identification, 'type')

            ET.SubElement(identification, 'number').text = str(row["customeridno"])

            ET.SubElement(identification, 'issuer').text = str(row["customeridissuer"])

            '''
                --> individual conducting txn
            '''
            individual_conducting_txn = ET.SubElement(ttr_msb, 'individualConductingTxn')
            individual_conducting_txn.set('id', "ind-01-01")
            
            '''
                --> individual conducting txn
                    --> individual conducting txn tree (individual_conducting_txn)
            '''
            ET.SubElement(individual_conducting_txn, 'fullName').text = str(row["teller"])

            individual_mainAddress = ET.SubElement(individual_conducting_txn, 'mainAddress')
            individual_mainAddress.set('id', "adr-01-03")

            '''
                --> individual conducting txn
                    --> individual conducting main address tree (individual_mainAddress)
            '''
            ET.SubElement(individual_mainAddress, 'addr').text = str(row["address1"])
            
            ET.SubElement(individual_mainAddress, 'suburb').text = str(s1)

            ET.SubElement(individual_mainAddress, 'state').text = str(s2)

            ET.SubElement(individual_mainAddress, 'postcode').text = str(s3)
            
            ET.SubElement(individual_mainAddress, 'country').text = str(row["country"])

            '''
                -> recipient
            '''
            recipient = ET.SubElement(ttr_msb, 'recipient')
            recipient.set('id', "rcp-01-01")

            '''
                --> recipient
                    --> recipient tree (recipient)
            '''
            sameAsCustomer = ET.SubElement(recipient, 'sameAsCustomer')
            sameAsCustomer.set('refId', "cst-01-01")
            
            '''
                --> transaction
            '''
            transaction = ET.SubElement(ttr_msb, 'transaction')
            transaction.set('id', "txn-01-01")
            
            '''
                --> transaction
                    --> transaction tree (transaction)
            '''
            ET.SubElement(transaction, 'txnDate').text = str(ConvertDateFormat(str(row["transactiondate"])))


            totalAmount = ET.SubElement(transaction, 'totalAmount')
            totalAmount.set('id', "tam-01-01")

            currency = ET.SubElement(totalAmount, 'currency').text = str("AUD")
            # ET.SubElement(totalAmount, 'amount').text = str(row["localamount"])
            ET.SubElement(totalAmount, 'amount').text = str(round(filtered_rows["localamount"].sum(),2))

            designatedSvc = ET.SubElement(transaction, 'designatedSvc').text = str("CUR_EXCH")
            
            moneyReceived = ET.SubElement(transaction, 'moneyReceived')
            moneyReceived.set('id', "mrv-01-01")

            moneyProvided = ET.SubElement(transaction, 'moneyProvided')
            moneyProvided.set('id', "mpr-01-01")

            '''
                --> transaction
                    --> transaction tree (transaction_
                        --> total amount tree (totalamont)
            '''
            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money received tree (moneyReceived)
            '''

            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money received tree (moneyReceived)
                            --> cash tree (cash)
            '''
            
            moneyReceived_cash = ET.SubElement(moneyReceived, 'cash')
            for i in range(len(filtered_rows)):
                # print(filtered_rows.iloc[i]['fxamount'])

            # for _, row in filtered_rows.iterrows():
                # print(_)

                foreignCash = ET.SubElement(moneyReceived_cash, 'foreignCash')
                foreigncash_id = str("fca-01-") + str(i+1).zfill(2)
                foreignCash.set('id', foreigncash_id)

                ET.SubElement(foreignCash, 'currency').text = str(filtered_rows.iloc[i]["currencycode"])

                amount = ET.SubElement(foreignCash, 'amount').text = str(round(filtered_rows.iloc[i]["fxamount"],2))

            # ET.SubElement(amount, col).text = str(row["loca"])


            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money providerd tree (moneyProvided)
            '''
            moneyProvided_cash = ET.SubElement(moneyProvided, 'cash')
            mpauscash = ET.SubElement(moneyProvided_cash, 'ausCash')
            mpauscash.set('id', "csh-01-01")
            ET.SubElement(mpauscash, 'currency').text = str("AUD")
            ET.SubElement(mpauscash, 'amount').text = str(row["localamount"])
            
            
            nonCashProvided = ET.SubElement(moneyProvided, 'nonCashProvided')

            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money providerd tree (moneyProvided)
                            -->  cash tree (money_provided_cash)
            '''
            

            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money providerd tree (moneyProvided)
                            -->  cash tree (money_provided_cash)
            '''
            

            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money providerd tree (moneyProvided)
                            --> non cash provided tree (fco)
            '''
            # fco = ET.SubElement(nonCashProvided, 'fco')

            '''
                --> transaction
                    --> transaction tree (transaction)
                        --> money providerd tree (moneyProvided)
                            --> non cash provided tree (fco)
                                -->  (fco)
            '''
            # amount = ET.SubElement(fco, 'amount')

        # dataframe.columns = dataframe.columns.str.strip().str.lower().str.replace(" ","")
        
        # for _, row in dataframe.iterrows():
        #     print(row["Terminal"])
            # item = ET.SubElement(root, 'item')

            # for col, value in row.items():
            #     print(col)
            #     ET.SubElement(item, col).text = str(value)

    xml_data = ET.tostring(root, encoding='unicode')
    return xml_data


@app.route('/download')
def download_xml():
    xml_data = request.args.get('xml_data', '')
    if xml_data:
        xml_file = io.BytesIO(xml_data.encode())
        xml_file.seek(0)
        return send_file(xml_file, as_attachment=True, download_name="data.xml", mimetype='text/xml')
    else:
        return render_template('index.html', error="XML data not found. Please upload a file first.")

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
