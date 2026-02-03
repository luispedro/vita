import numpy as np
from matplotlib import style
import matplotlib.ticker as ticker
style.use('default')


import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['axes.labelsize'] = 'small'

years = np.arange(2011, 2026)

gscholar_citations = np.array([
      43,
      50,
      61,
     123,
     260,
     536,
     628,
     935,
    1488,
    2209,
    2929,
    3285,
    3201,
    3510,
    4291,
    ])

wos_citations = [
      19, # 2011
      21,
      24,
      52,
     124,
     242,
     307,
     496,
     917,
    1312,
    1927,
    2168,
    2052,
    2347,
    2748,
    ]

wos_citations = np.array(wos_citations)

# Annualize

years = years.astype(float)
years_partial = years.copy()


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

h_ax.plot('Year_frac', 'Google', data=h_index_data.drop_duplicates(subset='Google'), linestyle='-', ms=2, c='#1b9e77', label='Google')
h_ax.plot('Year_frac', 'WoS', data=h_index_data.drop_duplicates(subset='WoS'), linestyle='-', ms=2, c='#7570b3', label='Web of Science')

cit_ax.plot(years_partial, np.cumsum(gscholar_citations), '-o', ms=4, c='#1b9e77', label='Google Scholar')
cit_ax.plot(years_partial, np.cumsum(wos_citations), '-o', ms=4, c='#7570b3', label='Web of Science')

#X_TICKS = np.concatenate((years[::2],[2023]))
X_TICKS = years[1::2]
for ax in (cit_ax, h_ax):
    ax.set_xticks(X_TICKS)
    ax.set_xticklabels([str(int(x)) for x in X_TICKS])
    ax.set_xlabel('Year')
    ax.grid(True)


cit_ax.legend(loc='best')
cit_ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

cit_ax.set_xlabel("Year")
cit_ax.set_ylabel("Number of citations\n(cumulative)")
cit_ax.set_xlim(2011.5, 2026.0)
cit_ax.set_ylim(0, 24_000)

h_ax.set_ylabel("h-index")
#h_ax.set_xlabel("Year (2022 is incomplete)")
h_ax.set_xlabel("Year")
h_ax.set_xlim(2012.5, 2026.0)
h_ax.set_ylim(0, 54)

sns.despine(fig, trim=True)
fig.tight_layout()
fig.show()
fig.savefig('citations-h-index.pdf')
