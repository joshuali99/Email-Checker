import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from imap_tools import MailBox, Q
import datetime
import pandas as pd
import re
import bestBuy

#set up the email connection in imap and imap_tools
username = ""
password = ""
imap = imaplib.IMAP4_SSL("imap.gmail.com")
mailbox = MailBox("imap.gmail.com")
imap.login(username, password)
mailbox.login(username, password, initial_folder = "INBOX")
status, numberMessages = imap.select()

#date from which we want the emails
year = 2020
day = 10
month = 5

#fetches Best Buy emails
bestBuyMessages = mailbox.fetch(Q(from_="BestBuyInfo@emailinfo.bestbuy.com", date_gte=datetime.date(year,month,day)))

#creates output dataframe that will be added to
output = pd.DataFrame(index = ['BBY01'], columns = ['Shipping #', 'Date', 'Product # Quantity', 'Destination'] )
currentOrders = pd.read_csv(r'orderConfirmations.csv')

# loops through these Best Buy emails
for msg in bestBuyMessages:
    #    message.subject          # str: 'some subject'
    
    dateReceived = msg.date_str
    msgHtml = msg.html

    #Checks if it is a "received order," so no shipping # yet.
    if "We've received your order" in msg.subject:

        modelAndQuantity = str(bestBuy.findModelAndQuantity(msgHtml))
        destination = bestBuy.findShippingLocation(msgHtml)
        orderNo = bestBuy.findOrderNo(msgHtml)

        append = pd.DataFrame({'Shipping #': None, 'Date': dateReceived, 'Product # Quantity': modelAndQuantity, 'Destination': destination}, index = [orderNo])
        output = output.append(append)

    #Checks if it is a "Your order, "BBY01-[NUMBER]" has shipped," in which case can derive the tracking number. 
    elif "Your order" in msg.subject:
        print("hi")
        i = 1+1
        bestBuy.findTrackingNumber(msgHtml)

output.to_csv(r'orderConfirmations.csv')