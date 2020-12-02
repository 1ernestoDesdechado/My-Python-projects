#!/usr/bin/env python
# coding: utf-8

# Purpose of the exersice:
# ---
# To extract from 2 independent sources price lists for playgrounds and compare them by using apprpriate statistical method.
# 
# 

# In[19]:


import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats as st


#Extract data from website 1
#Extract data and find out last page
URL = 'https://papa-joy.ru/catalog/detskie-gorki/'
r = requests.get(URL)
soup = BeautifulSoup(r.text,'html.parser')

pgsNum=soup.find_all('div',class_='pagination')
pgStr = pgsNum[-1].get_text(strip=True)
pgStr=pgStr.replace("Ctrl"," ")
pgStr=re.findall(r'\d',pgStr)
pgStr=int(pgStr[-1])

print(pgStr)


# In[20]:


myPlList=[]
# At this step we parse all necessary data from website 1

#if last page is not fully filled in we need to add 1 to pgStr(page counting variable) 
for page in range(1,pgStr+1):
    URL_SCR=f'https://papa-joy.ru/catalog/detskie-gorki/?PAGEN_1={page}'
    rUpd = requests.get(URL_SCR)
    soup = BeautifulSoup(rUpd.text,'html.parser')
    items = soup.find_all('div',class_='catalog-item-info')
    print(f'Process on page {page}')
    print(URL_SCR)
    
    
    for item in items:
        
        myPlList.append({
            'name': item.find('a',class_='item-title').get_text(strip=True),
            'price': item.find('div',class_='item-price').get_text(strip=True),
            'at_stock': item.find('div',class_='day-incoming').get_text(strip=True)
            
    })
    
print(f'Done,{len(myPlList)} items identified')


# In[21]:


#We convert the data to dataframe1
plGrParsed=pd.DataFrame(myPlList)
plGrParsed.info()
plGrParsed.head()


# In[22]:


# We convert the dataframe 1 to appropriate format
plGrParsed_u=plGrParsed.copy()
plGrParsed_u['price']=plGrParsed_u['price'].str.lower()
plGrParsed_u['price']=plGrParsed_u['price'].str.replace('руб.за шт','').str.replace(' ','').str.replace('от','')
plGrParsed_u['price']=plGrParsed_u['price'].str.replace('руб.экономия+[0-9]+руб.+[0-9]','')
plGrParsed_u['price']=plGrParsed_u['price'].astype(int)
plGrParsed_u.info()
plGrParsed_u.head()


# In[30]:


sns.boxplot(plGrParsed_u['price'])
plt.title("Price distribution")


# Date from website 1 is ready for comparison.
# We see that median is closer to 40kRUR,75% is 90kRUR. 
# Now we need to extract data from website 2 and transform it.  

# In[31]:


URL='https://kupiploshadku.ru/detskie-ploshchadki/'

r=requests.get(URL)
soup=BeautifulSoup(r.text,'lxml')
pgSearch=soup.find_all('div',class_='lazyloading-paging')

iCount=2
for ul in pgSearch:
    for li in ul:
        iCount+=1
myPlGr=[]

for iterVar in range(1,iCount):
    print(iterVar)
    URL_UPD = f'https://kupiploshadku.ru/detskie-ploshchadki/?page={iterVar}'
    rUpd = requests.get(URL_UPD)
    soup = BeautifulSoup(rUpd.text,'html.parser')
    items=soup.find_all('div',class_='product')
    print(URL_UPD)
    for item in items:
        myPlGr.append({
            'name': item.find('span',itemprop ='name').get_text(),
            #'price': item.find('span', class_="price nowrap").get_text()
            
            'at_stock':item.find('div', class_="stock yes").get_text(),
            'price':item.find('div', class_="prices").get_text(strip=True)          
     
    })
print(f'Done,{len(myPlGr)} items extracted')
#print(myPlGr)


# In[32]:


import numpy as np
myPlGr_DF2=pd.DataFrame(myPlGr)

myPlGr_DF2['price_upd'] = myPlGr_DF2['price'].str.lower().str.replace('р','').str.replace(' ','')
myPlGr_DF2['price_upd']=myPlGr_DF2['price_upd'].astype(np.int64)


myPlGr_DF2.head()


# In[33]:


#In order to see spread of prices lets build a boxplot
sns.boxplot(myPlGr_DF2['price_upd'])
plt.title("Percentage analysis")


# As we see there is one point that out of the range. There is one item that shows 2 prices in one(in column "price" national currency is mentioned twice for this item). Probably it contains old and new price. We will delete this item, as it is less then 5%(confidence interval) 

# In[34]:


myPlGr_DF2=myPlGr_DF2.sort_values(by='price_upd',ascending=False)  
myPlGr_DF2


# In[35]:


# we remove incorrect item
myPlGr_DF2=myPlGr_DF2.query('price_upd<119000139000')
sns.boxplot(myPlGr_DF2['price_upd'])
plt.title("Percentage analysis")


# Selection of approach and comparison
# ----
# The data is ready for comparison. We would like to select mann-whitney Utest  following
# 1) We took data from independent sources, they are not interdependent
# 2) Number of items is different in both samples
# 3) Boxplots show that data is not normally distributed
# 
# Zero hypothesis: both lists have identical median values

# In[42]:



from scipy import stats as st

df1List=plGrParsed_u['price'].tolist()
df2List=myPlGr_DF2['price_upd'].tolist()


# In[47]:


alpha = .05 # critical level of error

results = st.mannwhitneyu(df1List, df2List)

print('p-value: ', results.pvalue)

if (results.pvalue < alpha):
    print("Reject zero hypothesis")
else:
    print("Zero hypothesis is not rejected")


# In[ ]:





# In[ ]:





# In[ ]:




