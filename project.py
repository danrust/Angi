import pandas as pd
import math
from datetime import datetime
from pandas.tseries.offsets import MonthEnd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import json
from pandas.io.json import json_normalize

"""

1. Opportunity size - what does repeat rate look like today, and what might it grow to?
    A: 34.1%
    B: ?
2. Is there a relationship between service type and repeat bookings?
    A: lawnmowing and yardwork help have extremely high repeat rates
3. Is there a relationship between service quality and repeat bookings?
    A: It would appear so, but it could be the type of service rather than the rating itself



"""

"""

Today, customers don’t come back as often as we believe they should, given how many home
services they do every year. Building repeat relationships with our customers is the most
important goal for 2022.

Your goal as product leader is to double the average number of bookings per customer.

Other things to consider

● The average homeowner completes an average of 12 home maintenance jobs / year
● The most searched for "help" item on the site is "Who will show up to do the job?"
● From research, we’ve learned that customers who book with us frequently value the
ease and convenience of booking online and the fact that we “do the homework” to find
the right service professional for them
● Our average revenue is $250/job, lawn care and cleaning revenue is $100/job

"""

df = pd.read_excel('/Users/danielrust/Downloads/Booking_Sample_Data_Product_Practical_v2.xlsx')

#making sure there's no duplicate users/data doesn't need to be wrangled further at user level
df['EXTERNAL_USER_ID'].nunique()

#1925 user ids to 1925 rows, informing how to slice data further
df['repeat'] = df['SECOND_BOOKING_EXTERNAL_ID'].apply(lambda x:0 if pd.isnull(x) else 1)
repeat_rate = df['repeat'].mean()


#defining revenue
#lawn care, home cleaning is $100 in revenue
#all other jobs $250 in revenue
""" 

defining lawn care and home cleaning, we will assume
things like `shrub trimming` and `tree removal` are landscaping
and not lawn care. 

Lawn care will strictly be `lawnmowing trimming`
"""



def first_service_revenue(row):
    if row['FIRST_BOOKING_SERVICE_NAME'] == 'lawnmowing_trimming':
        return 100
    elif row['FIRST_BOOKING_SERVICE_NAME'] == 'home_cleaning':
        return 100
    else:
        return 250

def second_service_revenue(row):
    if row['SECOND_BOOKING_SERVICE_NAME'] == 'lawnmowing_trimming':
        return 100
    elif row['SECOND_BOOKING_SERVICE_NAME'] == 'home_cleaning':
        return 100
    elif row['repeat'] == 0:
        return 0
    else:
        return 250
        
df['first_booking_service_revenue'] = df.apply(lambda row: first_service_revenue(row),axis=1)
df['second_booking_service_revenue'] = df.apply(lambda row: second_service_revenue(row),axis=1)

#rating and repeat rate by service
df['FIRST_BOOKING_RATING'].fillna(value=0,inplace=True)
rbs = df.groupby('FIRST_BOOKING_SERVICE_NAME',as_index=False).agg({'FIRST_BOOKING_RATING':['mean','count'], 'repeat':'mean'})
rbs.columns = ['FIRST_BOOKING_RATING', 'avg_rating', 'count', 'repeat_rate']

#repeat rate by service
by_service = df.groupby('FIRST_BOOKING_SERVICE_NAME',as_index=False).agg({'repeat':['mean','count']})
by_service.columns = ['FIRST_BOOKING_SERVICE_NAME', 'repeat_rate', 'count']

#repeat rate by rating
df['FIRST_BOOKING_RATING'].fillna(value=0,inplace=True)
by_rating = df.groupby('FIRST_BOOKING_RATING',as_index=False).agg({'repeat':['mean','count']})
by_rating.columns = ['FIRST_BOOKING_RATING', 'repeat_rate', 'count']



repeat_bookings = df.loc[df['second_booking_service_revenue'] > 0]
repeat_bookings[['FIRST_BOOKING_CREATE_DATE', 'SECOND_BOOKING_CREATE_DATE']] = repeat_bookings[['FIRST_BOOKING_CREATE_DATE', 'SECOND_BOOKING_CREATE_DATE']].apply(pd.to_datetime, errors='coerce')
repeat_bookings['time_between_bookings'] = (repeat_bookings['SECOND_BOOKING_CREATE_DATE'] - repeat_bookings['FIRST_BOOKING_CREATE_DATE']).dt.days
repeat_bookings['time_between_bookings'].median()



#plotting for data viz
plt.style.use('fivethirtyeight')
fix, ax = plt.subplots(figsize = (12, 8))

#group df for plot
by_service['type'] = by_service['FIRST_BOOKING_SERVICE_NAME'].apply(lambda x: 1 if (x == 'yardwork_help' or x == 'lawnmowing_trimming') else 0)
ax = sns.scatterplot(x = 'repeat_rate', y = 'count', size = 'count', data = by_service, sizes = (10, 1000), hue='type', legend=False)
plt.draw()
ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
ax.set(xlabel='repeat rate', ylabel='number of first bookings')
ax.set_ylim(0, 500)

plt.text(x = -0.25
       , y = ax.get_ylim()[1]* 1.2
       , fontsize = 26
       , weight = "bold"
       , alpha = 0.75
       , s = "Lawn maintenance sees most repetition")
plt.text(x = -0.25
       , y = ax.get_ylim()[1]* 1.1
       , fontsize = 20
       , alpha = 0.85
       , s = "Booking volume by repeat reate, lawn care in shown in red")
