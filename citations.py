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
month_names = {n: name for name, n in months.items()}

# Citations accrued per year. The Months column is how much of each year the
# counts cover, which is 12 except for the year still in progress.
citation_data = pd.read_csv('citations.csv', comment='#')

years = citation_data['Year'].values
gscholar_citations = citation_data['Google'].values
wos_citations = citation_data['WoS'].values
months_counted = citation_data['Months'].values

first_year = years[0]
last_year = years[-1]
months_done = months_counted[-1]

if not (np.diff(years) == 1).all():
    raise ValueError('citations.csv skips a year')
if not (months_counted[:-1] == 12).all():
    raise ValueError('only the final year in citations.csv may be partial')
if not 1 <= months_done <= 12:
    raise ValueError(f'Months for {last_year} is {months_done}, not 1-12')

# Each yearly total is plotted at the end of the window it covers, so the
# partial final year sits where its data actually stops.
year_ends = years + 1.0
year_ends[-1] = last_year + months_done/12

cumulative_gscholar = np.cumsum(gscholar_citations)
cumulative_wos = np.cumsum(wos_citations)

h_index_data = pd.read_table('h-index.csv', sep=',')
h_index_data.columns = ['Year', 'Mon', 'Google', 'WoS']
h_index_data['Year_frac'] = h_index_data.apply(
        lambda x: x.Year + (months[x.Mon] - 0.5)/12, axis=1)

# The h-index is a step function: keep only the first survey at each value, so
# the plot jumps when the index actually changed instead of interpolating
# through values that never held.
h_google = h_index_data.drop_duplicates(subset='Google')
h_wos = h_index_data.dropna(subset=['WoS']).drop_duplicates(subset='WoS')

X_LIM = (first_year + 0.6, last_year + 1.9)
X_TICKS = np.arange(first_year + 1, last_year + 1, 2)


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
            f'final year through {month_names[months_done]} {last_year}',
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
rate_ax.set_xlim(first_year - 0.8, last_year + 0.8)
rate_ax.set_ylim(0, projected*1.14)
rate_ax.set_yticks([0, 4000])
rate_ax.set_yticklabels(['0', '4k'], fontsize=5.5)
rate_ax.set_xticks([first_year + 1, last_year])
rate_ax.set_xticklabels([str(first_year + 1), str(last_year)], fontsize=5.5)
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

sns.despine(fig, ax=cit_ax)
sns.despine(fig, ax=h_ax)
fig.tight_layout(pad=0.35, w_pad=1.2, rect=(0, 0, 1, 0.90))

# One legend for both panels, spanning them above rather than sitting inside
# either one. Both axes label their lines; take the handles from one of them so
# the entries are not repeated.
fig.legend(*cit_ax.get_legend_handles_labels(),
           loc='upper center', bbox_to_anchor=(0.5, 1.005), ncol=2,
           frameon=False, fontsize=7, handlelength=1.4,
           columnspacing=1.6, handletextpad=0.5)
fig.savefig('citations-h-index.pdf')

print(f'Citations: {cumulative_gscholar[-1]:,} (Google Scholar); '
      f'{cumulative_wos[-1]:,} (Web of Science)')
print(f'h-index: {h_google.Google.iloc[-1]:.0f} (Google Scholar); '
      f'{h_wos.WoS.iloc[-1]:.0f} (Web of Science)')
