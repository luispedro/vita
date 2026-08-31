#!/usr/bin/env python3
'''Generate talks-summary.tex from the (private) talks.yaml.

talks.yaml is deliberately *not* tracked in git: only the aggregate numbers in
talks-summary.tex are made public. Run this after editing talks.yaml:

    python make-talks-summary.py                     # default style
    python make-talks-summary.py --style prose       # try another rendering
    python make-talks-summary.py --preview           # compare all styles in one PDF
'''

import argparse
import collections
import datetime
import re
import subprocess
import sys

import yaml

# kind (as used in talks.yaml) -> row of the summary table
GROUPS = [
    ('invited',     'Keynotes \\&\\ invited conference talks',
        ['keynote', 'invited-talk', 'invited-talk-remote']),
    ('seminar',     'Institutional seminars',
        ['institutional-seminar', 'institutional-seminar-remote']),
    ('contributed', 'Contributed conference talks',
        ['from-abstract', 'from-abstract-remote']),
    ('lecture',     'Lectures, webinars \\&\\ outreach',
        ['summer-school-lecture', 'webinar', 'public-engagement']),
]

# counted and described separately, not talks in the usual sense
NON_TALK_KINDS = ['panel', 'convenor']

KIND_TO_GROUP = {k: g for g, _, kinds in GROUPS for k in kinds}

COLORS = {'invited': '1b9e77', 'seminar': '7570b3',
          'contributed': 'd95f02', 'lecture': '999999'}

SWATCH_DEFS = ''.join(
    f'\\providecolor{{talks-{g}}}{{HTML}}{{{c}}}\n' for g, c in COLORS.items()
) + ('\\providecommand\\swatch[1]{\\textcolor{#1}{\\rule[.08em]{.55em}{.55em}}}\n\n')

COUNTRY_ALIASES = {
    'United States': 'USA',
    'UK': 'United Kingdom',
}

NOT_A_COUNTRY = re.compile(r'^(online|remote|.*cohort)$', re.I)


def year_of(talk):
    return int(str(talk['date'])[:4])


def is_remote(talk):
    return ('remote' in talk['kind']
            or talk['kind'] == 'webinar'
            or '(remote)' in (talk.get('location') or ''))


def country_of(talk):
    '''Country the talk was given in/to, or None when there is no meaningful one.'''
    location = (talk.get('location') or '').strip()
    if not location or NOT_A_COUNTRY.match(location):
        return None
    country = re.sub(r'\s*\(remote\)\s*$', '', location.split(',')[-1].strip())
    if NOT_A_COUNTRY.match(country):
        return None
    return COUNTRY_ALIASES.get(country, country)


def load(path):
    with open(path) as f:
        talks = yaml.safe_load(f)
    unknown = {t['kind'] for t in talks} - set(KIND_TO_GROUP) - set(NON_TALK_KINDS)
    if unknown:
        raise SystemExit(f'{path}: unknown kind(s): {sorted(unknown)}')
    # a missing location silently shrinks the published country count, so say so
    for t in talks:
        if country_of(t) is None:
            sys.stderr.write(f'{path}: no country for {t["venue"]!r} '
                             f'({t["date"]}); not counted towards countries\n')
    return talks


def summarize(talks, since):
    all_talks = [t for t in talks if t['kind'] not in NON_TALK_KINDS]
    recent = [t for t in all_talks if year_of(t) >= since]

    rows = []
    for group, label, kinds in GROUPS:
        in_group = [t for t in all_talks if KIND_TO_GROUP[t['kind']] == group]
        rows.append((label,
                     len(in_group),
                     sum(1 for t in in_group if year_of(t) >= since)))

    countries = {country_of(t) for t in all_talks} - {None}
    countries_recent = {country_of(t) for t in recent} - {None}
    countries_in_person = {country_of(t) for t in all_talks if not is_remote(t)} - {None}

    return {
        'rows': rows,
        'total': len(all_talks),
        'total_recent': len(recent),
        'since': since,
        'countries': len(countries),
        'countries_recent': len(countries_recent),
        'countries_in_person': len(countries_in_person),
        'keynotes': sum(1 for t in all_talks if t['kind'] == 'keynote'),
        'remote': sum(1 for t in all_talks if is_remote(t)),
        'invited': next(n for label, n, _ in rows if label.startswith('Keynotes')),
        'panels': sum(1 for t in talks if t['kind'] == 'panel'),
        'convening': [t for t in talks if t['kind'] in NON_TALK_KINDS],
        'per_year': collections.Counter(year_of(t) for t in all_talks),
        'per_year_group': {
            group: collections.Counter(year_of(t) for t in all_talks
                                       if KIND_TO_GROUP[t['kind']] == group)
            for group, _, _ in GROUPS},
    }


# ---------------------------------------------------------------- renderings

def style_table(s):
    '''The established rendering: a two-column table plus a geography sentence.'''
    width = max(len(label) for label, _, _ in s['rows'])
    body = table_body(s, width)
    return f'''\\noindent{{\\CvItem
\\begin{{tabular}}{{lrr}}
\\textbf{{Category}} & \\textbf{{Total}} & \\textbf{{Since {s['since']}}}\\\\[.2em]
\\hline\\\\[-.8em]
{body}\\hline\\\\[-.8em]
{'\\textbf{Total}':<{width}} & \\textbf{{{s['total']}}} & \\textbf{{{s['total_recent']}}}\\\\
\\end{{tabular}}}}

\\vspace{{.6em}}
\\noindent{{\\CvItem {geography(s)}}}
'''


def style_prose(s):
    '''No table: three lines of dense prose. The most compact option.'''
    parts = ', '.join(f'{n} {label_lc(label)}' for label, n, _ in s['rows'][:-1])
    last = s['rows'][-1]
    return f'''\\noindent{{\\CvItem
\\textbf{{{s['total']} invited and contributed talks}} ({s['total_recent']} since {s['since']}):
{parts}, and {last[1]} {label_lc(last[0])}. {geography(s)}}}
'''


def style_keyfigures(s):
    """A strip of headline numbers over one prose line; no table."""
    figures = [
        (s['total'], 'talks'),
        (s['invited'], 'invited \\&\\ keynote'),
        (s['countries'], 'countries'),
        (s['total_recent'], f'since {s["since"]}'),
    ]
    strip = '\\hfill'.join(
        f'\\begin{{minipage}}[t]{{.23\\linewidth}}\\centering'
        f'{{\\subhead\\textcolor{{darkg}}{{{n}}}}}\\\\[.15em]'
        f'{{\\CvItem\\textcolor{{medg}}{{{caption}}}}}\\end{{minipage}}%\n'
        for n, caption in figures)
    breakdown = ', '.join(f'{n} {label_lc(label)}' for label, n, _ in s['rows'])
    return f'''\\noindent
{strip}
\\vspace{{1em}}

\\noindent{{\\CvItem {breakdown}. {geography(s)}}}
'''


def style_figure(s, gap='12pt'):
    """Table side by side with a stacked bar chart of talks per year.

    The colour swatches in the table double as the chart's legend.

    The table is boxed at its natural width and the chart takes whatever is
    left over, so `gap` is the real gutter between the two rather than
    whatever a pair of guessed percentage widths happens to leave.
    """
    return SWATCH_DEFS + f'''\\newsavebox{{\\talkstable}}
\\newlength{{\\talksgap}}
\\setlength{{\\talksgap}}{{{gap}}}
\\savebox{{\\talkstable}}{{%
{style_table_only(s)}}}

\\noindent\\begin{{minipage}}[c]{{\\wd\\talkstable}}
\\usebox{{\\talkstable}}
\\end{{minipage}}%
\\hspace{{\\talksgap}}%
\\begin{{minipage}}[c]{{\\dimexpr\\linewidth-\\wd\\talkstable-\\talksgap\\relax}}
\\includegraphics[width=\\linewidth]{{talks-by-year.pdf}}
\\end{{minipage}}

\\vspace{{.6em}}
\\noindent{{\\CvItem {geography(s)}}}
'''


def style_table_only(s):
    width = max(len(label) for label, _, _ in s['rows'])
    body = table_body(s, width, swatches=True)
    return f'''{{\\CvItem
\\begin{{tabular}}{{@{{}}lrr}}
\\textbf{{Category}} & \\textbf{{Total}} & \\textbf{{Since {s['since']}}}\\\\[.2em]
\\hline\\\\[-.8em]
{body}\\hline\\\\[-.8em]
{'\\textbf{Total}':<{width}} & \\textbf{{{s['total']}}} & \\textbf{{{s['total_recent']}}}\\\\
\\end{{tabular}}}}
'''


def table_body(s, width, swatches=False):
    lines = []
    for (label, total, recent), (group, _, _) in zip(s['rows'], GROUPS):
        cell = f'\\swatch{{talks-{group}}} {label}' if swatches else label
        lines.append(f'{cell:<{width}} & {total:3d} & {recent:3d}\\\\\n')
    return ''.join(lines)[:-1] + '[.2em]\n'


def label_lc(label):
    '''Lowercase a table label for use mid-sentence.'''
    return label[0].lower() + label[1:]


def geography(s):
    return (f'Talks delivered in {s["countries"]} countries '
            f'({s["countries_recent"]} since {s["since"]}), '
            f'including {s["keynotes"]} conference keynotes. '
            + convening(s))


def convening(s):
    '''"Additionally: session convenor and panellist ..." — derived from talks.yaml.'''
    entries = s['convening']
    if not entries:
        return ''
    roles = []
    if any(t['kind'] == 'convenor' for t in entries):
        roles.append('session convenor')
    if s['panels']:
        roles.append(f'panellist ({s["panels"]} panels)')
    # every such entry so far is at one meeting; name it when that holds
    meetings = {(t['venue'].split(' \u2013 ')[0], t['location'], year_of(t))
                for t in entries}
    if len(meetings) == 1:
        venue, location, year = meetings.pop()
        where = f' at {venue} ({location}), {year}'
    else:
        where = ''
    return f'Additionally: {" and ".join(roles)}{where}.'


STYLES = {
    'table': style_table,
    'prose': style_prose,
    'keyfigures': style_keyfigures,
    'figure': style_figure,
}

HEADER = ('% Generated by make-talks-summary.py from talks.yaml '
          '(style: {style}). Do not edit by hand.\n')


# -------------------------------------------------------------------- figure

def write_figure(s, path='talks-by-year.pdf'):
    from matplotlib import pyplot as plt
    from matplotlib import style as mplstyle
    mplstyle.use('default')
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['xtick.labelsize'] = 7
    plt.rcParams['ytick.labelsize'] = 7
    plt.rcParams['axes.labelsize'] = 'small'

    colors = {g: '#' + c for g, c in COLORS.items()}
    years = list(range(min(s['per_year']), max(s['per_year']) + 1))
    fig, ax = plt.subplots(figsize=(3.2, 1.5))
    bottom = [0] * len(years)
    for group, label, _ in GROUPS:
        counts = [s['per_year_group'][group][y] for y in years]
        ax.bar(years, counts, bottom=bottom, color=colors[group],
               label=label.replace('\\&\\', '&'), width=.75)
        bottom = [b + c for b, c in zip(bottom, counts)]
    ax.set_ylabel('Talks per year')
    ax.set_xticks([y for y in years if y % 4 == 0])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout(pad=.2)
    fig.savefig(path)
    return path


# ------------------------------------------------------------------- preview

PREVIEW = r'''\documentclass[a4paper]{article}
\usepackage[margin=2cm]{geometry}
\input{preamble.tex}
\pagestyle{empty}
\begin{document}
\parindent=0cm
CONTENT
\end{document}
'''


def build_preview(s, out='talks-preview.pdf'):
    '''Render every style into one PDF, in the CV's own fonts, for comparison.'''
    import os
    import shutil
    import tempfile
    preamble = extract_preamble('vita.tex')
    blocks = []
    for name, fn in STYLES.items():
        blocks.append(f'\\section{{Style: {name}}}\n\n' + fn(s)
                      + '\n\\vspace{2em}\n')
    tmp = tempfile.mkdtemp(prefix='talks-preview-')
    with open(os.path.join(tmp, 'preamble.tex'), 'w') as f:
        f.write(preamble)
    with open(os.path.join(tmp, 'talks-preview.tex'), 'w') as f:
        f.write(PREVIEW.replace('CONTENT', '\n'.join(blocks)))
    for extra in ('fonts', 'talks-by-year.pdf'):
        if os.path.isdir(extra):
            shutil.copytree(extra, os.path.join(tmp, extra))
        elif os.path.exists(extra):
            shutil.copy(extra, tmp)
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', 'talks-preview.tex'],
                       cwd=tmp, capture_output=True, text=True)
    built = os.path.join(tmp, 'talks-preview.pdf')
    if not os.path.exists(built):
        sys.stderr.write(r.stdout[-3000:])
        raise SystemExit('xelatex failed to build the preview')
    shutil.copy(built, out)
    return out


def extract_preamble(path):
    '''Everything in vita.tex before \\begin{document}, minus the page style.'''
    with open(path) as f:
        text = f.read()
    preamble = text.split('\\begin{document}')[0]
    return preamble.replace('\\pagestyle{cv}', '')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--input', default='talks.yaml')
    p.add_argument('--output', default='talks-summary.tex')
    p.add_argument('--style', default='table', choices=sorted(STYLES))
    p.add_argument('--since', type=int, default=2022,
                   help='anchor year for the "recent" column (default: 2022)')
    p.add_argument('--figure-gap', default='12pt',
                   help='gutter between table and chart in --style figure '
                        '(any TeX length; default: 12pt)')
    p.add_argument('--figure', action='store_true',
                   help='also write talks-by-year.pdf (implied by --style figure)')
    p.add_argument('--preview', action='store_true',
                   help='build talks-preview.pdf comparing all styles')
    p.add_argument('--stats', action='store_true',
                   help='print the underlying numbers and exit')
    args = p.parse_args(argv)

    s = summarize(load(args.input), args.since)

    if args.stats:
        for label, total, recent in s['rows']:
            print(f'{label.replace(chr(92) + "&" + chr(92), "&"):<40} {total:4d} {recent:4d}')
        for key in ('total', 'total_recent', 'countries', 'countries_recent',
                    'countries_in_person', 'keynotes', 'remote', 'panels'):
            print(f'{key:<40} {s[key]:4d}')
        print('per year:', dict(sorted(s['per_year'].items())))
        return

    if args.figure or args.style == 'figure':
        print('wrote', write_figure(s))

    if args.preview:
        if not args.figure and args.style != 'figure':
            write_figure(s)
        print('wrote', build_preview(s))
        return

    render = STYLES[args.style]
    with open(args.output, 'w') as f:
        f.write(HEADER.format(style=args.style))
        f.write(render(s, args.figure_gap) if args.style == 'figure' else render(s))
    print(f'wrote {args.output} ({s["total"]} talks, {s["total_recent"]} since {args.since})')


if __name__ == '__main__':
    main()
