
from datetime import datetime
import tzlocal
import csv
import requests
import logging
import json
import PySimpleGUI as sg

sg.theme('DarkGrey8')

layout = [[sg.Text('Please fill in starttime unix, enddtime unix and month'), sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='INONE',default_text='startime')],
          [sg.Input(key='INTWO',default_text='endtime')],
          [sg.Input(key='INTHREE',default_text='month')],
          [sg.Button('Enter'), sg.Button('Exit')],
          [sg.Image(key='-IMAGE-',source='./logo.png')]]

window = sg.Window('ss94 cost and income generator', layout)

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Enter':
        # Update the "output" text element to be the value of "input" element
        starttimeunix = (values['INONE'])
        endtimeunix = (values['INTWO'])
        monthvar = (values['INTHREE'])
        print(starttimeunix)
        csvfilenamekost = 'regnskap kost '+monthvar+' 2022.csv'
        csvfilenameincome = 'regnskap inntekt '+monthvar+' 2022.csv'
        erdadress = 'erd17lrq38ccxftne8r4sa68ntsheq77lz36rq9mdkyzyx8uu2mkjsvsruk9av'
        logging.basicConfig(filename=""+monthvar+".log", level=logging.NOTSET,format= '[%(asctime)s] %(levelname)s - %(message)s')

        def cost():
            logging.debug("COST Function START")
            response = requests.get("https://api.elrond.com/accounts/"+erdadress+"/transfers?sender="+erdadress+"&before="+endtimeunix+"&after="+starttimeunix)
            jsondata=(response.json())
            #create headers in csv before we start with transactionsdata

            with open(csvfilenamekost, mode='a') as numbers_file:
                numbers_writer = csv.writer(numbers_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                numbers_writer.writerow(["Date", "fee_egld", "value_egld","usd_value_egld","nok_value_egld","transaction_hash_url"]) 

                #for loop of all transactions
            for a in jsondata:
                logging.info(json.dumps(a, sort_keys=True, indent=4))
                #convert json data to variables
                fee = float(a["fee"])
                value = float(a["value"])
                ts = float(a["timestamp"])
                txhash = str(a["txHash"])
                #get local timezone based on timestamp in transaction
                local_timezone = tzlocal.get_localzone()
                local_time = datetime.fromtimestamp(ts, local_timezone)
                datets = local_time.strftime("%d-%m-%Y")
                #get price of EGLD at the day of the transaction
                url = "https://api.coingecko.com/api/v3/coins/elrond-erd-2/history?date="+str(datets)
                response2 = requests.get(url)
                response2json = response2.json()
                #change usd or nok to whatever currency you like. If you are changing variable name, please remember to change the same variable in CSV config
                usd = float(response2json["market_data"]["current_price"]["usd"])
                nok = float(response2json["market_data"]["current_price"]["nok"])
                #logging price data in case of error
                logging.info("USD: "+str(usd)+", NOK: "+str(nok))
                with open(csvfilenamekost, mode='a') as numbers_file:
                    numbers_writer = csv.writer(numbers_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    numbers_writer.writerow([local_time.strftime("%Y-%m-%d %H:%M:%S +02:00 (UTC)"), fee/1000000000000000000, value/1000000000000000000,"{:.2f}".format(usd),"{:.2f}".format(nok),"https://explorer.elrond.com/transactions/"+txhash]) 

        def income():
            logging.debug("INCOME Function START")
            response = requests.get("https://api.elrond.com/accounts/"+erdadress+"/transfers?receiver="+erdadress+"&before="+endtimeunix+"&after="+starttimeunix)
            jsondata=(response.json())
            #create headers in csv before we start with transactionsdata

            with open(csvfilenameincome, mode='a') as numbers_file:
                numbers_writer = csv.writer(numbers_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                numbers_writer.writerow(["Date", "value_egld","usd_value_egld","nok_value_egld","transaction_hash_url"]) 

                #for loop of all transactions
            for a in jsondata:
                logging.info(json.dumps(a, sort_keys=True, indent=4))
                #convert json data to variables
                value = float(a["value"])
                ts = float(a["timestamp"])
                txhash = str(a["txHash"])
                #get local timezone based on timestamp in transaction
                local_timezone = tzlocal.get_localzone()
                local_time = datetime.fromtimestamp(ts, local_timezone)
                datets = local_time.strftime("%d-%m-%Y")
                #get price of EGLD at the day of the transaction
                url = "https://api.coingecko.com/api/v3/coins/elrond-erd-2/history?date="+str(datets)
                response2 = requests.get(url)
                response2json = response2.json()
                #change usd or nok to whatever currency you like. If you are changing variable name, please remember to change the same variable in CSV config
                usd = float(response2json["market_data"]["current_price"]["usd"])
                nok = float(response2json["market_data"]["current_price"]["nok"])
                #logging price data in case of error
                logging.info("USD: "+str(usd)+", NOK: "+str(nok))
                with open(csvfilenameincome, mode='a') as numbers_file:
                    numbers_writer = csv.writer(numbers_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    numbers_writer.writerow([local_time.strftime("%Y-%m-%d %H:%M:%S +02:00 (UTC)"), value/1000000000000000000,"{:.2f}".format(usd),"{:.2f}".format(nok),"https://explorer.elrond.com/transactions/"+txhash]) 
        cost()
        income()
        window.close()
