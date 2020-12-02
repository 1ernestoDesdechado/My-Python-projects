#!/usr/bin/env python
# coding: utf-8

# ---
# Purpose of the research 
# ---
# The purpose of this research is to make a research of Ukranian Jeep market on the real data basis.
# For this purpose we selected web site 'https://auto.ria.com'/.
# We would like parse maximum available characteristics for analysis, such as title, region, year of production,fuel type etc.
# 
# We prefer to use classic ETAC approach:
# extract,transform analyse,conclude.

# ---
# Extraction 
# ---
# At this stage we import necessary libraries, connect to web site and parse all necessary data.

# In[45]:


#We import all necessary libraries for scraping and further analysis

import requests
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#We create Constants

URL='https://auto.ria.com/car/jeep/&?size=10&?count=10'
#URL='https://auto.ria.com/search/?indexName=auto,order_auto,newauto_search&brand.id[0]=32&abroad.not=-1&custom.not=-1&size=10'
#HOST='https://auto.ria.com'
HEADERS={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111'
,'accept':'*/*'}

#We scrape necessary data via request and beautifulSoup from all available pages

r=requests.get(URL,HEADERS)
soup=BeautifulSoup(r.text,'html.parser')

#I Count number of pages at web site 
# Default settings are  a bit complicated and show us default number of pages with hiding part of the data.
# But we found the ogic that shows that number of pages that show all the data are more twice than default one and three times are more than default one.

pagNum= soup.find_all('span',class_='page-item mhide')

if pagNum:
    pgInt = int(pagNum[-1].get_text())*3
else:
    pgInt = 1
print(f'Number of pages not less than {pgInt}')           


# In[55]:


#Parsing necessary data        
cars1_20=[]


for page in range(0,pgInt):
    print(f'Parsing page{page} ...' )
    URL_UPD = f'https://auto.ria.com/search/?indexName=auto,order_auto,newauto_search&brand.id[0]=32&price.currency=1&abroad.not=-1&custom.not=-1&page={page}&size=10'
     
    print(URL_UPD)           
    rUpd = requests.get(URL_UPD)
    soup1 = BeautifulSoup(rUpd.text,'html.parser')
    items=soup1.find_all('div',class_='content')
            
    for item in items:
        cars1_20.append({
            'title': item.find('span',class_='blue bold').get_text(strip=True),
                    #'link': HOST + item.find('a').get('href'),
            'price': item.find('div',class_='price-ticket').get_text(strip=True).replace('•',''),
            'city': item.find('li',class_='item-char view-location').get_text(),
            'mileage': item.find('li',class_='item-char').get_text(),
            'eng_type/volume': item.find('li',class_='item-char view-location').find_next('li').get_text(),
            'Car year': item.find('div',class_='item ticket-title').get_text(strip=True)[-4:]})
                
                
print(cars1_20)
#print(items)
    #(distance,city,Eng_type,volume,auto/manual)


# In[57]:


#I convert the data into dataframe
myParsedDF1=pd.DataFrame(cars1_20)
myParsedDF1.info()


# In[58]:


#In order to match dataframe with first page(10 records) I call 10 first records
myParsedDF1.head(10)


# In[59]:


#In order to match dataframe with last page(10 records) I call 10 first records
myParsedDF1.tail(10)


# In[60]:


# At this step I make a copy of dataframe (if I break something- there is no need to parse again)

myParsedDF=myParsedDF1.copy()
myParsedDF.info()


# ---
# Transformation of data
# ---
# We see from above that columns "price" and "eng_type/volume" need to be splitted in order to get detailed information.
# We assume that the all the parts of each column are filled on the the same logic. But still after splitting we will examine unique records in order to check abnormal records.
# 
# We examined all columns and see that formats should be in line with substance:
# USD,Hryvnya, Car year, mileage need to be converted to integer and Volume_L to float
# 
# Method info shows that volume is less then other columns. 
# For parsed columns we need to check if abnormal records exist. 
# Price is fully filled in and successfully converte to integer, that is why we assume that price is successful.
# 
# We also assume that one and the same model could be written both in upper and lower cases? that is why we convert it to lower.
# 
# Title: Titles are written in free form, that is why duplicates are possible.
# For our purposes we will not deep inside modelling, we will avoid misprints and differences in writing
# We assume that cars with prefixes 4x4,4 na 4 and cars without them are the same ones.
# We also assume that altitude and latitude are the same.
# 
# Replacements to be done:
# 
# latitude: latitud, latituti
# trailhawk: trail hawk
# official:oficial 
# replace with nothing: avtomat laredo, gas
# 4x4: 4wd 4.0, 4 x 4  
# unlimited: unlimite
# 
# 

# In[63]:



myParsedDF[['USD','Hryvnya']]=myParsedDF['price'].str.split('$', 1, expand=True)
myParsedDF['Hryvnya']=myParsedDF['Hryvnya'].str.replace('грн','')
myParsedDF['Hryvnya']=myParsedDF['Hryvnya'].str.replace(' ','')
myParsedDF['USD']=myParsedDF['USD'].str.replace(' ','')
myParsedDF[['Eng_type','Volume_L']]=myParsedDF['eng_type/volume'].str.split(',', 1, expand=True)
myParsedDF['Volume_L']=myParsedDF['Volume_L'].str.replace(' л.','')
myParsedDF['title']=myParsedDF['title'].str.lower()
myParsedDF.head()


# In[64]:



myParsedDF = myParsedDF.replace(to_replace=['latitud', 'latituti'],value='latitude')
myParsedDF = myParsedDF.replace(to_replace=['trail hawk'],value='trailhawk')
myParsedDF = myParsedDF.replace(to_replace=['4wd', '4.0','4 х 4', '4 x 4'],value='4x4')


# In[65]:


#At this step I convert data to applicable formats
myParsedDF['USD']=myParsedDF['USD'].astype(int)
myParsedDF['Hryvnya']=myParsedDF['Hryvnya'].astype(int)
myParsedDF['Volume_L']=myParsedDF['Volume_L'].astype(float)
myParsedDF['Car year']=myParsedDF['Car year'].astype(int)

myParsedDF.info()
myParsedDF


# In[70]:


# I strip data from blanks and once occasional duplicate
myParsedDF['Eng_type']=myParsedDF['Eng_type'].str.replace('Дизтопливо','Дизель')
myParsedDF['Eng_type']=myParsedDF['Eng_type'].str.strip(' ')


# In[71]:


#I check in columns if any empty or abnormal records exist


icheckEng_type=myParsedDF['Eng_type'].unique()
icheckEng_type


# In[72]:


# Abnormals exist, liters instead of Eng type. In this case we collect them together and see how material these are.
# Only less then 2%

wrongEng=myParsedDF.query('Eng_type == "2.4 л." or Eng_type == "2.7 л." or Eng_type == "3.2 л." or Eng_type == "4 л." or Eng_type == "2 л." or Eng_type == "2.5 л." or Eng_type == "3.6 л." or Eng_type == "3.1 л."')
wrongEng

wrongEng.info()
wrongEng.head()


# In[73]:


#Same check we do with Volume_L. Nan records exist. We need to check how may items are not filled in/ 
icheckVolume_L=myParsedDF['Volume_L'].unique()
icheckVolume_L


# In[74]:


# Same check for prices show that there is no missing data
ww=myParsedDF[myParsedDF['USD'].isna()]
ww.info()
#ww=myParsedDF[myParsedDF['Hryvnya'].isna()]
#ww.info()


# In[75]:


myParsedDF_U=myParsedDF[myParsedDF['Volume_L'].notna()]
myParsedDF_U=myParsedDF_U.query('Eng_type != "2.4 л." or Eng_type != "2.7 л." or Eng_type != "3.2 л." or Eng_type != "4 л." or Eng_type != "2 л." or Eng_type != "2.5 л." or Eng_type != "3.6 л." or Eng_type != "3.1 л."')



# In[76]:


wrongEng=myParsedDF_U.query('Eng_type == "2.4 л." or Eng_type == "2.7 л." or Eng_type == "3.2 л." or Eng_type == "4 л." or Eng_type == "2 л." or Eng_type == "2.5 л." or Eng_type == "3.6 л." or Eng_type == "3.1 л."')
wrongEng


# In[77]:


#Same check we do with mileage. Nan records exist. We need to check how may items are not filled in. 
myParsedDF_U['mileage'] = myParsedDF_U['mileage'].str.strip(' ')
myParsedDF_U['mileage'] = myParsedDF_U['mileage'].str.replace(' тыс. км','')
myParsedDF_U['mileage'] = myParsedDF_U['mileage'].str.replace('без пробега','0')
myParsedDF_U['mileage'] = myParsedDF_U['mileage'].astype(int)
icheckVolume_M=myParsedDF_U['mileage'].unique()
icheckVolume_M


# ---
# Transformation conclusion
# ---
# In statistics confidence interval usually varies between 5-10. We have delete blank volumes and wrong Eng_type and see 8% decrease in dataframe population, which is 6,4%. So it is not representative and we can start analysis part.   

# ---
# Analysis
# ---
# ---
# Step 1:
# --
# Firtsly we would like to understand top selling cities. As we see from table below there are almost 150 cities.
# It is impossible to cover all of them. In order to classify the most material ones we would like to build boxplot and it will help us to see median and interquartile range 

# In[78]:


#Create table that count number of cars per city

cars_per_city=myParsedDF_U.pivot_table(index='city',values='title',aggfunc='count').reset_index().sort_values('title',ascending=False)
cars_per_city.info()
cars_per_city.head(10)


# In[81]:


import seaborn as sns
import matplotlib.pyplot as plt

cars_per_city['title'].describe()


# In[82]:


cars_per_city['share']=cars_per_city['title']/cars_per_city['title'].sum()
cars_per_city['share']=cars_per_city['share'].round(2)

top_ten_cities_sales_share=cars_per_city.head(10)
top_ten_cities_sales_share


# In[83]:



top_ten_cities_sales_share_sum=top_ten_cities_sales_share['share'].sum().round(2)
top_ten_cities_sales_share_sum


# ### ---
# Conclusion on Step 1:
# ---
# Kyiv is the capital of the country and its leading in number of cars sold, but it takes only 23%.
# Top 10 cities are selling 60% of all cars
# min, 25% quartile and median  are the same, it means that there is a great number of cities where one car is sold, so the offer is geographically spread.   
# 75% of cities are selling 4 cars and below.
# Standard deviation(which is square root from dispersion) is 27, which is a significant number if to compare with total number.
# The conclusion is that sales mainly consist of a great number of cilites with small sales offers(75% have 4 offers or less).

# 
# Step2
# --
# We would also like to see how old the cars to be sold are and the number of them.
# 

# In[84]:


#Create table that count number of cars per year and share in totla population.

cars_per_year=myParsedDF_U.pivot_table(index='Car year',values='title',aggfunc='count').reset_index().sort_values('title',ascending=False)
cars_per_year['share']=cars_per_year['title']/cars_per_year['title'].sum()
cars_per_year['share']=cars_per_year['share'].round(2)
cars_per_year.info()
cars_per_year.head(10)


# In[85]:


# as the number of years is not as great as cities- we can visualize number of sales per year
plt.figure(figsize=(17,8))
sns.barplot(x='Car year',y='title',data=cars_per_year)
plt.xlabel("Year of production")
plt.ylabel("Number of offers")
plt.title("Offers per year of production")


# In[86]:


sns.boxplot(myParsedDF_U['Car year'])
plt.title("Percentage analysis")


# Step 2 conclusion:
# --
# Conclusion is the following:
# All the offers of cars produced before 2004 year are immaterial.
# 25% of offers are beteween 2004 and 2011.
# Most popular offers(median) relate to 2015 and 2016.
# 75% of offers are beteween 2004 and 2016.
# 

# Step 3:
# --
# We would like to see popularity of Jeep models offered

# In[87]:


cars_per_model=myParsedDF_U.pivot_table(index='title',values='Car year',aggfunc='count').reset_index().sort_values('Car year',ascending=False)
cars_per_model['share']=cars_per_model['Car year']/cars_per_model['Car year'].sum()
cars_per_model['share']=cars_per_model['share'].round(2)
cars_per_model=cars_per_model.rename(columns={'Car year':'Number'})

cars_per_model.info()
cars_per_model.head(10)


# In[88]:


cars_per_model['Number'].describe()


# Partial conclusion on Step 3: 
# --
# There are 247 models on the list. The most popular model is Jeep Grand Cherokee, it represents maximum offers. 
# 75% of the models are represented by 1 item. There are 3 models above oe equal to 10%, the rest of offers are widely spread.   
# 
# We cannot analyse all the cars For that purpose we would like to apply 2 most important criteria: price and milaege(indirectly stands for quality). 
# On the basis of this analysis we will decrease population of models and make further analysis.

# 
# Scatterplot shows popularity in:
# 
# range beteween 13kUSD and 16kUSD(both inclusively)
# 
# and mileage is between 50k and 140k kilometers

# In[89]:


import numpy as np
x = myParsedDF_U['USD']
y = myParsedDF_U['mileage']


plt.figure(figsize=(17,10))
plt.scatter(x, y,alpha=0.9)
plt.xlabel('Price USD')
plt.ylabel('mileage (thousands km) ')

plt.title('Most popular prices per year')


# In[90]:


sel_crit=myParsedDF_U.query('(mileage>=50) & (mileage<=140) &(USD>=13000)&(USD<=16000)')
sel_crit.info()
len_sel_crit=len(sel_crit['title'].unique())
len_sel_crit


# In[91]:


cars_per_model=sel_crit.pivot_table(index='title',values='Car year',aggfunc='count').reset_index().sort_values('Car year',ascending=False)
cars_per_model['share']=cars_per_model['Car year']/cars_per_model['Car year'].sum()
cars_per_model['share']=cars_per_model['share'].round(2)
cars_per_model=cars_per_model.rename(columns={'Car year':'Number'})

cars_per_model.head(10)


# In[92]:


# as the number of years is not as great as cities- we can visualize number of sales per year
plt.figure(figsize=(17,8))
sns.barplot(x='title',y='Number',data=cars_per_model)
plt.xlabel("Car model")
plt.xticks(rotation=90)
plt.ylabel("Number of offers")
plt.title("Offers per model")


# One more interesting characteristic is engine type. Let's investigate.

# In[94]:




cars_per_year = myParsedDF_U.pivot_table(index='Eng_type',values='title',aggfunc='count').reset_index().sort_values('title',ascending=False)
cars_per_year['share']=cars_per_year['title']/cars_per_year['title'].sum()
cars_per_year['share']=cars_per_year['share'].round(2)
cars_per_year.info()
cars_per_year.head(10)


# Most popular engine is petrol, then diesel and hybrid(gas-petrol). Gas are represented by 1 car only.
# 

# In[95]:


cars_per_year = myParsedDF_U.pivot_table(index='Volume_L',values='title',aggfunc='count').reset_index().sort_values('title',ascending=False)
cars_per_year['share']=cars_per_year['title']/cars_per_year['title'].sum()
cars_per_year['share']=cars_per_year['share'].round(2)
cars_per_year.info()
cars_per_year.head()


# 2.4 l engine takes almost half of the market, the rest are not so significant

# Conclusion: 
# ---
# Year of production: most popular cars offered relate to 2015 and 2016
# 
# Car models: Jeep charokee and Jeep compass
# Prices: most popular prices range between range 13kUSD and 16kUSD(both inclusively)
# 
# Mileage: mileage is between 50k and 140k kilometers.
# 
# Engines: petrol engines take over half of the market, 
# 
# Engine volume: 2.4 litres engines take almost half of the market
# 

# In[ ]:




