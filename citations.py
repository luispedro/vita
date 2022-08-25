import numpy as np
from matplotlib import style
style.use('default')
#%matplotlib qt


import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns

plt.rcParams['svg.fonttype'] = 'none'

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
    ])

gscholar_citations = np.array([
      42,
      45,
      56,
     119,
     247,
     484,
     601,
     885,
    1416,
    2056,
    2782,
    2097,
    ])

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
    2021:1930,
    2022:1198,
    }

wos_citations = np.array([wos_citations_dict[y] for y in years])

years = years.astype(float)
years[-1] = 2021. + 8/12.

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

fig,axes = plt.subplots(1,2,sharex=True)
cit_ax, h_ax = axes


cit_ax.clear()
h_ax.clear()

h_ax.plot(h_index_data['Year_frac'], h_index_data['WoS'], '-o', ms=4, c='#7570b3', label='Web of Science')
h_ax.plot(h_index_data['Year_frac'], h_index_data['Google'], '-o', ms=4, c='#1b9e77', label='Google')

cit_ax.plot(years + .5, np.cumsum(wos_citations), '-o', ms=4, c='#7570b3', label='Web of Science')
cit_ax.plot(years + .5, np.cumsum(gscholar_citations), '-o', ms=4, c='#1b9e77', label='Google Scholar')

h_ax.set_xticks(years[::2])
h_ax.set_xticklabels([(str(int(y)) if y != 2022 else "2022*") for y in years[::2]])
cit_ax.legend(loc='best')
cit_ax.set_xlabel("Year\n(Note: 2022 is incomplete)")
cit_ax.set_ylabel("Number of citations\n(cumulative)")

h_ax.set_ylabel("h-index")
h_ax.set_xlabel("Year\n(Note: 2022 is incomplete)")

sns.despine(fig, trim=True)
fig.tight_layout()
fig.savefig('2022-xx-xx__citations.svg')
fig.savefig('2022-xx-xx__citations.pdf')
fig.savefig('2022-xx-xx__citations.png', dpi=300)
