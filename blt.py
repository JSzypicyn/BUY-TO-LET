from bs4 import BeautifulSoup
import requests

import pandas as pd
import datetime
import os
# os.chdir('C:\Jovian\Python') update directory path if your running this on your local machine
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import csv
import re

# TODO: add a list of locations and scan through all of them all at Once


locations = '5E550'
base_url = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%' + location + '&sortType=1&index='
properties_per_page = 24
num_properties = 900
csv_filename = 'filename_temp.csv'
csv_location = location + '_data.csv'

key_phrase_list = ["return", "pcm", "investors"
                   "rental", "income", "investment", "buy-to-let", "buy to let",
                    "tenanted"]

leasehold_charges =["service charge", "Service charge", "Service Charge",
                    "ground rent", "Ground rent", "Ground Rent"]

# Collect & convert HTML data as text , collects multiple pages in form of pagdict list
def page_content(base_url,num_properties,properties_per_page):
    i=00
    listf=[]
    pagedict=[]
    while i < num_properties:
        i += properties_per_page
        listf.append(str(i))
    page_idx = listf

    for item in page_idx:
        page = requests.get(base_url+(item))
        if page.status_code !=200:
                raise Exception(f"Unable to download {base_url+(item)}")
        page_content = page.text
        pagedict.append(page_content)
    return pagedict

def det_page_content(base_url,num_properties,properties_per_page):
    i=00
    listf=[]
    pagedict=[]

    for i in range(num_properties):
        page = requests.get(base_url+"#/?channel=RES_BUY")
        if page.status_code !=200:
                raise Exception(f"Unable to download {base_url}")
        page_content = page.text
        pagedict.append(page_content)
    return page_content

def html_parse(pagedict):
    page_doc=[0]*len(pagedict)
    for i in range(len(pagedict)):
        page_doc[i] = BeautifulSoup(pagedict[i], features="html.parser")

    return page_doc

def data_in_text(pagedict,page_doc):
    page_links1 = []

    price_tag=[0]*len(pagedict)
    date_tag=[0]*len(pagedict)
    address_tag=[0]*len(pagedict)
    bed_tag=[0]*len(pagedict)
    number_tag=[0]*len(pagedict)
    agent_tag=[0]*len(pagedict)
    id_tag=[0]*len(pagedict)
    yield_info=[0]*len(pagedict)

    for i in range(len(pagedict)):

        price_tag[i]=page_doc[i].find_all('div', class_="propertyCard-priceValue")
        date_tag[i]=page_doc[i].find_all('span',class_="propertyCard-branchSummary-addedOrReduced")
        address_tag[i]=page_doc[i].find_all('address',class_="propertyCard-address")
        bed_tag[i]=page_doc[i].find_all('h2',class_="propertyCard-title")
        number_tag[i]=page_doc[i].find_all('a',class_="propertyCard-contactsPhoneNumber")
        agent_tag[i]=page_doc[i].find_all('img',class_="propertyCard-branchLogo-image")
        id_tag[i]=page_doc[i].find_all('a',class_="propertyCard-anchor")

    for i in range(len(pagedict)):
        for j in range(0,25):
            try:
                page_links1.append({'Data_Date': date.today().strftime("%d/%m/%Y"),'Property_Published':date_tag[i][j].text.strip().replace(",","-"),'Price':price_tag[i][j].text.strip().replace(",",""),'Address':address_tag[i][j].text.strip().replace(",","-").replace("\n",""),'No_of_Beds':bed_tag[i][j].text.strip().replace(",","-"),'Agent_Name':agent_tag[i][j]['alt'].strip().replace(",","-").replace(" Logo",""),'Contact_Number':number_tag[i][j].text.strip(),'Property_link':'https://www.rightmove.co.uk/properties/'+id_tag[i][j]['id'].replace("prop","")})
            except IndexError:
                pass
            continue

    return(page_links1)

def det_data_in_text(pagedict,page_doc):
    page_links1 = []

    description=[0]*len(pagedict)
    data_present=[0]*len(pagedict)
    charges_present=[0]*len(pagedict)
    for i in range(len(pagedict)):
        description[i]=page_doc[i].find_all('div',class_=re.compile("STw8udCxUaBUMfOOZu0iL"))
        desc = str(description[i])

        for word in key_phrase_list:
            if desc.find(word) != -1:
                data_present[i] = 1

        for word in leasehold_charges:
            if desc.find(word) != -1:
                charges_present[i] = 1
    # make a dataframe out of description and data_present and return it

    data = {'Description': description,
            'Key_Words_Present': data_present,
            'Charges_Present': charges_present}

    df = pd.DataFrame(data)

    return(df)

def find_yield_data(df):
    num_props = len(df)
    details_pagedict=[]

    for i in range(num_props):
        url_to_search = df['Property_link'].iloc[i]
        details_pagedict.append(det_page_content(url_to_search,1,1))

    det_page_doc = html_parse(details_pagedict)
    data_present_df = det_data_in_text(details_pagedict,det_page_doc)
    df = df.reset_index(drop=True)
    df = pd.concat([df, data_present_df.reindex(df.index)], axis=1)
    df=df[df['Key_Words_Present'] != 0]
    # df=df[df['Charges_Present'] != 0]
    df.to_csv(csv_location)
    return df



def write_csv(items, path):

    with open(path,'w', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write the headers in the first line
        headers = list(items[0].keys())
        writer.writerow(headers)
        # Write one item per line
        for item in items:
            values = []
            for header in headers:
                values.append(str(item.get(header, "")))
            writer.writerow(values)


def test_run():
    pagedict = page_content(base_url,num_properties,properties_per_page)

    page_doc = html_parse(pagedict)

    data_text = data_in_text(pagedict,page_doc)

    csv_file  = write_csv(data_text,csv_filename)

    df = pd.read_csv(csv_filename)

    df['Price'] = df['Price'].str.replace('£','')
    df['Price'] = df['Price'].str.replace('NaN','')
    df['Price'] = df['Price'].str.replace('POA','')
    df['Price'] = df['Price'].str.replace(' ','')
    df['Price'] = df['Price'].str.replace('nan','')
    df['Price'] = df['Price'].str.replace('ComingSoon','')


    new_df=df[df['Price'] != '']

    new_df['Price']=new_df['Price'].astype(int)
    new_df=new_df[new_df['Price'] < 100000]

    yield_df = find_yield_data(new_df)

    Total_properties = yield_df['Price'].count()
    print(f"Total {Total_properties} properties are currently available for sale.")

    # histogram presentation
    plt.hist(yield_df['Price'],alpha=0.5,bins=10)
    plt.title("Histogram of Property Price")
    plt.xlabel("Price")
    plt.ylabel("Frequency")
    plt.show()

if __name__ == "__main__":

    test_run()
