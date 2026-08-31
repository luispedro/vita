import datetime

import numpy as np
import pandas as pd
from matplotlib import style
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

style.use('default')

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.edgecolor'] = '#888888'
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['xtick.color'] = '#666666'
plt.rcParams['ytick.color'] = '#666666'
plt.rcParams['xtick.major.size'] = 2.5
plt.rcParams['ytick.major.size'] = 2.5
plt.rcParams['xtick.major.width'] = 0.6
plt.rcParams['ytick.major.width'] = 0.6
plt.rcParams['grid.color'] = '#dddddd'
plt.rcParams['grid.linewidth'] = 0.6

GOOGLE = '#1b9e77'
WOS = '#7570b3'
MUTED = '#666666'

# The figure is placed full-width on page 2 of the CV, which is exactly full:
# 2.24in is the tallest that still fits, and at 2.26in "Language skills" is
# pushed onto its own page and the CV grows from 12 to 13 pages. Do not
# enlarge without rebuilding vita.pdf.
FIG_SIZE = (6.5, 2.2)

# The final year is partial. This is the date the counts below were collected;
# it drives both the position of the last point and the note on the figure.
# Update it whenever the counts are updated.
DATA_THROUGH = datetime.date(2026, 8, 31)

FIRST_YEAR = 2011

# Citations accrued in each year, starting at FIRST_YEAR.
gscholar_citations = np.array([
      43,
      50,
      61,
     126,
     266,
     532,
     634,
     931,
    1510,
    2210,
    2945,
    3313,
    3271,
    3544,
    4278,
    3285,
    ])

wos_citations = np.array([
     #  1, # 2007
     #  0, # 2008
     #  3, # 2009
     #  4, # 2010
      19, # 2011
      21,
      24,
      52,
     124,
     242,
     307,
     495,
     915,
    1309,
    1927,
    2164,
    2047,
    2355,
    2878,
    2012,
    ])

years = np.arange(FIRST_YEAR, FIRST_YEAR + len(gscholar_citations))
last_year = years[-1]
months_done = DATA_THROUGH.month

if len(wos_citations) != len(gscholar_citations):
    raise ValueError('Google Scholar and Web of Science series have different lengths')
if last_year != DATA_THROUGH.year:
    raise ValueError(f'DATA_THROUGH is {DATA_THROUGH.year}, but the counts end in {last_year}')

# Each yearly total is plotted at the end of the window it covers, so the
# partial final year sits where its data actually stops.
year_ends = years + 1.0
year_ends[-1] = last_year + months_done/12

cumulative_gscholar = np.cumsum(gscholar_citations)
cumulative_wos = np.cumsum(wos_citations)

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

h_index_data = pd.read_table('h-index.csv', sep=',')
h_index_data.columns = ['Year', 'Mon', 'Google', 'WoS']
h_index_data['Year_frac'] = h_index_data.apply(
        lambda x: x.Year + (months[x.Mon] - 0.5)/12, axis=1)

# The h-index is a step function: keep only the first survey at each value, so
# the plot jumps when the index actually changed instead of interpolating
# through values that never held.
h_google = h_index_data.drop_duplicates(subset='Google')
h_wos = h_index_data.dropna(subset=['WoS']).drop_duplicates(subset='WoS')

X_LIM = (FIRST_YEAR + 0.6, last_year + 1.9)
X_TICKS = np.arange(FIRST_YEAR + 1, last_year + 1, 2)


def style_x_axis(ax):
    ax.set_xlim(*X_LIM)
    ax.set_xticks(X_TICKS)
    ax.set_xticklabels([str(y) for y in X_TICKS])
    ax.grid(True, axis='y')
    ax.set_axisbelow(True)
    ax.set_ylim(0, None)


def label_end(ax, x, y, color, dy):
    '''Mark the last point of a series and print its value beside it.'''
    ax.plot(x, y, 'o', ms=3.5, c=color, mec='white', mew=0.8, zorder=4)
    ax.annotate(f'{y:,.0f}', (x, y),
                textcoords='offset points', xytext=(4, dy),
                fontsize=7, color=color, va='center', fontweight='bold')


fig, (cit_ax, h_ax) = plt.subplots(1, 2, figsize=FIG_SIZE)

cit_ax.plot(year_ends, cumulative_gscholar, '-', lw=1.6, c=GOOGLE,
            label='Google Scholar', zorder=3)
cit_ax.plot(year_ends, cumulative_wos, '-', lw=1.6, c=WOS,
            label='Web of Science', zorder=3)
label_end(cit_ax, year_ends[-1], cumulative_gscholar[-1], GOOGLE, 1)
label_end(cit_ax, year_ends[-1], cumulative_wos[-1], WOS, -1)

style_x_axis(cit_ax)
cit_ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
cit_ax.set_ylabel('Citations (cumulative)')
cit_ax.text(0.985, 0.03,
            f'final year through {DATA_THROUGH:%b %Y}',
            transform=cit_ax.transAxes,
            ha='right', va='bottom', fontsize=5.5, color=MUTED)

# The cumulative curve is flat for its first decade, which leaves room for the
# per-year counts the cumulative view hides. Google Scholar only: the inset is
# there to show the rate, not to compare the two sources.
rate_ax = cit_ax.inset_axes([0.10, 0.52, 0.42, 0.44])
rate_ax.bar(years, gscholar_citations, width=0.7, color=GOOGLE, lw=0, zorder=3)
projected = gscholar_citations[-1] * 12/months_done
rate_ax.bar(last_year, projected - gscholar_citations[-1], width=0.7,
            bottom=gscholar_citations[-1], color='none', edgecolor=GOOGLE,
            lw=0.5, linestyle=(0, (1.2, 1.2)), zorder=3)
rate_ax.set_xlim(FIRST_YEAR - 0.8, last_year + 0.8)
rate_ax.set_ylim(0, projected*1.14)
rate_ax.set_yticks([0, 4000])
rate_ax.set_yticklabels(['0', '4k'], fontsize=5.5)
rate_ax.set_xticks([FIRST_YEAR + 1, last_year])
rate_ax.set_xticklabels([str(FIRST_YEAR + 1), str(last_year)], fontsize=5.5)
rate_ax.tick_params(length=1.5, width=0.5, pad=1)
rate_ax.set_title('per year (GS)', fontsize=6, color=MUTED, pad=1.5)
for spine in rate_ax.spines.values():
    spine.set_linewidth(0.5)
rate_ax.spines['top'].set_visible(False)
rate_ax.spines['right'].set_visible(False)

h_ax.plot('Year_frac', 'Google', data=h_google, drawstyle='steps-post', lw=1.6,
          c=GOOGLE, label='Google Scholar', zorder=3)
h_ax.plot('Year_frac', 'WoS', data=h_wos, drawstyle='steps-post', lw=1.6,
          c=WOS, label='Web of Science', zorder=3)
label_end(h_ax, h_google.Year_frac.iloc[-1], h_google.Google.iloc[-1], GOOGLE, 1)
label_end(h_ax, h_wos.Year_frac.iloc[-1], h_wos.WoS.iloc[-1], WOS, -1)

style_x_axis(h_ax)
h_ax.set_ylabel('h-index')

# One legend for both panels, inside the corner the h-index steps leave empty.
# borderaxespad keeps it clear of the y-axis instead of straddling it.
h_ax.legend(loc='upper left', frameon=False, fontsize=6.5, handlelength=1.2,
            handletextpad=0.45, borderpad=0.0, labelspacing=0.3,
            borderaxespad=0.6)

sns.despine(fig, ax=cit_ax)
sns.despine(fig, ax=h_ax)
fig.tight_layout(pad=0.35, w_pad=1.2)
fig.savefig('citations-h-index.pdf')

print(f'Citations: {cumulative_gscholar[-1]:,} (Google Scholar); '
      f'{cumulative_wos[-1]:,} (Web of Science)')
print(f'h-index: {h_google.Google.iloc[-1]:.0f} (Google Scholar); '
      f'{h_wos.WoS.iloc[-1]:.0f} (Web of Science)')
