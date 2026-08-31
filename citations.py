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

# The citations panel starts here. Everything earlier is folded into the
# curve's starting point instead of being drawn year by year: the two sources
# reach back to different years, Google Scholar stops breaking the counts out
# per year before 2014, and between them those years are 3% of the total.
PLOT_FROM = 2016

# The last year for which the Google Scholar column holds a lumped total
# rather than that year alone. PLOT_FROM has to be past it.
GOOGLE_LUMPED_THROUGH = 2013

# Citations accrued per year. The Months column is how much of each year the
# counts cover, which is 12 except for the year still in progress.
citation_data = pd.read_csv('citations.csv', comment='#')

years = citation_data['Year'].values
months_counted = citation_data['Months'].values
last_year = years[-1]
months_done = months_counted[-1]

if not (np.diff(years) == 1).all():
    raise ValueError('citations.csv skips a year')
if not (months_counted[:-1] == 12).all():
    raise ValueError('only the final year in citations.csv may be partial')
if not 1 <= months_done <= 12:
    raise ValueError(f'Months for {last_year} is {months_done}, not 1-12')
if PLOT_FROM <= GOOGLE_LUMPED_THROUGH:
    raise ValueError(f'PLOT_FROM={PLOT_FROM} would draw the Google Scholar '
                     f'total for {GOOGLE_LUMPED_THROUGH} and earlier as a '
                     f'single year')

earlier = citation_data[citation_data.Year < PLOT_FROM]
plotted = citation_data[citation_data.Year >= PLOT_FROM]
if plotted.isna().any().any():
    raise ValueError(f'citations.csv has gaps at or after {PLOT_FROM}')

# The curve opens at PLOT_FROM already carrying everything that came before,
# so it stays a true cumulative total rather than restarting from zero.
year_ends = np.concatenate(([float(PLOT_FROM)], plotted.Year + 1.0))
year_ends[-1] = last_year + months_done/12

cumulative_gscholar = np.concatenate(
        ([earlier.Google.sum()], earlier.Google.sum() + plotted.Google.cumsum()))
cumulative_wos = np.concatenate(
        ([earlier.WoS.sum()], earlier.WoS.sum() + plotted.WoS.cumsum()))

h_index_data = pd.read_table('h-index.csv', sep=',')
h_index_data.columns = ['Year', 'Mon', 'Google', 'WoS']
h_index_data['Year_frac'] = h_index_data.apply(
        lambda x: x.Year + (months[x.Mon] - 0.5)/12, axis=1)

# The h-index is a step function: keep only the first survey at each value, so
# the plot jumps when the index actually changed instead of interpolating
# through values that never held.
h_google = h_index_data.drop_duplicates(subset='Google')
h_wos = h_index_data.dropna(subset=['WoS']).drop_duplicates(subset='WoS')

# The panels no longer span the same years: the citations series is folded
# back to PLOT_FROM while the h-index keeps its whole history. They share a
# right edge, which leaves room for the endpoint labels on both.
X_RIGHT = last_year + 1.9
h_first_year = int(h_index_data.Year.min())


def style_x_axis(ax, from_year):
    ticks = np.arange(from_year, last_year + 1, 2)
    ax.set_xlim(from_year - 0.4, X_RIGHT)
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(y) for y in ticks])
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

style_x_axis(cit_ax, PLOT_FROM)
cit_ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
cit_ax.set_ylabel('Citations (cumulative)')
cit_ax.text(0.985, 0.03,
            f'includes citations before {PLOT_FROM}\n'
            f'final year through {month_names[months_done]} {last_year}',
            transform=cit_ax.transAxes,
            ha='right', va='bottom', fontsize=5.5, color=MUTED,
            linespacing=1.4)

# The cumulative curve is flat for its first decade, which leaves room for the
# per-year counts the cumulative view hides. Google Scholar only: the inset is
# there to show the rate, not to compare the two sources.
rate_ax = cit_ax.inset_axes([0.10, 0.52, 0.42, 0.44])
rate_ax.bar(plotted.Year, plotted.Google, width=0.7, color=GOOGLE, lw=0, zorder=3)
this_year = plotted.Google.iloc[-1]
projected = this_year * 12/months_done
rate_ax.bar(last_year, projected - this_year, width=0.7, bottom=this_year,
            color='none', edgecolor=GOOGLE, lw=0.5, linestyle=(0, (1.2, 1.2)),
            zorder=3)
rate_ax.set_xlim(PLOT_FROM - 0.8, last_year + 0.8)
rate_ax.set_ylim(0, projected*1.14)
rate_ax.set_yticks([0, 4000])
rate_ax.set_yticklabels(['0', '4k'], fontsize=5.5)
rate_ax.set_xticks([PLOT_FROM, last_year])
rate_ax.set_xticklabels([str(PLOT_FROM), str(last_year)], fontsize=5.5)
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

style_x_axis(h_ax, h_first_year)
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

print(f'Citations: {cumulative_gscholar[-1]:,.0f} (Google Scholar); '
      f'{cumulative_wos[-1]:,.0f} (Web of Science)')
print(f'h-index: {h_google.Google.iloc[-1]:.0f} (Google Scholar); '
      f'{h_wos.WoS.iloc[-1]:.0f} (Web of Science)')
