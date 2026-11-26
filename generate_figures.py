import os
os.environ['MPLCONFIGDIR'] = r'c:\Users\ASUS\Desktop\minor project\results\.matplotlib'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

# Fig 2.2.2 Dense Block
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.axis('off')
layers = ['Input x0', 'Layer 1 (H1)', 'Layer 2 (H2)', 'Layer 3 (H3)', 'Output']
xs = [0.1, 0.3, 0.5, 0.7, 0.9]
cols = ['#e2e8f0', '#fed7aa', '#fde68a', '#bbf7d0', '#bfdbfe']
for x, name, c in zip(xs, layers, cols):
    r = plt.Rectangle((x-0.08, 0.35), 0.16, 0.3, facecolor=c, edgecolor='#334155', lw=1.5, transform=ax.transAxes)
    ax.add_patch(r)
    ax.text(x, 0.5, name, ha='center', va='center', fontsize=8, fontweight='bold', transform=ax.transAxes)
for i in range(len(xs)-1):
    ax.annotate('', xy=(xs[i+1]-0.08, 0.5), xytext=(xs[i]+0.08, 0.5), arrowprops=dict(facecolor='black', width=1, headwidth=5), transform=ax.transAxes)
# Dense skip arcs
arcs = [(0, 2, 0.75), (0, 3, 0.85), (1, 3, 0.72)]
for start, end, y_arc in arcs:
    ax.plot([xs[start], xs[start], xs[end], xs[end]], [0.65, y_arc, y_arc, 0.65], 'r--', lw=1.2, transform=ax.transAxes)
    ax.annotate('', xy=(xs[end], 0.65), xytext=(xs[end], y_arc), arrowprops=dict(facecolor='red', edgecolor='red', width=0.8, headwidth=4), transform=ax.transAxes)
ax.text(0.5, 0.92, 'Iterative Feature Concatenation (xl = Hl([x0, x1, ..., x{l-1}]))', ha='center', va='center', fontsize=9, fontweight='bold', transform=ax.transAxes)
plt.tight_layout()
fig.savefig(r'c:\Users\ASUS\Desktop\minor project\results\fig_2_2_2_dense_block.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# Fig 2.2.3 EfficientNet compound scaling
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.axis('off')
ax.text(0.5, 0.88, 'EfficientNet: Compound Scaling Paradigm', ha='center', va='center', fontsize=11, fontweight='bold', transform=ax.transAxes)
dims = [
    ('Depth Scaling', 'd = alpha^phi\n(# Layers)', 0.2, '#fed7aa'),
    ('Width Scaling', 'w = beta^phi\n(# Channels)', 0.5, '#bae6fd'),
    ('Resolution', 'r = gamma^phi\n(Input Res)', 0.8, '#bbf7d0')
]
for title, eq, x, col in dims:
    r = plt.Rectangle((x-0.12, 0.35), 0.24, 0.38, facecolor=col, edgecolor='#334155', lw=1.5, transform=ax.transAxes)
    ax.add_patch(r)
    ax.text(x, 0.58, title, ha='center', va='center', fontsize=9, fontweight='bold', transform=ax.transAxes)
    ax.text(x, 0.44, eq, ha='center', va='center', fontsize=8, transform=ax.transAxes)
ax.text(0.5, 0.15, 'Constraint: alpha * beta^2 * gamma^2 ≈ 2, with Compound Coefficient phi', ha='center', va='center', fontsize=9, fontstyle='italic', transform=ax.transAxes)
plt.tight_layout()
fig.savefig(r'c:\Users\ASUS\Desktop\minor project\results\fig_2_2_3_efficientnet.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# Fig 2.3.1 Vision / Biosignal Transformer
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.axis('off')
ax.text(0.5, 0.92, 'Biosignal / Time-Series Transformer Encoder Architecture', ha='center', va='center', fontsize=10, fontweight='bold', transform=ax.transAxes)
tf_boxes = [
    ('Multi-Channel Biosignal Window (ECG, EDA, EMG, Blink)', 0.5, 0.80, 0.8, 0.08, '#f1f5f9'),
    ('Linear Projection to Latent Dimension d=64 + Positional Encoding', 0.5, 0.65, 0.8, 0.08, '#bae6fd'),
    ('Multi-Head Self-Attention (4 Heads) + LayerNorm', 0.5, 0.50, 0.7, 0.08, '#fde68a'),
    ('Feed-Forward MLP (dim 128) + Dropout (0.3) + LayerNorm', 0.5, 0.35, 0.7, 0.08, '#fed7aa'),
    ('Global Temporal Pooling + Classification Head (3 Classes)', 0.5, 0.20, 0.7, 0.08, '#bbf7d0')
]
for title, x, y, w, h, col in tf_boxes:
    r = plt.Rectangle((x-w/2, y-h/2), w, h, facecolor=col, edgecolor='#334155', lw=1.5, transform=ax.transAxes)
    ax.add_patch(r)
    ax.text(x, y, title, ha='center', va='center', fontsize=8, fontweight='bold', transform=ax.transAxes)
for i in range(len(tf_boxes)-1):
    y_from = tf_boxes[i][2] - tf_boxes[i][4]/2
    y_to = tf_boxes[i+1][2] + tf_boxes[i+1][4]/2
    ax.annotate('', xy=(0.5, y_to), xytext=(0.5, y_from), arrowprops=dict(facecolor='black', width=1, headwidth=5), transform=ax.transAxes)
plt.tight_layout()
fig.savefig(r'c:\Users\ASUS\Desktop\minor project\results\fig_2_3_1_transformer.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# Fig 4.3.1 Combined Confusion Matrix (All models)
with open(r'c:\Users\ASUS\Desktop\minor project\results\all_results.json') as f:
    res = json.load(f)
fig, axes = plt.subplots(2, 3, figsize=(13, 8))
axes = axes.flatten()
names = ['XGBoost', 'Random Forest', '1D-CNN', 'Transformer', 'Quantum Hybrid']
class_labels = ['Low', 'Med', 'High']
for idx, name in enumerate(names):
    ax = axes[idx]
    cm = np.array(res[name]['confusion_matrix'])
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    acc_val = res[name]['accuracy'] * 100
    ax.set_title(f"{name} (Acc: {acc_val:.1f}%)", fontsize=10, fontweight='bold')
    tick_marks = np.arange(len(class_labels))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(class_labels, fontsize=9)
    ax.set_yticklabels(class_labels, fontsize=9)
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'), ha='center', va='center', color='white' if cm[i, j] > thresh else 'black', fontsize=10)
    ax.set_ylabel('True Label', fontsize=9)
    ax.set_xlabel('Predicted Label', fontsize=9)
axes[5].axis('off')
axes[5].text(0.05, 0.75, "Evaluation Cohort Summary:\n• Unseen Test Subjects (N=9, 772 windows)\n• Low Fatigue: Rest baseline\n• Medium Fatigue: Cognitive / Physical\n• High Fatigue: Combined Fatigue\n• Strict Subject-Wise Evaluation", fontsize=9.5, transform=axes[5].transAxes, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8fafc', edgecolor='#cbd5e1'))
plt.tight_layout()
fig.savefig(r'c:\Users\ASUS\Desktop\minor project\results\fig_4_3_1_confusion_matrices.png', dpi=200, bbox_inches='tight')
plt.close(fig)
print('All figures created successfully.')

