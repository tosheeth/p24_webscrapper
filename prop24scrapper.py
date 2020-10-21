from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import datetime
import pandas as pd
import progressbar

fname = 'capetown.csv'

suburbs = []
url = 'https://www.property24.com/for-sale/cape-town/western-cape/432'
className = 'p24_regularTile js_rollover_container'
data = {
        'suburb': [],
        'type': [],
        'price':[],
        'beds': [],
        'baths': [],
        'garages': [],
        'm2': [],
        'ppm2': [],
        'date': [],
        'url': []
}

df = ''

page = uReq(url)
html = page.read()
pageSoup = soup(html, "html.parser")
props = pageSoup.findAll('div',{'class':className})
urls = []

def toInt(line):
        a = []
        for i in line:
                if (i.isdigit() or i == '.'): a.append(i)

        result = ''
        result = result.join(a)
        return result

lastPageInfo = pageSoup.findAll('a',{'rel':'nofollow'})

lastpage = 2
for i in lastPageInfo:
        if i.text.isdigit():
                lastpage = int(i.text)

print(lastpage)
for i in range(1,lastpage):
        urlCurr = url + '/p' + str(i)

        try:
                page = uReq(url)
                html = page.read()
                pageSoup = soup(html, "html.parser")
                props = pageSoup.findAll('div',{'class':className})
        except:
                break
        for prop in props:
                urls.append('https://www.property24.com' + prop.a['href'])
                

print('Got URLs')

for i in range(len(urls)):
        link = urls[i]
        data['url'].append(link)
        page = uReq(link)
        html = page.read()
        pageSoup = soup(html, "html.parser")
        link_arr = link.split('/')
        
        # Get Suburb
        suburb = link_arr[link_arr.index('for-sale') + 1]
        data['suburb'].append(suburb)

        # Get Price
        price = 'na'
        try:
                priceInfo = pageSoup.findAll('div',{'class':'p24_price'})
                price = toInt(priceInfo[1].text)
        except:
                pass
        data['price'].append(price)

        # Get Beds
        beds = 'na'
        try:
                bedsInfo = pageSoup.findAll('li',{'title':'Bedrooms'})
                beds = toInt(bedsInfo[0].text)
        except:
                pass
        data['beds'].append(beds)

        # Get Baths
        baths = 'na'
        try:
                bathsInfo = pageSoup.findAll('li',{'title':'Bathrooms'})
                baths = toInt(bathsInfo[0].text)
        except:
                pass
        data['baths'].append(baths)

        # Get Garage
        garage = 'na'
        try:
                garageInfo = pageSoup.findAll('li',{'title':'Parking Spaces'})
                garage = toInt(garageInfo[0].text)
        except:
                pass
        data['garages'].append(garage)

        # Get m2
        msq = 'na'
        try:
                msqInfo = pageSoup.findAll('li',{'title':'Floor Size'})
                msq = toInt(msqInfo[0].text)
        except:
                pass
        data['m2'].append(msq[:len(msq)-1])

        # Get Price Per m2
        ppm2 = 'na'
        try:
                ppm2 = str(float(price)/float(msq))
        except:
                pass
        data['ppm2'].append(ppm2)

        #Get listing date
        date = 'na'
        features = pageSoup.findAll('div',{'class':'p24_info'})
        titles = pageSoup.findAll('div',{'class':'col-xs-6 p24_propertyOverviewKey'})
        titleList = []

        for i in titles:
                if not i.text == 'Street Address':
                        titleList.append(i.text)
        try:
                date = features[titleList.index('Listing Date')].text
        except:
                pass
        data['date'].append(date)

        #Get listing type
        listType = 'na'
        try:
                listType = features[titleList.index('Type of Property')].text
        except:
                pass

        data['type'].append(listType)
        
        
print('Got Data')
suburbs = list(set(data['suburb']))       
df = pd.DataFrame(data)
print('Created Dataframe')

for suburb in suburbs:
        currDf = df[(df.suburb == suburb)]
        filename = suburb + '.txt'
        currDf.to_csv(filename)
        print('Data Saved To CSV: ',filename)

print('Complete')
