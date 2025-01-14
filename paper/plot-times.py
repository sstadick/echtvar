import sys
import os
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
import pandas as pd

matplotlib.rc('font', size=13)
plt.rcParams['figure.constrained_layout.use'] = True
sns.set_style('white')

files = sys.argv[1:]

def parse_time(f):

    d = {'tool': os.path.basename(f).split('-')[0]}

    for line in open(f):
        if 'Elapsed' in line:
            d['wall time orig'] = line.split('):')[1].strip().split(':')
            wt = 0.0
            for i, v in enumerate(reversed(d['wall time orig'])):
               wt += max(1, 60 * i) * float(v)
            d['Wall time (seconds)'] = wt
            d.pop('wall time orig')

        if 'Maximum resident' in line:
            d['Memory (MB)'] = int(line.split('):')[1].strip()) / 1000.0
        if 'User time' in line:
            d['User time (seconds)'] = float(line.split('):')[1].strip())
        if line.startswith('#SIZE:'):
            d['File size (GB)'] = float(line.split()[1]) / 1000.0
    return d

import numpy as np

# https://stackoverflow.com/a/51535326
def show_values_on_bars(axs):
    def _show_on_single_plot(ax):        
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height()
            value = '{:.1f}'.format(p.get_height())
            ax.text(_x, _y, value, ha="center") 

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)


tools = [parse_time(f) for f in files]
df = pd.DataFrame.from_records(tools)

df = pd.melt(df, id_vars=('tool',),
    value_vars=('Wall time (seconds)', 'User time (seconds)', 'Memory (MB)', 'File size (GB)'), value_name=('value'))

df.to_csv('exome.plots.tsv', index=False, sep="\t")

fig, axes = plt.subplots(2, 2, figsize=(6, 6), constrained_layout=True)

# dropped wall time
for ii, var in enumerate(('Wall time (seconds)', 'User time (seconds)', 'Memory (MB)', 'File size (GB)')):

    i, j = [(0, 0), (0, 1), (1, 0), (1, 1)][ii]

    sub = df.loc[df.variable == var, :]
    subplot = sns.barplot(data=sub, x='tool', y='value', ax=axes[i, j])
    axes[i, j].set_ylabel(var)
    axes[i, j].set_xlabel(None)
    #show_values_on_bars(subplot)
    axes[i, j].bar_label(subplot.containers[0], fmt='%.1f')
    axes[i, j].set_ylim(ymax=1.07*axes[i, j].get_ylim()[1])

    if i == 1:
      lbls = axes[i, j].get_xticklabels()
      axes[i, j].set_xticklabels(lbls, rotation=15, ha='right')
    else:
      axes[i, j].set_xticklabels([], rotation=15, ha='right')


# set times to same y-axis
ym = max(axes[0, 1].get_ylim()[1], axes[0, 0].get_ylim()[1])
axes[0, 1].set_ylim(ymax=ym)
axes[0, 0].set_ylim(ymax=ym)


plt.tight_layout()
plt.savefig('echtvar-comparison.png', format='png', dpi=1200)
plt.savefig('echtvar-comparison.eps', format='eps', dpi=1200)
plt.show()
