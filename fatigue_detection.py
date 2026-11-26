#!/usr/bin/env python3
"""
fatigue_detection.py
====================
3-Class Fatigue Detection using MePhy Biosignal Dataset

Classes : Low (rest) | Medium (cognitive / physical fatigue) | High (combo fatigue)
Models  : Random Forest, XGBoost, 1D-CNN, Transformer, Quantum-Classical Hybrid
Signals : ECG, EDA, EMG, Eye Blinking

Authors : Abinash Boro, Satyam Prakash, Arnav Kumar
Institute: BIT Mesra, Ranchi
"""

import os, sys, json, time, math, warnings
os.environ['MPLCONFIGDIR'] = os.path.join(r"c:\Users\ASUS\Desktop\minor project\results", ".matplotlib")
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             confusion_matrix, classification_report)
from sklearn.decomposition import PCA
from sklearn.utils.class_weight import compute_class_weight

import xgboost as xgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings('ignore')
np.random.seed(42)
torch.manual_seed(42)

# ================================================================
# CONFIGURATION
# ================================================================
DATASET_ROOT = Path(r"c:\Users\ASUS\Desktop\minor project\MePhy Dataset\MePhy Dataset\MePhy Dataset")
OUTPUT_DIR   = Path(r"c:\Users\ASUS\Desktop\minor project\results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SEC  = 30          # seconds per window
OVERLAP_SEC = 15          # overlap between consecutive windows
STEP_SEC    = WINDOW_SEC - OVERLAP_SEC   # 15 s stride
SEED        = 42

CONDITIONS = ['rest', 'cognitive-fatigue', 'physical-fatigue', 'combo-fatigue']
COND_TO_CLASS = {
    'rest': 0,                    # Low fatigue
    'cognitive-fatigue': 1,       # Medium fatigue
    'physical-fatigue': 1,        # Medium fatigue
    'combo-fatigue': 2,           # High fatigue
}
CLASS_NAMES = ['Low', 'Medium', 'High']
NUM_CLASSES = 3

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ================================================================
# DATA LOADING  (file → per-second arrays)
# ================================================================

def parse_ecg(filepath):
    """Parse ECG CSV → Nx3 array [HR, IBI, raw_value], 1 row per second."""
    try:
        rows = []
        with open(filepath, 'r') as fh:
            for line in fh:
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) >= 6:
                    try:
                        rows.append([float(parts[1]),   # HR
                                     float(parts[2]),   # IBI (inter-beat interval)
                                     float(parts[5])])  # raw value
                    except ValueError:
                        continue
        return np.array(rows, dtype=np.float32) if rows else None
    except FileNotFoundError:
        return None


def load_signal_values(filepath):
    """Load the value column from a tab-separated file (EDA / EMG / EyeBlink)."""
    try:
        df = pd.read_csv(filepath, sep='\t', header=None, usecols=[1], names=['v'])
        df['v'] = pd.to_numeric(df['v'], errors='coerce')
        arr = df['v'].dropna().values.astype(np.float32)
        return arr if len(arr) > 0 else None
    except Exception:
        return None


def bin_to_seconds(raw, n_seconds):
    """Bin a high-rate 1-D signal into per-second statistics → Nx4 [mean, std, range, rms]."""
    n = len(raw)
    sps = n // n_seconds
    if sps < 1:
        return np.zeros((n_seconds, 4), dtype=np.float32)
    usable = sps * n_seconds
    arr = raw[:usable].reshape(n_seconds, sps)
    return np.column_stack([
        arr.mean(axis=1),
        arr.std(axis=1),
        arr.max(axis=1) - arr.min(axis=1),
        np.sqrt(np.mean(arr ** 2, axis=1)),
    ]).astype(np.float32)


def bin_blink_to_seconds(raw, n_seconds):
    """Bin blink flags → Nx2 [count, fraction]."""
    n = len(raw)
    sps = n // n_seconds
    if sps < 1:
        return np.zeros((n_seconds, 2), dtype=np.float32)
    usable = sps * n_seconds
    arr = raw[:usable].reshape(n_seconds, sps)
    return np.column_stack([arr.sum(axis=1), arr.mean(axis=1)]).astype(np.float32)


# ================================================================
# FEATURE EXTRACTION  (one window → 33-dim vector)
# ================================================================

def extract_features(ecg_w, eda_w, emg_w, blink_w):
    """Return an ordered dict of ~33 scalar features from one window."""
    f = {}

    # --- ECG (cols: HR, IBI, raw) ---
    if ecg_w is not None and len(ecg_w) >= 2:
        hr = ecg_w[:, 0]
        f['hr_mean']   = hr.mean()
        f['hr_std']    = hr.std()
        f['hr_min']    = hr.min()
        f['hr_max']    = hr.max()
        f['hr_range']  = float(np.ptp(hr))
        f['hr_median'] = np.median(hr)
        f['hr_cv']     = hr.std() / (hr.mean() + 1e-8)
        f['hr_slope']  = stats.linregress(np.arange(len(hr)), hr).slope

        ibi = ecg_w[:, 1]
        f['ibi_mean']  = ibi.mean()
        f['ibi_std']   = ibi.std()                                           # ≈ SDNN
        d = np.diff(ibi)
        f['ibi_rmssd'] = np.sqrt(np.mean(d ** 2)) if len(d) > 0 else 0.0

        raw_e = ecg_w[:, 2]
        f['ecg_raw_mean'] = raw_e.mean()
        f['ecg_raw_std']  = raw_e.std()
    else:
        for k in ('hr_mean','hr_std','hr_min','hr_max','hr_range','hr_median',
                   'hr_cv','hr_slope','ibi_mean','ibi_std','ibi_rmssd',
                   'ecg_raw_mean','ecg_raw_std'):
            f[k] = 0.0

    # --- EDA (cols: mean, std, range, rms  per second) ---
    if eda_w is not None and len(eda_w) >= 2:
        col = eda_w[:, 0]
        f['eda_mean']     = col.mean()
        f['eda_std']      = col.std()
        f['eda_min']      = col.min()
        f['eda_max']      = col.max()
        f['eda_range']    = float(np.ptp(col))
        f['eda_var_mean'] = eda_w[:, 1].mean()
        f['eda_rms_mean'] = eda_w[:, 3].mean()
        f['eda_slope']    = stats.linregress(np.arange(len(col)), col).slope
    else:
        for k in ('eda_mean','eda_std','eda_min','eda_max','eda_range',
                   'eda_var_mean','eda_rms_mean','eda_slope'):
            f[k] = 0.0

    # --- EMG ---
    if emg_w is not None and len(emg_w) >= 2:
        col = emg_w[:, 0]
        f['emg_mean']     = col.mean()
        f['emg_std']      = col.std()
        f['emg_min']      = col.min()
        f['emg_max']      = col.max()
        f['emg_range']    = float(np.ptp(col))
        f['emg_rms_mean'] = emg_w[:, 3].mean()
        f['emg_var_mean'] = emg_w[:, 1].mean()
        f['emg_slope']    = stats.linregress(np.arange(len(col)), col).slope
    else:
        for k in ('emg_mean','emg_std','emg_min','emg_max','emg_range',
                   'emg_rms_mean','emg_var_mean','emg_slope'):
            f[k] = 0.0

    # --- Eye Blinking (cols: count, fraction  per second) ---
    if blink_w is not None and len(blink_w) >= 2:
        bc = blink_w[:, 0]
        f['blink_rate']          = bc.sum()
        f['blink_rate_per_min']  = bc.sum() * 60.0 / len(bc)
        f['blink_fraction_mean'] = blink_w[:, 1].mean()
        f['blink_std']           = bc.std()
    else:
        for k in ('blink_rate','blink_rate_per_min','blink_fraction_mean','blink_std'):
            f[k] = 0.0

    # sanitise
    for k in f:
        if not np.isfinite(f[k]):
            f[k] = 0.0
    return f


def make_ts_window(ecg_w, eda_w, emg_w, blink_w, L=30):
    """Create a 4-channel × L time-series tensor for DL models."""
    def _pad(arr, length):
        if arr is None or len(arr) == 0:
            return np.zeros(length, dtype=np.float32)
        if len(arr) >= length:
            return arr[:length].astype(np.float32)
        out = np.zeros(length, dtype=np.float32)
        out[:len(arr)] = arr.astype(np.float32)
        return out

    ch0 = _pad(ecg_w[:, 0]  if ecg_w is not None and len(ecg_w) > 0  else None, L)
    ch1 = _pad(eda_w[:, 0]  if eda_w is not None and len(eda_w) > 0  else None, L)
    ch2 = _pad(emg_w[:, 3]  if emg_w is not None and len(emg_w) > 0  else None, L)
    ch3 = _pad(blink_w[:, 0] if blink_w is not None and len(blink_w) > 0 else None, L)
    return np.stack([ch0, ch1, ch2, ch3])   # (4, L)


# ================================================================
# DATASET BUILDING
# ================================================================

def build_dataset():
    cache = OUTPUT_DIR / 'processed_data.npz'
    if cache.exists():
        print(f"[INFO] Loading cached dataset from {cache}")
        d = np.load(cache, allow_pickle=True)
        return d['X_feat'], d['X_ts'], d['y'], d['groups'], list(d['feat_names'])

    all_feat, all_ts, all_y, all_g = [], [], [], []
    feat_names = None

    user_dirs = sorted(
        [d for d in DATASET_ROOT.iterdir() if d.is_dir() and d.name.startswith('user')],
        key=lambda p: int(p.name.replace('user', ''))
    )
    print(f"[INFO] Found {len(user_dirs)} users")

    for ui, udir in enumerate(user_dirs):
        uid = udir.name
        t0 = time.time()

        for cond in CONDITIONS:
            # 1. Load ECG (1 Hz baseline)
            ecg = parse_ecg(udir / 'ECG_Collection' / f'{uid}_{cond}.txt')
            if ecg is None or len(ecg) < WINDOW_SEC:
                continue
            n_sec = len(ecg)

            # 2. Load & bin EDA
            eda_raw = load_signal_values(udir / 'EDA_Collection' / f'{uid}_{cond}.txt')
            eda_ps  = bin_to_seconds(eda_raw, n_sec) if eda_raw is not None \
                      else np.zeros((n_sec, 4), dtype=np.float32)

            # 3. Load & bin EMG
            emg_raw = load_signal_values(udir / 'EMG_Collection' / f'{uid}_{cond}.txt')
            emg_ps  = bin_to_seconds(emg_raw, n_sec) if emg_raw is not None \
                      else np.zeros((n_sec, 4), dtype=np.float32)

            # 4. Load & bin Eye-Blink
            blink_raw = load_signal_values(udir / 'EyeBlinking_Collection' / f'{uid}_{cond}.txt')
            blink_ps  = bin_blink_to_seconds(blink_raw, n_sec) if blink_raw is not None \
                        else np.zeros((n_sec, 2), dtype=np.float32)

            # 5. Align to shortest
            min_len = min(len(ecg), len(eda_ps), len(emg_ps), len(blink_ps))
            if min_len < WINDOW_SEC:
                continue
            ecg      = ecg[:min_len]
            eda_ps   = eda_ps[:min_len]
            emg_ps   = emg_ps[:min_len]
            blink_ps = blink_ps[:min_len]

            label = COND_TO_CLASS[cond]

            # 6. Sliding-window extraction
            n_windows = (min_len - WINDOW_SEC) // STEP_SEC + 1
            for w in range(n_windows):
                s = w * STEP_SEC
                e = s + WINDOW_SEC
                feats = extract_features(ecg[s:e], eda_ps[s:e], emg_ps[s:e], blink_ps[s:e])
                if feat_names is None:
                    feat_names = list(feats.keys())
                all_feat.append(list(feats.values()))
                all_ts.append(make_ts_window(ecg[s:e], eda_ps[s:e], emg_ps[s:e], blink_ps[s:e], WINDOW_SEC))
                all_y.append(label)
                all_g.append(ui)

        dt = time.time() - t0
        if (ui + 1) % 5 == 0 or ui == 0:
            print(f"  [{ui+1:>3}/{len(user_dirs)}] {uid:>8}  {dt:5.1f}s  |  windows so far: {len(all_y)}")

    X_feat  = np.array(all_feat, dtype=np.float32)
    X_ts    = np.array(all_ts,   dtype=np.float32)
    y       = np.array(all_y,    dtype=np.int64)
    groups  = np.array(all_g,    dtype=np.int64)

    np.savez(cache, X_feat=X_feat, X_ts=X_ts, y=y, groups=groups,
             feat_names=np.array(feat_names))
    print(f"\n[INFO] Dataset: {X_feat.shape[0]} windows × {X_feat.shape[1]} features")
    bc = np.bincount(y, minlength=NUM_CLASSES)
    print(f"       Classes: {dict(zip(CLASS_NAMES, bc))}")
    return X_feat, X_ts, y, groups, feat_names


# ================================================================
# SUBJECT-WISE SPLIT  (70 / 15 / 15)
# ================================================================

def subject_split(X_feat, X_ts, y, groups):
    uids = np.unique(groups)
    rng  = np.random.RandomState(SEED)
    rng.shuffle(uids)

    n = len(uids)
    n_tr = int(0.70 * n)
    n_va = int(0.15 * n)
    train_set = set(uids[:n_tr])
    val_set   = set(uids[n_tr:n_tr + n_va])
    test_set  = set(uids[n_tr + n_va:])

    masks = {}
    for name, s in [('train', train_set), ('val', val_set), ('test', test_set)]:
        masks[name] = np.isin(groups, list(s))

    splits = {}
    for name, m in masks.items():
        splits[name] = dict(X_feat=X_feat[m].copy(),
                            X_ts=X_ts[m].copy(),
                            y=y[m].copy())

    for name in ('train','val','test'):
        bc = np.bincount(splits[name]['y'], minlength=NUM_CLASSES)
        print(f"  {name:>5}: {splits[name]['y'].shape[0]:>5} samples  {dict(zip(CLASS_NAMES, bc))}")
    return splits


# ================================================================
# NORMALISATION  (fit on train only)
# ================================================================

def normalise(splits):
    scaler = StandardScaler()
    splits['train']['X_feat'] = scaler.fit_transform(splits['train']['X_feat'])
    splits['val']['X_feat']   = scaler.transform(splits['val']['X_feat'])
    splits['test']['X_feat']  = scaler.transform(splits['test']['X_feat'])

    nc = splits['train']['X_ts'].shape[1]
    mu = splits['train']['X_ts'].mean(axis=(0, 2))
    sd = splits['train']['X_ts'].std(axis=(0, 2))
    sd[sd == 0] = 1.0
    for sp in splits.values():
        for c in range(nc):
            sp['X_ts'][:, c, :] = (sp['X_ts'][:, c, :] - mu[c]) / sd[c]

    return splits, scaler


# ================================================================
# MODEL DEFINITIONS
# ================================================================

# 1. Random Forest
def train_rf(X, y):
    m = RandomForestClassifier(n_estimators=500, max_depth=25, min_samples_leaf=3,
                               class_weight='balanced', random_state=SEED, n_jobs=-1)
    m.fit(X, y)
    return m

# 2. XGBoost
def train_xgb(X, y, Xv, yv):
    cw = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES), y=y)
    sw = np.array([cw[c] for c in y])
    m = xgb.XGBClassifier(n_estimators=500, max_depth=8, learning_rate=0.05,
                           subsample=0.8, colsample_bytree=0.8, gamma=1,
                           objective='multi:softprob', num_class=NUM_CLASSES,
                           eval_metric='mlogloss', random_state=SEED,
                           use_label_encoder=False, verbosity=0)
    m.fit(X, y, sample_weight=sw, eval_set=[(Xv, yv)], verbose=False)
    return m


# 3. 1D-CNN
class CNN1D(nn.Module):
    def __init__(self, C=4, L=30, K=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(C, 32, 3, padding=1), nn.BatchNorm1d(32), nn.ReLU(),
            nn.Conv1d(32, 64, 3, padding=1), nn.BatchNorm1d(64), nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, 3, padding=1), nn.BatchNorm1d(128), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.4),
                                  nn.Linear(64, K))
    def forward(self, x):
        return self.head(self.net(x).squeeze(-1))


# 4. Transformer Encoder
class PosEnc(nn.Module):
    def __init__(self, d, maxlen=200):
        super().__init__()
        pe = torch.zeros(maxlen, d)
        pos = torch.arange(maxlen).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d, 2).float() * -(math.log(10000.0) / d))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer('pe', pe.unsqueeze(0))
    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class TransformerNet(nn.Module):
    def __init__(self, C=4, L=30, d=64, heads=4, layers=2, K=3):
        super().__init__()
        self.proj = nn.Linear(C, d)
        self.pe   = PosEnc(d, L)
        enc_layer = nn.TransformerEncoderLayer(d, heads, dim_feedforward=128,
                                               dropout=0.3, batch_first=True)
        self.enc  = nn.TransformerEncoder(enc_layer, layers)
        self.head = nn.Sequential(nn.Linear(d, 64), nn.ReLU(), nn.Dropout(0.4),
                                  nn.Linear(64, K))
    def forward(self, x):                     # x: (B, C, L)
        x = x.permute(0, 2, 1)                # (B, L, C)
        x = self.pe(self.proj(x))
        x = self.enc(x).mean(dim=1)
        return self.head(x)


# 5. Quantum-Classical Hybrid  (fallback: BiLSTM)
HAS_PENNYLANE = False
try:
    import pennylane as qml
    HAS_PENNYLANE = True
    print("[INFO] PennyLane available – will train Quantum Hybrid model")
except ImportError:
    print("[INFO] PennyLane not installed – will use BiLSTM as 5th model")

if HAS_PENNYLANE:
    NQ = 4
    qdev = qml.device('default.qubit', wires=NQ)

    @qml.qnode(qdev, interface='torch', diff_method='backprop')
    def qcircuit(inputs, weights):
        qml.AngleEmbedding(inputs, wires=range(NQ))
        qml.StronglyEntanglingLayers(weights, wires=range(NQ))
        return [qml.expval(qml.PauliZ(i)) for i in range(NQ)]

    class QuantumHybridNet(nn.Module):
        def __init__(self, F, K=3):
            super().__init__()
            self.pre = nn.Sequential(nn.Linear(F, 32), nn.ReLU(),
                                     nn.Linear(32, NQ), nn.Tanh())
            wshapes = {"weights": (2, NQ, 3)}
            self.ql  = qml.qnn.TorchLayer(qcircuit, wshapes)
            self.post = nn.Linear(NQ, K)
        def forward(self, x):
            x = self.pre(x) * np.pi
            x = self.ql(x)
            return self.post(x)

class BiLSTMNet(nn.Module):
    def __init__(self, C=4, K=3, H=64):
        super().__init__()
        self.lstm = nn.LSTM(C, H, 2, batch_first=True, bidirectional=True, dropout=0.3)
        self.head = nn.Sequential(nn.Linear(H*2, 64), nn.ReLU(), nn.Dropout(0.4),
                                  nn.Linear(64, K))
    def forward(self, x):
        x = x.permute(0, 2, 1)
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


# ================================================================
# GENERIC DL TRAINING LOOP  (early stopping, weighted CE, scheduler)
# ================================================================

def train_dl(model, trL, vaL, cw, epochs=100, lr=1e-3, patience=20, tag=''):
    model = model.to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=cw.to(DEVICE))
    opt = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.ReduceLROnPlateau(opt, 'min', patience=7, factor=0.5)

    best_vl, best_st, wait = float('inf'), None, 0
    hist = dict(tl=[], vl=[], va=[])

    for ep in range(epochs):
        model.train()
        tl = 0
        for xb, yb in trL:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            tl += loss.item() * xb.size(0)
        tl /= len(trL.dataset)

        model.eval()
        vl, cor, tot = 0, 0, 0
        with torch.no_grad():
            for xb, yb in vaL:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                out = model(xb)
                vl += criterion(out, yb).item() * xb.size(0)
                cor += (out.argmax(1) == yb).sum().item()
                tot += yb.size(0)
        vl /= len(vaL.dataset)
        va = cor / tot
        sched.step(vl)
        hist['tl'].append(tl); hist['vl'].append(vl); hist['va'].append(va)

        if vl < best_vl:
            best_vl = vl
            best_st = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                print(f"  [{tag}] Early stop @ epoch {ep+1}")
                break

        if (ep+1) % 20 == 0 or ep == 0:
            print(f"  [{tag}] Ep {ep+1:>3}: tl={tl:.4f}  vl={vl:.4f}  va={va:.4f}")

    if best_st:
        model.load_state_dict(best_st)
    model.eval()
    return model, hist


def dl_predict(model, loader):
    preds = []
    model.eval()
    with torch.no_grad():
        for xb, _ in loader:
            preds.append(model(xb.to(DEVICE)).argmax(1).cpu().numpy())
    return np.concatenate(preds)


# ================================================================
# EVALUATION  &  VISUALISATION
# ================================================================

def evaluate(y_true, y_pred, name):
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None,
                                                   labels=[0,1,2], zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(y_true, y_pred, average='macro',
                                                     zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=[0,1,2])
    res = dict(accuracy=round(acc,4), macro_precision=round(mp,4),
               macro_recall=round(mr,4), macro_f1=round(mf,4),
               per_class={}, confusion_matrix=cm.tolist())
    for i, c in enumerate(CLASS_NAMES):
        res['per_class'][c] = dict(precision=round(p[i],4),
                                   recall=round(r[i],4), f1=round(f1[i],4))
    print(f"\n{'='*55}\n  {name}\n{'='*55}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Macro F1 : {mf:.4f}")
    for c in CLASS_NAMES:
        m = res['per_class'][c]
        print(f"  {c:>7}: P={m['precision']:.4f}  R={m['recall']:.4f}  F1={m['f1']:.4f}")
    return res


def plot_cm(cm, name):
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax)
    ax.set_xlabel('Predicted'); ax.set_ylabel('True')
    ax.set_title(f'Confusion Matrix – {name}')
    plt.tight_layout()
    fp = OUTPUT_DIR / f'cm_{name.replace(" ","_")}.png'
    fig.savefig(fp, dpi=150); plt.close(fig)
    return str(fp)


def plot_histories(hists):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for n, h in hists.items():
        axes[0].plot(h['tl'], label=f'{n} train')
        axes[0].plot(h['vl'], '--', label=f'{n} val')
    axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Loss')
    axes[0].set_title('Loss Curves'); axes[0].legend(fontsize=8)
    for n, h in hists.items():
        axes[1].plot(h['va'], label=n)
    axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Validation Accuracy'); axes[1].legend(fontsize=8)
    plt.tight_layout()
    fp = OUTPUT_DIR / 'training_curves.png'
    fig.savefig(fp, dpi=150); plt.close(fig)


def plot_feature_importance(model, names, tag):
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
    else:
        return
    idx = np.argsort(imp)[::-1][:15]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(range(len(idx)), imp[idx][::-1])
    ax.set_yticks(range(len(idx)))
    ax.set_yticklabels([names[i] for i in idx[::-1]])
    ax.set_xlabel('Importance'); ax.set_title(f'Top 15 Features – {tag}')
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / f'feat_imp_{tag.replace(" ","_")}.png', dpi=150)
    plt.close(fig)


def save_comparison(results):
    rows = []
    for n, r in results.items():
        row = dict(Model=n, Accuracy=r['accuracy'],
                   Macro_Precision=r['macro_precision'],
                   Macro_Recall=r['macro_recall'], Macro_F1=r['macro_f1'])
        for c in CLASS_NAMES:
            for m in ('precision','recall','f1'):
                row[f'{c}_{m}'] = r['per_class'][c][m]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'comparison_table.csv', index=False)
    print('\n' + df.to_string(index=False))
    return df


# ================================================================
# MAIN
# ================================================================

def main():
    t_start = time.time()
    print('='*60)
    print('  Fatigue Detection Pipeline – MePhy Dataset')
    print(f'  Device: {DEVICE}')
    print('='*60)

    # --- 1. Data ---
    print('\n[1/6] Building dataset …')
    X_f, X_t, y, g, fnames = build_dataset()

    # --- 2. Split ---
    print('\n[2/6] Subject-wise split …')
    sp = subject_split(X_f, X_t, y, g)

    # --- 3. Normalise ---
    print('\n[3/6] Normalising …')
    sp, _ = normalise(sp)

    # --- 4. Prepare loaders ---
    cw = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES), y=sp['train']['y'])
    cw_t = torch.FloatTensor(cw)
    print(f"  Class weights: {dict(zip(CLASS_NAMES, np.round(cw,3)))}")

    BS = 64

    def _loaders(key, feat=False):
        X = sp[key]['X_feat'] if feat else sp[key]['X_ts']
        ds = TensorDataset(torch.FloatTensor(X), torch.LongTensor(sp[key]['y']))
        return DataLoader(ds, batch_size=BS, shuffle=(key == 'train'))

    ts_tr, ts_va, ts_te = _loaders('train'), _loaders('val'), _loaders('test')
    ft_tr, ft_va, ft_te = _loaders('train', True), _loaders('val', True), _loaders('test', True)

    results = {}
    hists   = {}

    # --- 5a. Random Forest ---
    print('\n[4/6] Training models …')
    print('\n  ── Random Forest ──')
    t0 = time.time()
    rf = train_rf(sp['train']['X_feat'], sp['train']['y'])
    rf_p = rf.predict(sp['test']['X_feat'])
    results['Random Forest'] = evaluate(sp['test']['y'], rf_p, 'Random Forest')
    plot_cm(np.array(results['Random Forest']['confusion_matrix']), 'Random Forest')
    plot_feature_importance(rf, fnames, 'Random Forest')
    print(f"  Time: {time.time()-t0:.1f}s")

    # --- 5b. XGBoost ---
    print('\n  ── XGBoost ──')
    t0 = time.time()
    xg = train_xgb(sp['train']['X_feat'], sp['train']['y'],
                    sp['val']['X_feat'], sp['val']['y'])
    xg_p = xg.predict(sp['test']['X_feat'])
    results['XGBoost'] = evaluate(sp['test']['y'], xg_p, 'XGBoost')
    plot_cm(np.array(results['XGBoost']['confusion_matrix']), 'XGBoost')
    plot_feature_importance(xg, fnames, 'XGBoost')
    print(f"  Time: {time.time()-t0:.1f}s")

    # --- 5c. 1D-CNN ---
    print('\n  ── 1D-CNN ──')
    t0 = time.time()
    cnn = CNN1D(C=4, L=WINDOW_SEC, K=NUM_CLASSES)
    cnn, ch = train_dl(cnn, ts_tr, ts_va, cw_t, epochs=120, lr=1e-3, patience=20, tag='1D-CNN')
    hists['1D-CNN'] = ch
    results['1D-CNN'] = evaluate(sp['test']['y'], dl_predict(cnn, ts_te), '1D-CNN')
    plot_cm(np.array(results['1D-CNN']['confusion_matrix']), '1D-CNN')
    print(f"  Time: {time.time()-t0:.1f}s")

    # --- 5d. Transformer ---
    print('\n  ── Transformer ──')
    t0 = time.time()
    tfm = TransformerNet(C=4, L=WINDOW_SEC, d=64, heads=4, layers=2, K=NUM_CLASSES)
    tfm, th = train_dl(tfm, ts_tr, ts_va, cw_t, epochs=120, lr=1e-3, patience=20, tag='Transformer')
    hists['Transformer'] = th
    results['Transformer'] = evaluate(sp['test']['y'], dl_predict(tfm, ts_te), 'Transformer')
    plot_cm(np.array(results['Transformer']['confusion_matrix']), 'Transformer')
    print(f"  Time: {time.time()-t0:.1f}s")

    # --- 5e. Quantum Hybrid or BiLSTM ---
    if HAS_PENNYLANE:
        print('\n  ── Quantum-Classical Hybrid ──')
        m5_name = 'Quantum Hybrid'
        t0 = time.time()
        nf = sp['train']['X_feat'].shape[1]
        qm = QuantumHybridNet(F=nf, K=NUM_CLASSES)
        qm, qh = train_dl(qm, ft_tr, ft_va, cw_t, epochs=60, lr=3e-3, patience=12, tag=m5_name)
        hists[m5_name] = qh
        results[m5_name] = evaluate(sp['test']['y'], dl_predict(qm, ft_te), m5_name)
    else:
        print('\n  ── BiLSTM ──')
        m5_name = 'BiLSTM'
        t0 = time.time()
        lstm = BiLSTMNet(C=4, K=NUM_CLASSES)
        lstm, qh = train_dl(lstm, ts_tr, ts_va, cw_t, epochs=120, lr=1e-3, patience=20, tag=m5_name)
        hists[m5_name] = qh
        results[m5_name] = evaluate(sp['test']['y'], dl_predict(lstm, ts_te), m5_name)
    plot_cm(np.array(results[m5_name]['confusion_matrix']), m5_name)
    print(f"  Time: {time.time()-t0:.1f}s")

    # --- 6. Save everything ---
    print('\n[5/6] Saving results …')
    plot_histories(hists)
    save_comparison(results)

    with open(OUTPUT_DIR / 'all_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # --- Summary ---
    best = max(results, key=lambda k: results[k]['accuracy'])
    print(f"\n{'='*60}")
    print(f"  BEST MODEL: {best}  –  Accuracy {results[best]['accuracy']:.4f}")
    print(f"  Total time: {(time.time()-t_start)/60:.1f} min")
    print(f"  Outputs:    {OUTPUT_DIR}")
    print(f"{'='*60}")
    return results


if __name__ == '__main__':
    main()

