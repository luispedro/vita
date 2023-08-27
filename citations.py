import numpy as np
from matplotlib import style
style.use('default')
#%matplotlib qt


import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['axes.labelsize'] = 'small'

years = np.array([
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    ])

gscholar_citations = np.array([
      43,
      49,
      54,
     114,
     246,
     494,
     609,
     905,
    1454,
    2117,
    2816,
    3116,
    2023,
    ])

# Annualize
gscholar_citations[-1] *= 12/8

wos_citations_dict = {
    2011:22,
    2012:23,
    2013:28,
    2014:53,
    2015:148,
    2016:291,
    2017:365,
    2018:554,
    2019:987,
    2020:1393,
    2021:1949,
    2022:2136,
    2023:1199,
    }

wos_citations = np.array([wos_citations_dict[y] for y in years])
wos_citations[-1] *= 12/8

years = years.astype(float)

h_index_data = pd.read_table('h-index.csv', sep=',')
h_index_data.columns = ['Year', 'Mon', 'Google', 'WoS']

months = {
 'Jan': 1,
 'Feb': 2,
 'Mar': 3,
 'Apr': 4,
 'May': 5,
 'Jun': 6,
 'Jul': 7,
 'Aug': 8,
 'Sep': 9,
 'Oct': 10,
 'Nov': 11,
 'Dec': 12,
 }

h_index_data['Time'] = h_index_data.apply(lambda x: datetime.datetime(year=x.Year, month=months[x.Mon], day=1), axis=1)
h_index_data['Year_frac'] = h_index_data['Time'].dt.year + h_index_data['Time'].dt.month/12.

fig,(cit_ax, h_ax) = plt.subplots(1, 2, sharex=False, figsize=(6.5,1.8))

cit_ax.clear()
h_ax.clear()

h_ax.plot(h_index_data['Year_frac'], h_index_data['Google'], '-', ms=2, c='#1b9e77', label='Google')
h_ax.plot(h_index_data['Year_frac'], h_index_data['WoS'], '-', ms=2, c='#7570b3', label='Web of Science')

cit_ax.plot(years, np.cumsum(gscholar_citations), '-o', ms=4, c='#1b9e77', label='Google Scholar')
cit_ax.plot(years, np.cumsum(wos_citations), '-o', ms=4, c='#7570b3', label='Web of Science')

#X_TICKS = np.concatenate((years[::2],[2023]))
X_TICKS = years[::2]
for ax in (cit_ax, h_ax):
    ax.set_xticks(X_TICKS)
    ax.set_xticklabels([str(int(x)) for x in X_TICKS])
    ax.set_xlabel('Year')
    ax.grid(True)



cit_ax.legend(loc='best')
cit_ax.set_xlabel("Year")
cit_ax.set_ylabel("Number of citations\n(cumulative)")
cit_ax.set_xlim(2011.5, 2023.5)

h_ax.set_ylabel("h-index")
#h_ax.set_xlabel("Year (2022 is incomplete)")
h_ax.set_xlabel("Year")
h_ax.set_xlim(2012.5, 2023.5)

sns.despine(fig, trim=True)
fig.tight_layout()
fig.show()
fig.savefig('citations-h-index.pdf')
fig.savefig('2022-xx-xx__citations.svg')
fig.savefig('2022-xx-xx__citations.pdf')
fig.savefig('2022-xx-xx__citations.png', dpi=300)
