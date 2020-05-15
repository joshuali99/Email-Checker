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
import csv

#set up the email connection in imap and imap_tools
username = "INSERT EMAIL"
password = "INSERT PASSWORD"
imap = imaplib.IMAP4_SSL("imap.gmail.com")
mailbox = MailBox("imap.gmail.com")
imap.login(username, password)
mailbox.login(username, password, initial_folder = "INBOX")
status, numberMessages = imap.select()

#date from which we want the emails
year = 2020
day = 8
month = 5

#fetches Best Buy emails
bestBuyMessages = mailbox.fetch(Q(from_="BestBuyInfo@emailinfo.bestbuy.com", date_gte=datetime.date(year,month,day)))

#creates output dataframe that will be added to
orderConfirmations = pd.DataFrame(index = ['BBY01'], columns = ['Shipping #', 'Date', 'Product # Quantity', 'Destination', 'Cost'])
shippedOrders = pd.DataFrame(index = ['BBY01'], columns = ['Shipping #', 'Date', 'Product # Quantity', 'Destination', 'Cost'] )
#orderConfirmations = pd.read_csv(r'orderConfirmations.csv', index_col = 0)
#shippedOrders = pd.read_csv(r'shippedOrders.csv')

# loops through these Best Buy emails
for msg in bestBuyMessages:
    
    dateReceived = msg.date_str
    msgHtml = msg.html

    #Checks if it is a "received order," so no shipping # yet.
    if "We've received your order" in msg.subject:
        #assigns the values of model/quantity, destination, and order number
        modelAndQuantity = str(bestBuy.findModelAndQuantity(msgHtml))
        destination = bestBuy.findShippingLocation(msgHtml)
        orderNo = bestBuy.findOrderNo(msgHtml)
        cost = bestBuy.findOrderTotal(msgHtml)

        #creates a dataframe and appends to a series
        append = pd.DataFrame({'Shipping #': None, 'Date': dateReceived, 'Product # Quantity': modelAndQuantity, 'Destination': destination, 'Cost': cost}, index = [orderNo])
        orderConfirmations = orderConfirmations.append(append)

    #Checks if it is a "Your order, "BBY01-[NUMBER]" has shipped," in which case can derive the tracking number. 
    elif "Your order" in msg.subject:

        trackingNo, orderNo = bestBuy.findTrackingNumber(msgHtml)
        try:
            found = orderConfirmations.loc[orderNo]
            orderConfirmations = orderConfirmations.drop(orderNo)
            found.update(pd.Series([trackingNo], index = ['Shipping #']))
            shippedOrders = shippedOrders.append(found)
        except KeyError:
            pass



shippedOrders.to_csv(r'shippedOrders.csv')
orderConfirmations.to_csv(r'orderConfirmations.csv')