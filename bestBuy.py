import re
    
#this method finds the order number by looping through the text to find "BBY01" and just assigns string after that
def findOrderNo(msgHtml):
    orderNoLocation = msgHtml.find("BBY01")
    orderNo = msgHtml[orderNoLocation:orderNoLocation+18]
    return orderNo

#this method finds the order total by finding the last formatted "$dollars.cents" that appears in the HTML.
def findOrderTotal(msgHtml):
    costPattern = re.compile(r'\$\d{1,3},?\d{1,3}\.\d{2}')
    costList = costPattern.findall(msgHtml)
    orderTotal = costList[len(costList)-1]
    return orderTotal

#Finds all models in the order and the quantities associated with each model. Returns dictionary, with key as Model number and value as number of each model.
def findModelAndQuantity(msgHtml):

    #parses out the "sections" that includes model number and the Qty into a group of strings
    modelPattern = re.compile(r'<strong>Model: </strong>.*?>\d<', re.DOTALL)
    allModels = modelPattern.findall(msgHtml)

    modelQtyDict = {}
    
    #loops through all those "sections"
    for i in allModels:

        #finds the model number within that section
        modelNumber = re.compile(r'</strong>(.*?)<br', re.DOTALL)
        modelNumber = re.search(modelNumber, i).group(1)

        #finds the quantity of that model within that section
        modelQuantity = re.compile(r'>(\d)<')
        modelQuantity = re.search(modelQuantity, i).group(1)

        #adds that model/quantity to dictionary, depending on whether that model/quantity already is inside the dictionary.
        if modelNumber in modelQtyDict:
            modelQtyDict[modelNumber] += int(modelQuantity)
        else:
            modelQtyDict[modelNumber] = int(modelQuantity)

    return modelQtyDict

#returns delivery location of order based on ORDER NUMBER. (So if one order number has separate delivery locations, this should be changed.)
def findShippingLocation(msgHtml):

    #parse out the section with the shipping location
    shippingSectionPattern = re.compile(r'(Get it By:|Will Ship By:)(.*?</span>)', re.DOTALL) #need to test this on a Will Ship By, most recent emails are "Get it By"
    shippingSection = re.search(shippingSectionPattern, msgHtml).group(2)

    #parse out the actual shipping location
    shippingLocationPattern = re.compile(r'<br/>(.*?)</span>', re.DOTALL)
    shippingLocation = re.search(shippingLocationPattern, shippingSection,).group(1)

    #remove the Brs and replace with a comma in the shipping location
    removeBr = re.compile(r'<br/>', re.DOTALL)
    shippingLocation = re.sub(removeBr, ', ', shippingLocation)

    return shippingLocation        

#Uses the "Your order... has shiped" to parse out the tracking number, returns both the tracking number and the corresponding Order Number
def findTrackingNumber(msgHtml):
    
    #parse out the section with the tracking number
    trackingNumberPattern = re.compile(r'Tracking #.*?</a>', re.DOTALL)
    trackingNumberSection = re.search(trackingNumberPattern, msgHtml).group()

    #parse out the tracking number from the section
    trackingNumberPattern = re.compile(r'">(.*?)</a>', re.DOTALL)
    trackingNumber = re.search(trackingNumberPattern, trackingNumberSection).group(1)

    return trackingNumber, findOrderNo(msgHtml)

#returns the entire order based on the "We've received..." email, so it doesn't actually have the tracking number.
def completeTxt(msgHtml, date):
    output = findOrderNo(msgHtml) + " " + date + " " + findOrderTotal(msgHtml) + " " + findShippingLocation(msgHtml)
    products = ""
    productList = findModelAndQuantity(msgHtml)
    for i in productList:
        products += i + " " + str(productList[i]) + " "
    
    return output, products