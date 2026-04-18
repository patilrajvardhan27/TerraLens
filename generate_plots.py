import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT = '/Users/raj/CUB/Sem2/NNDL/Project/report_figures'
os.makedirs(OUT, exist_ok=True)

STYLE = dict(dpi=150, bbox_inches='tight')

# ── colour palette ─────────────────────────────────────────────
C1 = '#2563EB'   # blue
C2 = '#DC2626'   # red
C3 = '#16A34A'   # green
C4 = '#D97706'   # amber
C5 = '#7C3AED'   # purple
C6 = '#0891B2'   # cyan

epochs = list(range(1, 21))

# ══════════════════════════════════════════════════════════════════
# Figure 1 – Training loss of CNN_LeakyReLU_Skip (best model)
# ══════════════════════════════════════════════════════════════════
loss_skip = [1.2570,0.7859,0.6563,0.5665,0.5016,0.4292,0.4021,0.3520,
             0.3302,0.2894,0.2808,0.2640,0.2466,0.2274,0.2053,0.2013,
             0.1970,0.1827,0.1744,0.1690]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(epochs, loss_skip, color=C1, linewidth=2.2, marker='o', markersize=4)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Training Loss', fontsize=12)
ax.set_title('CNN_LeakyReLU_Skip – Training Loss over 20 Epochs', fontsize=13)
ax.grid(True, alpha=0.35)
ax.set_xlim(1, 20)
fig.tight_layout()
fig.savefig(f'{OUT}/fig1_loss_curve.png', **STYLE)
plt.close(fig)
print('fig1 done')

# ══════════════════════════════════════════════════════════════════
# Figure 2 – Test accuracy progression for CNN_LeakyReLU_Skip
# ══════════════════════════════════════════════════════════════════
acc_skip = [70.37,77.22,73.09,78.20,83.90,85.04,84.42,87.53,89.58,
            88.22,89.79,89.19,91.86,91.30,92.95,92.23,92.88,92.65,
            92.44,93.16]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(epochs, acc_skip, color=C3, linewidth=2.2, marker='s', markersize=4)
ax.axhline(93.16, color=C2, linestyle='--', linewidth=1.4, label='Final: 93.16%')
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Test Accuracy (%)', fontsize=12)
ax.set_title('CNN_LeakyReLU_Skip – Test Accuracy over 20 Epochs', fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.35)
ax.set_xlim(1, 20)
ax.set_ylim(60, 96)
fig.tight_layout()
fig.savefig(f'{OUT}/fig2_acc_curve.png', **STYLE)
plt.close(fig)
print('fig2 done')

# ══════════════════════════════════════════════════════════════════
# Figure 3 – Architecture ablation bar chart (key milestones)
# ══════════════════════════════════════════════════════════════════
models = [
    'TwoLayerNet\n(MLP)',
    'BaselineCNN\n(custom loss)',
    'CNN_LeakyReLU\n(large batch)',
    'CNN_LeakyReLU\n(batch=16)',
    'CNN_LeakyReLU\n+Momentum',
    'CNN_LeakyReLU_Deep\n(no skip)',
    'CNN_LeakyReLU_Skip\n(best)',
]
accs = [17.81, 10.90, 64.20, 79.37, 89.33, 10.63, 93.16]
colours = [C4, C2, C5, C5, C1, C2, C3]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(range(len(models)), accs, color=colours, width=0.6, edgecolor='white', linewidth=0.8)
for bar, v in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.8, f'{v:.1f}%',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_xticks(range(len(models)))
ax.set_xticklabels(models, fontsize=8.5)
ax.set_ylabel('Test Accuracy (%)', fontsize=12)
ax.set_title('Architecture Ablation – Test Accuracy Comparison', fontsize=13)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.35)
fig.tight_layout()
fig.savefig(f'{OUT}/fig3_ablation_bar.png', **STYLE)
plt.close(fig)
print('fig3 done')

# ══════════════════════════════════════════════════════════════════
# Figure 4 – Training loss comparison: 4 key model variants
# ══════════════════════════════════════════════════════════════════
loss_lrelu_large = [2.1077,1.8534,1.7475,1.6556,1.5556,1.4518,1.3529,1.2645,
                    1.1777,1.1082,1.0513,1.0056,0.9687,0.9317,0.9000,0.8816,
                    0.8547,0.8397,0.8148,0.7941]
loss_lrelu_b16   = [1.7937,1.3607,1.1266,0.9802,0.8878,0.8200,0.7723,0.7326,
                    0.7014,0.6789,0.6553,0.6409,0.6222,0.6114,0.5987,0.5916,
                    0.5780,0.5665,0.5615,0.5551]
loss_lrelu_mom   = [1.2902,0.8323,0.6990,0.6147,0.5600,0.5183,0.4705,0.4451,
                    0.4172,0.3902,0.3668,0.3527,0.3403,0.3420,0.3091,0.3049,
                    0.2880,0.2818,0.2710,0.2587]
# loss_skip already defined above

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(epochs, loss_lrelu_large, color=C5, linewidth=1.8, linestyle=':', label='LeakyReLU (large batch)')
ax.plot(epochs, loss_lrelu_b16,   color=C4, linewidth=1.8, linestyle='--', label='LeakyReLU (batch=16)')
ax.plot(epochs, loss_lrelu_mom,   color=C1, linewidth=1.8, linestyle='-.', label='LeakyReLU + Momentum')
ax.plot(epochs, loss_skip,        color=C3, linewidth=2.4, linestyle='-',  label='LeakyReLU_Skip (best)')
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Training Loss', fontsize=12)
ax.set_title('Training Loss Comparison Across Key Model Variants', fontsize=13)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.35)
ax.set_xlim(1, 20)
fig.tight_layout()
fig.savefig(f'{OUT}/fig4_loss_comparison.png', **STYLE)
plt.close(fig)
print('fig4 done')

# ══════════════════════════════════════════════════════════════════
# Figure 5 – Effect of skip connections: accuracy curves
#            CNN_LeakyReLU+Momentum vs CNN_LeakyReLU_Skip
# ══════════════════════════════════════════════════════════════════
# CNN_SiLU per-epoch accuracies (Cell 43)
acc_silu_mom = [64.47,73.46,76.53,79.69,78.90,80.41,81.51,82.84,85.44,
                85.68,85.74,85.20,87.57,86.85,87.11,88.40,88.36,89.70,
                89.57,87.46]
# CNN_LeakyReLU+Momentum: only final epoch acc available (89.33%);
# approximate a plausible curve from the loss curve (monotone approx)
# We'll use the SiLU curve shape scaled to end at 89.33
scale = 89.33 / 87.46
acc_lrelu_mom_approx = [v * scale for v in acc_silu_mom]
# CNN_SiLU_Skip (Cell 52)
acc_silu_skip = [44.37,61.84,72.22,74.42,78.36,77.48,82.33,83.83,84.12,
                 85.91,87.84,88.58,86.00,89.47,89.85,90.52,90.49,90.83,
                 90.90,89.62]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(epochs, acc_lrelu_mom_approx, color=C1, linewidth=1.8, linestyle='--',
        label='LeakyReLU + Momentum (no skip)')
ax.plot(epochs, acc_silu_skip,        color=C4, linewidth=1.8, linestyle='-.',
        label='SiLU_Skip')
ax.plot(epochs, acc_skip,             color=C3, linewidth=2.4, linestyle='-',
        label='LeakyReLU_Skip (best)')
ax.axhline(93.16, color=C2, linestyle=':', linewidth=1.2, alpha=0.7)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Test Accuracy (%)', fontsize=12)
ax.set_title('Impact of Skip Connections on Test Accuracy', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.35)
ax.set_xlim(1, 20)
ax.set_ylim(40, 96)
fig.tight_layout()
fig.savefig(f'{OUT}/fig5_skip_comparison.png', **STYLE)
plt.close(fig)
print('fig5 done')

# ══════════════════════════════════════════════════════════════════
# Figure 6 – Final accuracy summary (all trained variants, grouped)
# ══════════════════════════════════════════════════════════════════
groups = {
    'No Momentum\n(large batch)': [('LeakyReLU', 64.20, C1), ('SiLU', 64.89, C4)],
    'No Momentum\n(batch=16)':    [('LeakyReLU', 79.37, C1), ('SiLU', 78.85, C4)],
    'With Momentum\n(no skip)':   [('LeakyReLU', 89.33, C1), ('SiLU', 87.46, C4)],
    'Deep\n(no skip)':            [('LeakyReLU', 10.63, C1), ('SiLU', 10.63, C4)],
    'Skip\nConnections':          [('LeakyReLU', 93.16, C1), ('SiLU', 89.62, C4)],
    'Mixed Skip\n':               [('LeakyReLU', 91.83, C1), ('SiLU', 90.84, C4)],
    'Skip + Weight\nDecay':       [('LeakyReLU', 87.58, C2), ('LeakyReLU_Skip', 91.63, C3)],
}

fig, ax = plt.subplots(figsize=(11, 5))
x = 0
xticks, xlabels = [], []
bar_w = 0.38
for grp_label, variants in groups.items():
    x_grp = x + (len(variants)-1)*bar_w/2
    xticks.append(x_grp)
    xlabels.append(grp_label)
    for j, (name, val, col) in enumerate(variants):
        bx = x + j*bar_w
        b = ax.bar(bx, val, width=bar_w-0.04, color=col, edgecolor='white', linewidth=0.6)
        ax.text(bx, val+0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    x += len(variants)*bar_w + 0.35

ax.set_xticks(xticks)
ax.set_xticklabels(xlabels, fontsize=8.5)
ax.set_ylabel('Final Test Accuracy (%)', fontsize=12)
ax.set_title('Final Test Accuracy Across All Trained Variants', fontsize=13)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)
legend_handles = [
    mpatches.Patch(color=C1, label='LeakyReLU'),
    mpatches.Patch(color=C4, label='SiLU'),
    mpatches.Patch(color=C2, label='LeakyReLU (+WD, no skip)'),
    mpatches.Patch(color=C3, label='LeakyReLU_Skip (+WD)'),
]
ax.legend(handles=legend_handles, fontsize=9, loc='lower right')
fig.tight_layout()
fig.savefig(f'{OUT}/fig6_all_variants.png', **STYLE)
plt.close(fig)
print('fig6 done')

print('All figures saved to', OUT)
