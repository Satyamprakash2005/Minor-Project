# Multimodal Biosignal Fatigue Detection Using Hybrid Machine Learning and Quantum-Classical Architectures

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.15-orange.svg)](https://pytorch.org/)
[![PennyLane](https://img.shields.io/badge/PennyLane-0.45-purple.svg)](https://pennylane.ai/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4-red.svg)](https://xgboost.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, multi-stage machine learning and deep learning framework for **3-class human fatigue classification** (*Low*, *Medium*, *High*) using multimodal physiological biosignals (**ECG, EDA, EMG, and Eye Blinking**).

> **B.Tech Summer Internship Project**  
> **Department of Computer Science and Engineering**  
> **Birla Institute of Technology (BIT), Mesra, Ranchi, Jharkhand – 835215**

---

## 👥 Authors & Team
- **Abinash Boro** (BTECH/10059/23)
- **Satyam Prakash** (BTECH/10083/23)
- **Arnav Kumar** (BTECH/10167/23)

**Project Guide:** Dr. (Mrs.) Sanchita Paul, Associate Professor, Dept. of CSE, BIT Mesra  
**Head of Department:** Dr. Abhijit Mustafi  

---

## 📌 Project Overview
Undetected cognitive and physical fatigue is a primary cause of catastrophic accidents in transportation, aviation, industrial manufacturing, and high-stakes human-robot collaboration (HRC). 

This project formulates an objective, non-invasive biosignal screening pipeline benchmarked on the comprehensive **MePhy dataset** (60 human participants across 4 standardized experimental conditions). We address common pitfalls in existing fatigue literature (e.g., temporal data leakage and binary oversimplification) by enforcing **strict subject-wise holdout validation** across 3 discrete physiological fatigue regimes:
- **Low Fatigue (Class 0):** Baseline resting calm state.
- **Medium Fatigue (Class 1):** Moderate single-modality load (Stroop / N-Back cognitive tests or isolated physical exertion).
- **High Fatigue (Class 2):** Compound fatigue (concurrent cognitive and physical exhaustion).

---

## 🧠 Evaluated Model Paradigms
We comparatively evaluated 5 distinct algorithmic architectures under identical subject-wise training (42 subjects), validation (9 subjects), and test (9 subjects; 772 evaluation windows) splits:
1. **Extreme Gradient Boosting (XGBoost) [PRIMARY]:** Regularized gradient-boosted decision trees over 33 engineered statistical and physiological features.
2. **Random Forest (RF):** 500-tree bootstrap aggregation ensemble with feature bagging.
3. **1D Deep Convolutional Neural Network (1D-CNN):** 3-stage temporal convolution (`Conv1d` 32 → 64 → 128) with batch normalization and adaptive pooling on raw 4-channel time series.
4. **Time-Series Transformer Encoder:** Multi-head self-attention (MHSA, 4 heads, $d=64$, 2 encoder layers) with sinusoidal positional encodings.
5. **Quantum-Classical Hybrid Circuit:** 4-qubit parameterized variational quantum circuit with `AngleEmbedding` and `StronglyEntanglingLayers` via PennyLane QNodes.

---

## 📊 Empirical Benchmarking Results

### 3-Class Fatigue Classification (Unseen Holdout Cohort: 9 Subjects, 772 Windows)
| Model | Status | Overall Accuracy | Macro F1 | Low F1 | Medium F1 | High F1 | Medium Precision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | **PRIMARY** | **52.72%** | **0.4782** | 0.4196 | **0.6185** | 0.3963 | **71.35%** |
| **Random Forest** | Baseline | 51.94% | 0.4674 | 0.4225 | 0.6178 | 0.3619 | 69.85% |
| **1D-CNN** | Baseline | 42.62% | 0.4173 | 0.3902 | 0.4501 | 0.4117 | 69.58% |
| **Transformer** | Baseline | 42.23% | 0.4179 | 0.4094 | 0.4457 | 0.3986 | 74.07% |
| **Quantum Hybrid** | Baseline | 35.75% | 0.3553 | 0.3292 | 0.3211 | 0.4155 | 69.08% |

### Frontline Clinical & Industrial Screening Performance
- **Binary Screening (Calm Baseline vs. Active Fatigue):** **93.61% Accuracy**
- **Contrast Screening (Low Fatigue vs. Severe High Fatigue):** **86.99% Accuracy**

> **Key Architectural Insight:**  
> Tree-based models (XGBoost and Random Forest) significantly outperformed deep sequence models on unseen test subjects. Biosignals exhibit massive inter-individual baseline variance (e.g., resting heart rate differences); handcrafted physiological biomarkers (HRV SDNN/RMSSD, EDA derivative slope, EMG RMS power) provide critical inductive biases that normalize individual baselines, whereas raw neural networks suffer from distribution shift when trained on moderate-sized cohorts without extensive pre-training.

---

## 📁 Repository Structure
```text
├── fatigue_detection.py                  # Full end-to-end pipeline (Data loader, feature extraction, 5 models)
├── generate_report.py                    # Generates the complete Word (.docx) B.Tech project report
├── generate_figures.py                   # Generates diagrams and confusion matrix visualizations
├── push_to_github.py                     # Standalone Python Git push utility (no git CLI needed)
├── Fatigue_Detection_Project_Report.docx # Formatted academic report matching BIT Mesra B.Tech template
├── ProjectReport_BTECH_10059_23__1___1_.pdf # Reference format template
├── .gitignore                            # Excludes large raw datasets and binary caches
├── results/
│   ├── all_results.json                  # Detailed numerical metrics, per-class stats, and confusion matrices
│   ├── comparison_table.csv              # Model comparison matrix
│   ├── fig_4_3_1_confusion_matrices.png  # Combined confusion matrices for all 5 models
│   ├── feat_imp_XGBoost.png              # Top 15 physiological features ranked by XGBoost
│   ├── training_curves.png               # Training/validation loss and convergence curves
│   ├── fig_2_2_1_residual_block.png      # ResNet residual learning diagram
│   ├── fig_2_2_2_dense_block.png         # DenseNet iterative concatenation diagram
│   ├── fig_2_2_3_efficientnet.png        # EfficientNet compound scaling diagram
│   ├── fig_2_3_1_transformer.png         # Multi-channel biosignal Transformer diagram
│   └── bit_mesra_logo.png                # High-resolution institute emblem
└── README.md                             # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- NVIDIA GPU with CUDA support (optional, CPU execution fully supported)

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Satyamprakash2005/Minor-Project.git
cd Minor-Project
pip install numpy pandas scikit-learn xgboost matplotlib seaborn scipy torch pennylane python-docx
```

### 3. Running the Complete Training & Evaluation Pipeline
Execute the full pipeline script:
```bash
python fatigue_detection.py
```
This script will:
1. Load and synchronize ECG, EDA, EMG, and Eye Blinking biosignals across all 60 users.
2. Segment continuous records into 30-second sliding windows (15s overlap).
3. Compute 33 time-domain, frequency-domain, and physiological features per window.
4. Execute strict subject-wise train/val/test splits (70/15/15).
5. Train all 5 architectures (Random Forest, XGBoost, 1D-CNN, Transformer, Quantum Hybrid).
6. Save metrics and plots into the `results/` folder.

### 4. Regenerating the Word Report
To regenerate the official academic report:
```bash
python generate_report.py
```

---

## 📑 References & Citations
1. **MePhy Dataset:** Gabbi, M., Cornia, L., Villani, V., & Sabattini, L. (2024). *Understanding Fatigue Through Biosignals: A Comprehensive Dataset*. ACM/IEEE HRI '24, pp. 842–846. [doi:10.1145/3610977.3637485](https://doi.org/10.1145/3610977.3637485).
2. **Physiological Signal Analysis:** Kakhi, K., Khosravi, A., Alizadehsani, R., & Acharya, U. R. (2025). *Exploring the Relationships Between Physiological Signals During Automated Fatigue Detection*. [arXiv:2509.21794](https://arxiv.org/abs/2509.21794).
3. **XGBoost:** Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. ACM KDD '16, pp. 785–794. [arXiv:1603.02754](https://arxiv.org/abs/1603.02754).
4. **Transformers:** Vaswani, A., et al. (2017). *Attention Is All You Need*. NeurIPS 2017. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).
5. **Quantum Machine Learning:** Bergholm, V., et al. (2018). *PennyLane: Automatic Differentiation of Hybrid Quantum-Classical Computations*. [arXiv:1811.04968](https://arxiv.org/abs/1811.04968).

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
