import logging
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encoder import NQueensEncoder

sys.stdout.reconfigure(encoding='utf-8')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

RUNTIME_FILES = ['sat_vs_cp_benchmark.csv', 'benchmark_large_N.csv',
                 'benchmark_large_N_50.csv', 'benchmark_extra_large_N.csv']
SIZES = [8, 10, 15, 20, 25, 30, 40, 50, 100, 200]

ENC_STYLE = {
    'Binomial':   dict(color='#2a78d6', marker='o', ls='-'),
    'Sequential': dict(color='#eb6834', marker='s', ls='--'),
    'Binary':     dict(color='#1baf7a', marker='D', ls='-.'),
    'Commander':  dict(color='#eda100', marker='^', ls=':'),
    'Product':    dict(color='#e87ba4', marker='v', ls=(0, (5, 1.5, 1, 1.5, 1, 1.5))),
}
SOLVER_STYLE = {
    'CP-SAT':     dict(color='#2a78d6', marker='o', ls='-'),
    'CPLEX-CP':   dict(color='#eb6834', marker='s', ls='--'),
    'CPLEX-MIP':  dict(color='#1baf7a', marker='D', ls='-.'),
    'Gurobi-MIP': dict(color='#eda100', marker='^', ls=':'),
}
INK, INK_2, GRID = '#0b0b0b', '#52514e', '#e4e3df'

plt.rcParams.update({
    'font.size': 10, 'axes.edgecolor': INK_2, 'axes.labelcolor': INK, 'xtick.color': INK_2,
    'ytick.color': INK_2, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
    'figure.facecolor': 'white', 'axes.facecolor': 'white', 'legend.frameon': False,
})


def _style_axes(ax, xticks=None):
    ax.grid(True, which='major', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    if xticks is not None:
        ax.set_xscale('log')
        ax.xaxis.set_major_locator(FixedLocator(xticks))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xticklabels([str(x) for x in xticks])


def load_runtime():
    frames = []
    for name in RUNTIME_FILES:
        path = os.path.join(RESULTS_DIR, name)
        if os.path.exists(path):
            frames.append(pd.read_csv(path))
    df = pd.concat(frames, ignore_index=True)
    df['Error'] = df['Error'].fillna('').astype(str)
    df['Is_SAT'] = df['Is_SAT'].astype(str).str.lower() == 'true'
    df['Algorithm'] = df['Algorithm'].replace({'Gurobi-mip': 'Gurobi-MIP', 'gurobi-mip': 'Gurobi-MIP'})
    return df.drop_duplicates(subset=['Board_Size', 'Algorithm'], keep='last')


def plot_runtime(df):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    panels = [(axes[0], ENC_STYLE, 'SAT encodings (Glucose3, original variable order)'),
              (axes[1], SOLVER_STYLE, 'CP and MIP solvers')]
    for ax, styles, title in panels:
        xmax = 2
        timeouts = df[df['Algorithm'].isin(styles) & (df['Error'].str.upper() == 'TIMEOUT')]
        for alg, st in styles.items():
            sub = df[df['Algorithm'] == alg].sort_values('Board_Size')
            ok = sub[(sub['Error'] == '') & sub['Is_SAT']]
            if not ok.empty:
                y = ok['Solve_Time(s)']
                yerr = [y - ok['Solve_Min(s)'], ok['Solve_Max(s)'] - y]
                ax.errorbar(ok['Board_Size'], y, yerr=yerr, color=st['color'], ls=st['ls'],
                            marker=st['marker'], ms=6, lw=2, capsize=2.5, elinewidth=1,
                            label=alg, zorder=3)
                xmax = max(xmax, ok['Board_Size'].max())
        for n, grp in timeouts.groupby('Board_Size'):
            order = [a for a in styles if a in set(grp['Algorithm'])]
            for j, alg in enumerate(order):
                st = styles[alg]
                row = grp[grp['Algorithm'] == alg].iloc[0]
                shift = 1 + 0.045 * (j - (len(order) - 1) / 2)
                ax.scatter([n * shift], [row['Solve_Time(s)']], marker=st['marker'], s=55,
                           facecolors='white', edgecolors=st['color'], linewidths=1.8, zorder=4)
            xmax = max(xmax, n)
        ticks = [n for n in SIZES if n <= xmax]
        _style_axes(ax, ticks)
        ax.set_yscale('log')
        ax.set_title(title, loc='left', color=INK)
        ax.set_xlabel('Board size N (log scale)')
    axes[0].set_ylabel('Solve time (s, log scale)')

    for ax, styles in ((axes[0], ENC_STYLE), (axes[1], SOLVER_STYLE)):
        handles, labels = ax.get_legend_handles_labels()
        handles.append(Line2D([], [], ls='', marker='o', mfc='white', mec=INK_2, mew=1.6, ms=7))
        labels.append('timed out (true time ≥ limit)')
        ax.legend(handles, labels, loc='upper left', fontsize=8.5)
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, 'chart_runtime_comparison.png')
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_clauses():
    sizes = [n for n in SIZES if n <= 100]
    counts = {enc: [len(NQueensEncoder(n).generate_clauses(enc.lower())[0]) for n in sizes]
              for enc in ENC_STYLE}
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for enc, st in ENC_STYLE.items():
        ax.plot(sizes, counts[enc], color=st['color'], ls=st['ls'], marker=st['marker'],
                ms=6, lw=2, label=enc, zorder=3)
    _style_axes(ax, sizes)
    ax.set_yscale('log')
    ax.set_xlabel('Board size N (log scale)')
    ax.set_ylabel('Number of clauses (log scale)')
    ax.set_title('CNF size per encoding (exact counts)', loc='left', color=INK)
    last = {enc: counts[enc][-1] for enc in ENC_STYLE}
    labels = [('Binomial', last['Binomial']), ('Binary', last['Binary']),
              ('Commander', last['Commander']),
              ('Product ≈ Sequential', (last['Product'] * last['Sequential']) ** 0.5)]
    nudge = {'Binary': 1.12, 'Commander': 0.88}
    for text, y in labels:
        ax.annotate(text, (sizes[-1], y * nudge.get(text, 1.0)), xytext=(6, 0),
                    textcoords='offset points', va='center', fontsize=8.5, color=INK)
    ax.set_xlim(sizes[0] * 0.92, sizes[-1] * 1.9)
    ax.legend(loc='upper left', fontsize=8.5)
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, 'chart_clauses_comparison.png')
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_ordering():
    path = os.path.join(RESULTS_DIR, 'robustness_shuffle.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    sizes = sorted(df['Board_Size'].unique())
    fig, axes = plt.subplots(1, len(sizes), figsize=(3.7 * len(sizes), 4.4), sharey=True, squeeze=False)
    encs = list(ENC_STYLE)
    for ax, n in zip(axes[0], sizes):
        sub = df[df['Board_Size'] == n]
        for i, enc in enumerate(encs):
            st = ENC_STYLE[enc]
            e = sub[sub['Encoding'] == enc].sort_values('Seed')
            if e.empty:
                continue
            done = e[e['Status'] == 'SAT']
            to = e[(e['Status'] == 'TIMEOUT') & (e['Seed'] != 0)]
            shuf = done[done['Seed'] != 0]
            jitter = [(j % 5 - 2) * 0.07 for j in range(len(shuf))]
            ax.scatter([i + d for d in jitter], shuf['Solve_Time(s)'], s=22, color=st['color'],
                       alpha=0.85, edgecolors='white', linewidths=0.6, zorder=3)
            if not to.empty:
                ax.scatter([i + 0.25] * len(to), to['Solve_Time(s)'], s=40, marker='^',
                           facecolors='white', edgecolors=st['color'], linewidths=1.6, zorder=4)
                ax.annotate(f'{len(to)}×', (i + 0.25, to['Solve_Time(s)'].iloc[0]), xytext=(5, 4),
                            textcoords='offset points', fontsize=7.5, color=INK_2)
            times = e['Solve_Time(s)'].where(e['Status'] == 'SAT', float('inf'))
            med = times.median()
            if med != float('inf'):
                ax.hlines(med, i - 0.3, i + 0.3, color=INK, lw=1.6, zorder=5)
            orig = e[e['Seed'] == 0].iloc[0]
            ax.scatter([i - 0.25], [orig['Solve_Time(s)']], marker='X', s=70, color=INK,
                       facecolors=INK if orig['Status'] == 'SAT' else 'white', zorder=6)
        ax.set_xticks(range(len(encs)))
        ax.set_xticklabels(encs, rotation=35, ha='right')
        ax.set_yscale('log')
        _style_axes(ax)
        ax.grid(False, axis='x')
        ax.set_title(f'N = {n}', loc='left', color=INK)
    axes[0][0].set_ylabel('Solve time (s, log scale)')
    handles = [Line2D([], [], ls='', marker='X', color=INK, ms=8, label='original order (seed 0; hollow = timed out)'),
               Line2D([], [], ls='', marker='o', color=INK_2, ms=5, label='permuted CNF (seeds 1–9)'),
               Line2D([], [], color=INK, lw=1.6, label='median of all 10 runs'),
               Line2D([], [], ls='', marker='^', mfc='white', mec=INK_2, mew=1.5, ms=7,
                      label='permuted runs timed out (≥ 60 s), with count')]
    fig.legend(handles=handles, loc='upper center', ncol=4, fontsize=8.5, bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, 'chart_ordering_sensitivity.png')
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def main():
    for out in (plot_runtime(load_runtime()), plot_clauses(), plot_ordering()):
        if out:
            print('=> ' + out)


if __name__ == '__main__':
    main()
