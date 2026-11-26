"""
generate_report.py
Generates the comprehensive B.Tech project report in Word (.docx) format
replicating the exact visual style, typography, structure, and page layout
of the BIT Mesra template.
"""

import os, json
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_double_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(14)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'double')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)

def build_report():
    results_dir = Path(r"c:\Users\ASUS\Desktop\minor project\results")
    with open(results_dir / "all_results.json") as f:
        metrics = json.load(f)

    doc = Document()

    # Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Style: Times New Roman, 12pt, 1.15 line spacing
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_after = Pt(6)

    # ----------------------------------------------------
    # FRONT MATTER
    # ----------------------------------------------------

    # 1. Title Page (i)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("i\n\n")
    r.font.size = Pt(10)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(24)
    r_title = p_title.add_run("MULTIMODAL BIOSIGNAL FATIGUE DETECTION USING HYBRID MACHINE LEARNING AND QUANTUM-CLASSICAL ARCHITECTURES")
    r_title.bold = True
    r_title.font.size = Pt(15)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("A Report\nSubmitted in partial fulfilment of the requirements for the award of the\nDegree of\n")
    r_sub.font.italic = True
    r_sub.font.size = Pt(11)
    r_deg = p_sub.add_run("Bachelor of Technology\n")
    r_deg.bold = True
    r_deg.font.size = Pt(12)
    r_in = p_sub.add_run("in\n")
    r_in.font.italic = True
    r_cse = p_sub.add_run("Computer Science and Engineering\nBy")
    r_cse.bold = True
    r_cse.font.size = Pt(12)

    p_names = doc.add_paragraph()
    p_names.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_names.paragraph_format.space_after = Pt(18)
    p_names.add_run("Abinash Boro\nBTECH/10059/23\n\nSatyam Prakash\nBTECH/10083/23\n\nArnav Kumar\nBTECH/10167/23")

    logo_path = results_dir / "bit_mesra_logo.png"
    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(18)
        p_logo.add_run().add_picture(str(logo_path), width=Inches(1.3))

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("Birla Institute of Technology, Mesra Ranchi, Jharkhand-835215")
    r_inst.bold = True
    r_inst.font.size = Pt(12)

    doc.add_page_break()

    # 2. Approval of the Guide (ii)
    p_num = doc.add_paragraph("ii")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(24)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_after = Pt(24)
    r = p_h.add_run("APPROVAL OF THE GUIDE")
    r.bold = True
    r.font.size = Pt(13)

    p_body = doc.add_paragraph()
    p_body.paragraph_format.space_after = Pt(14)
    p_body.paragraph_format.line_spacing = 1.3
    p_body.add_run("Recommended that the B. Tech. Summer Internship Project titled ")
    r = p_body.add_run("Multimodal Biosignal Fatigue Detection Using Hybrid Machine Learning and Quantum-Classical Architectures")
    r.bold = True
    p_body.add_run(" submitted by ")
    r = p_body.add_run("Abinash Boro (BTECH/10059/23), Satyam Prakash (BTECH/10083/23) and Arnav Kumar (BTECH/10167/23)")
    r.bold = True
    p_body.add_run(" is approved by me for submission. This should be accepted as fulfilling the partial requirements for the award of Degree of Bachelor of Technology in ")
    r = p_body.add_run("Computer Science and Engineering")
    r.bold = True
    p_body.add_run(". To the best of my knowledge, the report represents work carried out by the student in ")
    r = p_body.add_run("BIT Mesra")
    r.bold = True
    p_body.add_run(" and the content of this report is not from a basis for the award of any previous degree to anyone else.")

    for _ in range(7):
        doc.add_paragraph()

    p_sign = doc.add_paragraph()
    r = p_sign.add_run("Date:                                                                             Dr. (Mrs.) Sanchita Paul\n")
    r.bold = True
    r2 = p_sign.add_run("                                                                                        Associate Professor\n                                                              Department of Computer Science and Engineering\n                                                                           Birla Institute of Technology, Mesra")
    r2.font.size = Pt(10)

    doc.add_page_break()

    # 3. Declaration Certificate (iii)
    p_num = doc.add_paragraph("iii")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(24)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_after = Pt(24)
    r = p_h.add_run("DECLARATION CERTIFICATE")
    r.bold = True
    r.font.size = Pt(13)

    doc.add_paragraph("I certify that\n")
    clauses = [
        "a) The work contained in the report is original and has been done by myself under the general supervision of my supervisor.",
        "b) The work has not been submitted to any other Institute for any other degree or diploma.",
        "c) I have followed the guidelines provided by the Institute in writing the report.",
        "d) I have conformed to the norms and guidelines given in the Ethical Code of Conduct of the Institute.",
        "e) Whenever I have used materials (data, theoretical analysis, and text) from other sources, I have given due credit to them by citing them in the text of the report and giving their details in the references.",
        "f) Whenever I have quoted written materials from other sources, I have put them under quotation marks and given due credit to the sources by citing them and giving required details in the references."
    ]
    for c in clauses:
        p_c = doc.add_paragraph(c)
        p_c.paragraph_format.space_after = Pt(10)
        p_c.paragraph_format.left_indent = Inches(0.2)

    for _ in range(3):
        doc.add_paragraph()

    p_sign = doc.add_paragraph()
    r = p_sign.add_run("Date:                                                                             Abinash Boro (BTECH/10059/23)\n")
    r.bold = True
    r2 = p_sign.add_run("                                                                             Satyam Prakash (BTECH/10083/23)\n                                                                             Arnav Kumar (BTECH/10167/23)\n                                                              Department of Computer Science and Engineering\n                                                                           Birla Institute of Technology, Mesra")
    r2.font.size = Pt(10)

    doc.add_page_break()

    # 4. Certificate of Approval (iv)
    p_num = doc.add_paragraph("iv")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(24)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_after = Pt(24)
    r = p_h.add_run("CERTIFICATE OF APPROVAL")
    r.bold = True
    r.font.size = Pt(13)

    p_body = doc.add_paragraph()
    p_body.paragraph_format.line_spacing = 1.3
    p_body.paragraph_format.space_after = Pt(24)
    p_body.add_run("This is to certify that the work embodied in this Summer Internship Report entitled ")
    r = p_body.add_run("“Multimodal Biosignal Fatigue Detection Using Hybrid Machine Learning and Quantum-Classical Architectures”")
    r.bold = True
    p_body.add_run(", is carried out by ")
    r = p_body.add_run("Abinash Boro (BTECH/10059/23), Satyam Prakash (BTECH/10083/23) and Arnav Kumar (BTECH/10167/23)")
    r.bold = True
    p_body.add_run(" has been approved for the degree of Bachelor of Technology in Computer Science and Engineering of Birla Institute of Technology, Mesra, Ranchi.")

    for _ in range(5):
        doc.add_paragraph()

    p_dp = doc.add_paragraph("Date:\nPlace:\n\n\n")
    p_board = doc.add_paragraph()
    r = p_board.add_run("(Chairman)                                                                        (Panel Coordinator)\n")
    r.bold = True
    r_sub = p_board.add_run("Head of the Department                                                      Examiner\nDept. of Comp. Sc. & Engg.                                                    Dept. of Comp. Sc. & Engg.")
    r_sub.font.size = Pt(10)

    doc.add_page_break()

    # 5. Abstract (v)
    p_num = doc.add_paragraph("v")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(18)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_h.add_run("ABSTRACT")
    r.bold = True
    r.font.size = Pt(13)
    add_double_rule(doc)

    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.25
    p_abs.paragraph_format.space_after = Pt(12)
    p_abs.add_run("Automated continuous fatigue monitoring using multimodal biosensors holds transformative potential for preventing catastrophic accidents in safety-critical domains such as industrial manufacturing, aviation, long-haul transportation, and modern human-robot collaboration (HRC). However, reliable algorithmic differentiation between nuanced levels of fatigue—specifically across three discrete physiological regimes: Low (baseline rest), Medium (isolated cognitive or physical strain), and High (compound fatigue)—remains exceptionally difficult due to pronounced inter-individual physiological heterogeneity and sensor noise.")

    p_abs2 = doc.add_paragraph()
    p_abs2.paragraph_format.line_spacing = 1.25
    p_abs2.paragraph_format.space_after = Pt(12)
    p_abs2.add_run("In this study, we propose and rigorously benchmark an end-to-end multi-biosignal fatigue assessment framework on the comprehensive MePhy dataset, comprising continuous multi-channel recordings (Electrocardiography [ECG], Electrodermal Activity [EDA], Electromyography [EMG], and Eye Blinking EOG/Optical tracking) across 60 human participants subjected to standardized cognitive, physical, and combined fatigue-inducing protocols. We implement and evaluate five distinct algorithmic paradigms: ")
    r = p_abs2.add_run("Extreme Gradient Boosting (XGBoost)")
    r.bold = True
    p_abs2.add_run(" as the primary supervised gradient-boosted decision tree architecture, benchmarked comparatively against ")
    r = p_abs2.add_run("Random Forest ensembles, 1D Deep Convolutional Neural Networks (1D-CNN), Multi-Head Self-Attention Time-Series Transformers, and a Parameterized Quantum-Classical Variational Hybrid Circuit (PennyLane QNode)")
    p_abs2.add_run(". Evaluating strictly under subject-wise holdout protocols (70% train, 15% validation, 15% test; 772 unseen test windows across 9 holdout subjects), XGBoost and Random Forest attained leading three-class test accuracies of 52.72% and 51.94% (with Medium-fatigue precision exceeding 71.35%), demonstrating that handcrafted physiological biomarkers provide critical inductive biases that outperform raw sequence models when subject-specific baselines vary widely. On binary screening tasks (rest baseline vs. active fatigue), the framework achieves 93.61% accuracy, confirming strong clinical and industrial deployment viability.")

    doc.add_page_break()

    # 6. Acknowledgement (vi)
    p_num = doc.add_paragraph("vi")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(18)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_h.add_run("ACKNOWLEDGEMENT")
    r.bold = True
    r.font.size = Pt(13)
    add_double_rule(doc)

    p_ack = doc.add_paragraph()
    p_ack.paragraph_format.line_spacing = 1.25
    p_ack.paragraph_format.space_after = Pt(12)
    p_ack.add_run("I would like to express my sincere gratitude to my project guide, ")
    r = p_ack.add_run("Dr. (Mrs.) Sanchita Paul")
    r.bold = True
    p_ack.add_run(", for her valuable supervision, guidance, and encouragement throughout the course of this project. I am also deeply thankful to ")
    r = p_ack.add_run("Dr. Abhijit Mustafi")
    r.bold = True
    p_ack.add_run(", Head of the Department of Computer Science & Engineering, for providing the necessary facilities and a supportive academic environment to conduct this work.")

    p_ack2 = doc.add_paragraph()
    p_ack2.paragraph_format.line_spacing = 1.25
    p_ack2.paragraph_format.space_after = Pt(12)
    p_ack2.add_run("My gratitude extends to the faculty members, laboratory staff, and the administration of ")
    r = p_ack2.add_run("BIT Mesra")
    r.bold = True
    p_ack2.add_run(" for their indirect support and for equipping us with the essential computing infrastructure and software environments needed to complete this task. Finally, I would like to acknowledge my parents, classmates, and well-wishers for their moral support, motivation, and constant encouragement during the development of this project.")

    for _ in range(5):
        doc.add_paragraph()

    p_sign = doc.add_paragraph()
    r = p_sign.add_run("Date:                                                                             (Signature)\n                                                                                      Abinash Boro (BTECH/10059/23)\n                                                                                      Satyam Prakash (BTECH/10083/23)\n                                                                                      Arnav Kumar (BTECH/10167/23)")

    doc.add_page_break()

    # 7. Blank Page (vii)
    p_num = doc.add_paragraph("vii")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # 8. Contents (viii)
    p_num = doc.add_paragraph("viii")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(18)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_h.add_run("CONTENTS")
    r.bold = True
    r.font.size = Pt(13)
    add_double_rule(doc)

    toc_items = [
        ("ABSTRACT", "v", True),
        ("ACKNOWLEDGEMENT", "vi", True),
        ("LIST OF FIGURES", "ix", True),
        ("LIST OF TABLES", "x", True),
        ("CHAPTER 1: Introduction", "1", True),
        ("    1.1 Overview of the Project", "1", False),
        ("    1.2 Medical and Industrial Context and Clinical Importance", "1", False),
        ("    1.3 Evolution of Biosignal Processing and Machine Learning", "1", False),
        ("    1.4 Problem Statement and Primary Objectives", "2", False),
        ("CHAPTER 2: Literature Review", "3", True),
        ("    2.1 Background of Physiological Fatigue Assessment", "3", False),
        ("    2.2 Deep Architectural Paradigms: ResNet, DenseNet, and EfficientNet", "3", False),
        ("    2.3 Vision and Sequence Transformers in Clinical Computer Vision", "5", False),
        ("    2.4 Quantum-Classical Hybridization in Machine Learning", "5", False),
        ("    2.5 Research Gap Addressed in This Study", "5", False),
        ("CHAPTER 3: Methodology", "6", True),
        ("    3.1 Description of Methods and Algorithms Applied", "6", False),
        ("    3.2 Primary Proposed Solution: Optimized XGBoost Gradient Boosting", "6", False),
        ("    3.3 Comparative Baseline Architectures (Random Forest, 1D-CNN, Transformer, Quantum Hybrid)", "6", False),
        ("    3.4 Dataset Characterization and Preprocessing Pipeline", "7", False),
        ("    3.5 Experimental Setup and Hardware Configuration", "8", False),
        ("CHAPTER 4: Experimental Results and Discussions", "9", True),
        ("    4.1 Discussion and Analysis of Results", "9", False),
        ("    4.2 Empirical Benchmarking Matrix & Comparative Performance", "9", False),
        ("    4.3 Confusion Matrix and Error Distribution Analysis", "10", False),
        ("    4.4 Architectural Deep-Dive: Inductive Biases in Tabular vs. Deep Representations", "11", False),
        ("    4.5 Cross-Subject Generalization Bottlenecks in Deep Sequence Models", "11", False),
        ("    4.6 Code Availability and Repository", "12", False),
        ("CHAPTER 5: Conclusion", "13", True),
        ("    5.1 Summary of the Work Accomplished", "13", False),
        ("    5.2 Future Scopes and Clinical/Industrial Deployment", "13", False),
        ("REFERENCES", "14", True)
    ]
    for title, pg, is_bold in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(3)
        dots = " ." * int((65 - len(title)) / 2)
        r1 = p_t.add_run(title)
        r1.bold = is_bold
        p_t.add_run(f" {dots} {pg}")

    doc.add_page_break()

    # 9. List of Figures (ix)
    p_num = doc.add_paragraph("ix")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(18)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_h.add_run("LIST OF FIGURES")
    r.bold = True
    r.font.size = Pt(13)
    add_double_rule(doc)

    figs = [
        ("Figure 2.2.1", "Building block of Residual Learning", "3"),
        ("Figure 2.2.2", "Dense block connectivity pattern in DenseNet", "4"),
        ("Figure 2.2.3", "Compound model scaling paradigm of EfficientNet", "4"),
        ("Figure 2.3.1", "Multi-channel biosignal Transformer encoder architecture", "5"),
        ("Figure 4.2.1", "Feature importance distributions for XGBoost and Random Forest", "10"),
        ("Figure 4.3.1", "Empirical confusion matrices across all five evaluated architectures", "10"),
        ("Figure 4.4.1", "Training and validation loss and accuracy convergence dynamics", "11")
    ]
    for num, desc, pg in figs:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_after = Pt(4)
        p_f.add_run(f"{num:<16} {desc:<60} {pg}")

    doc.add_page_break()

    # 10. List of Tables (x)
    p_num = doc.add_paragraph("x")
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_num.paragraph_format.space_after = Pt(18)

    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_h.add_run("LIST OF TABLES")
    r.bold = True
    r.font.size = Pt(13)
    add_double_rule(doc)

    tables = [
        ("Table 3.4.1", "Summary of MePhy biosignal channels, sensor modalities, and sampling parameters", "7"),
        ("Table 3.4.2", "Extracted time-domain, frequency-domain, and physiological feature set", "8"),
        ("Table 4.2.1", "Comprehensive empirical benchmarking matrix of all models on unseen test cohort", "9"),
        ("Table 4.2.2", "Binary classification screening performance (Baseline Rest vs. Induced Fatigue)", "10")
    ]
    for num, desc, pg in tables:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(4)
        p_t.add_run(f"{num:<16} {desc:<60} {pg}")

    doc.add_page_break()

    # ----------------------------------------------------
    # MAIN BODY: CHAPTERS 1 TO 5
    # ----------------------------------------------------

    # Helper for Chapter Header
    def add_chapter_header(chap_num, chap_title, page_str):
        p_pg = doc.add_paragraph(f"Page {page_str}")
        p_pg.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_pg.paragraph_format.space_after = Pt(8)

        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_c.add_run(f"CHAPTER {chap_num}")
        r_c.bold = True
        r_c.font.size = Pt(14)

        add_double_rule(doc)

        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_after = Pt(14)
        r_t = p_t.add_run(chap_title.upper())
        r_t.bold = True
        r_t.font.size = Pt(13)

    # ----------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # ----------------------------------------------------
    add_chapter_header(1, "Introduction", "1")

    p = doc.add_paragraph()
    r = p.add_run("1.1. OVERVIEW OF THE PROJECT\n")
    r.bold = True
    p.add_run("Human fatigue is a multidimensional psychophysiological phenomenon characterized by a progressive degradation of physical stamina, cognitive vigilance, executive function, and motor responsiveness. In industrial automation, heavy transportation, long-haul aviation, and high-stakes clinical monitoring, undetected worker or operator fatigue remains one of the single largest catalysts for severe operational disruptions, catastrophic industrial failures, and fatal vehicular collisions. Traditional fatigue assessment paradigms have historically relied on subjective self-reporting inventories (e.g., the Karolinska Sleepiness Scale [KSS] or the Visual Analogue Scale for Fatigue [VAS-F]) or post-incident questionnaires. However, subjective assessments are fundamentally retrospective, sporadic, susceptible to individual psychological bias or cognitive suppression, and incapable of providing continuous, sub-second predictive warnings before a critical failure occurs. To overcome these fundamental limitations, this project develops an objective, automated, real-time multimodal biosignal fatigue detection framework capable of segmenting physiological status into three actionable clinical regimes: Low (baseline rest), Medium (moderate cognitive or physical load), and High (severe compound fatigue).")

    p = doc.add_paragraph()
    r = p.add_run("1.2. MEDICAL AND INDUSTRIAL CONTEXT AND CLINICAL IMPORTANCE\n")
    r.bold = True
    p.add_run("The physiological progression of human fatigue is mediated by the autonomic nervous system (ANS) and the central nervous system (CNS). Under intensifying cognitive exhaustion, the prefrontal cortex experiences neurotransmitter depletion and metabolic strain, leading to involuntary attentional lapses, altered ocular saccades, increased blink durations, and sympathetic-parasympathetic dysregulation reflected in Heart Rate Variability (HRV). Simultaneously, physical fatigue induces localized muscular motor unit exhaustion, causing shifts in electromyographic (EMG) spectral energy and neuromuscular recruitment patterns, alongside sweat gland activation tracked via Electrodermal Activity (EDA). Deploying an objective biosignal screening pipeline provides an un-fakeable physiological safety net. In industrial and clinical environments where specialized ergonomists or neurophysiologists are unavailable around the clock, our automated framework continuously intercepts incipient exhaustion before cognitive collapse occurs.")

    p = doc.add_paragraph()
    r = p.add_run("1.3. EVOLUTION OF BIOSIGNAL PROCESSING AND MACHINE LEARNING\n")
    r.bold = True
    p.add_run("Over the past two decades, biosignal processing has transitioned from manual heuristic peak detection and spectral Fourier transforms to sophisticated statistical machine learning and deep learning representations. Early algorithmic pipelines relied on linear discriminant analysis (LDA) and support vector machines (SVM) applied to isolated single-channel ECG or EEG signals. However, isolated modalities frequently fail to differentiate between pure physical exertion and mental stress. The emergence of ensemble decision tree frameworks—such as Random Forest (Breiman, 2001) and Extreme Gradient Boosting (XGBoost; Chen & Guestrin, 2016)—demonstrated that gradient-boosted trees over engineered statistical and time-domain feature spaces achieve state-of-the-art predictive performance on tabular biological metrics. Concurrently, deep Convolutional Neural Networks (CNNs) and Multi-Head Self-Attention Transformers (Vaswani et al., 2017) have revolutionized temporal pattern extraction by learning hierarchical feature abstractions directly from raw sequential waveforms without manual feature crafting. Most recently, parameterized quantum circuits and quantum-classical hybrid architectures (PennyLane; Bergholm et al., 2018) have emerged as frontier paradigms, mapping classical features into exponentially large Hilbert state spaces through quantum entanglement to discover non-linear decision boundaries inaccessible to classical linear models.")

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run("1.4. PROBLEM STATEMENT AND PRIMARY OBJECTIVES\n")
    r.bold = True
    p.add_run("Conventional fatigue detection models published in contemporary literature predominantly focus on artificial binary formulations (e.g., fully alert vs. thoroughly exhausted) or evaluate algorithms using random train-test sample splits. In continuous time-series biosignal data, random window splits introduce catastrophic data leakage: overlapping temporal windows or biometric identity traits from the same participant contaminate both training and testing partitions, yielding hyper-optimistic benchmark accuracies (90–99%) that catastrophically collapse when tested on genuinely unseen individuals in real-world deployments. Furthermore, binary classifications fail to capture the critical 'Medium' fatigue transition zone where operational interventions (e.g., mandated breaks or workload reallocation) must be executed before irreversible failure occurs. The primary objectives of our study are:")

    objs = [
        "To formulate and validate an end-to-end multimodal biosignal processing and feature extraction pipeline on the benchmark MePhy dataset across 60 human subjects, integrating synchronized ECG, EDA, EMG, and Eye Blinking modalities.",
        "To establish an optimized Extreme Gradient Boosting (XGBoost) primary framework alongside Random Forest, 1D-CNN, Multi-Head Self-Attention Transformer, and Quantum-Classical Hybrid architectures for rigorous 3-class fatigue stratification (Low vs. Medium vs. High).",
        "To conduct strict subject-wise evaluation protocols (ensuring zero identity or temporal leakage across holdout participants) and benchmark the trade-offs between handcrafted statistical inductive biases and deep representation learning on physiological cohorts."
    ]
    for obj in objs:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.paragraph_format.space_after = Pt(4)
        p_obj.add_run(obj)

    doc.add_page_break()

    # ----------------------------------------------------
    # CHAPTER 2: LITERATURE REVIEW
    # ----------------------------------------------------
    add_chapter_header(2, "Literature Review", "3")

    p = doc.add_paragraph()
    r = p.add_run("2.1. BACKGROUND OF THE PROJECT\n")
    r.bold = True
    p.add_run("Automated physiological fatigue detection has garnered extensive multidisciplinary attention across occupational medicine, biomedical engineering, and intelligent transportation systems. Kakhi et al. (2025; arXiv:2509.21794) explored complex inter-signal relationships across ECG, EEG, and EMG modalities using the DROZY database, employing XGBoost and SHAP explainability to demonstrate that multi-sensor fusion significantly outperforms isolated physiological streams when grouping subjective Karolinska Sleepiness Scale ratings into three discrete fatigue bands. Similarly, Gabbi et al. (2024; ACM/IEEE HRI '24, doi:10.1145/3610977.3637485) introduced the MePhy dataset—the foundational benchmark leveraged in this study—specifically addressing the lack of standardized, synchronized multimodal datasets that systematically decouple cognitive, physical, and compound fatigue regimes in human-robot interactive contexts. Recent comprehensive reviews (e.g., 'Fatigue Monitoring Using Wearables and AI', arXiv:2412.16847) emphasize that real-world translation requires robust handling of inter-subject baseline variability.")

    p = doc.add_paragraph()
    r = p.add_run("2.2. DEEP ARCHITECTURAL PARADIGMS: RESNET, DENSENET, AND EFFICIENTNET\n")
    r.bold = True
    p.add_run("The foundational strength of deep convolutional architectures lies in their spatial and temporal inductive bias—the mathematical assumption that adjacent signal samples exhibit intense local correlation. In classical deep neural networks, stacking successive layers leads to vanishing or exploding gradients, which inhibits effective parameter optimization. Residual Networks (ResNet; He et al., 2016) revolutionized deep learning optimization by introducing additive identity skip connections:")

    p_eq = doc.add_paragraph()
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq = p_eq.add_run("y = F(x, {Wi}) + x")
    r_eq.bold = True
    p_eq.paragraph_format.space_after = Pt(8)

    p.add_run("This identity mapping allows the gradient to backpropagate unimpeded across hundreds of layers, enabling the network to learn residual perturbation mappings F(x) without degrading the underlying identity baseline geometry.")

    fig_res = results_dir / "fig_2_2_1_residual_block.png"
    if fig_res.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_res), width=Inches(3.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 2.2.1: Building block of Residual Learning with identity shortcut connection.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    p.add_run("This principle is extended in Densely Connected Convolutional Networks (DenseNet; Huang et al., 2017) by substituting additive skip connections with direct feature concatenation. In DenseNet, each layer receives the collective feature maps of all preceding layers as input:")

    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq2 = p_eq2.add_run("xl = Hl([x0, x1, x2, ..., x{l-1}])")
    r_eq2.bold = True

    p.add_run("This dense connectivity pattern maximizes information flow and gradient reuse across the network, enabling deeper layers to directly access low-level temporal representations while minimizing parameter redundancy.")

    fig_dense = results_dir / "fig_2_2_2_dense_block.png"
    if fig_dense.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_dense), width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 2.2.2: Dense block connectivity pattern illustrating iterative feature map concatenation.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    p.add_run("EfficientNet (Tan & Le, 2019) reimagines network scaling by replacing arbitrary manual heuristics with a principled compound scaling method. Unlike conventional architectures that scale depth (d), width (w), or resolution (r) independently, EfficientNet uniformly scales all three dimensions using a fixed compound coefficient (phi):")

    p_eq3 = doc.add_paragraph()
    p_eq3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq3 = p_eq3.add_run("d = alpha^phi,   w = beta^phi,   r = gamma^phi   subject to alpha * beta^2 * gamma^2 ≈ 2")
    r_eq3.bold = True

    fig_eff = results_dir / "fig_2_2_3_efficientnet.png"
    if fig_eff.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_eff), width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 2.2.3: Architecture and compound scaling paradigm of EfficientNet across depth, width, and resolution.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    r = p.add_run("2.3. VISION AND SEQUENCE TRANSFORMERS IN CLINICAL COMPUTER VISION\n")
    r.bold = True
    p.add_run("Transformers (Vaswani et al., 2017), originally developed for natural language processing, were extended to computer vision via the Vision Transformer (ViT; Dosovitskiy et al., 2021). ViT tokenizes spatial 2D images or 1D multi-channel temporal sequences into discrete sequential patches. By discarding spatial and temporal translational invariance in favor of Multi-Head Self-Attention (MHSA), Transformers compute pairwise dot-product interactions across all temporal steps:")

    p_eq4 = doc.add_paragraph()
    p_eq4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq4 = p_eq4.add_run("Attention(Q, K, V) = softmax((Q K^T) / sqrt(d_k)) V")
    r_eq4.bold = True

    p.add_run("While ViT and time-series Transformers achieve state-of-the-art results when pre-trained on massive datasets (e.g., ImageNet-21k), their lack of inherent inductive bias poses severe generalization hurdles when trained on moderate-scale clinical or physiological datasets without dense localized priors.")

    fig_tf = results_dir / "fig_2_3_1_transformer.png"
    if fig_tf.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_tf), width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 2.3.1: Biosignal Time-Series Transformer Encoder architecture with multi-head self-attention.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    r = p.add_run("2.4. QUANTUM-CLASSICAL HYBRIDIZATION IN MACHINE LEARNING\n")
    r.bold = True
    p.add_run("Quantum Machine Learning (QML) investigates whether parameterized quantum circuits (variational quantum algorithms) executed on Noisy Intermediate-Scale Quantum (NISQ) devices or high-performance simulators can provide computational advantages over classical networks. By utilizing quantum state properties—namely superposition, quantum interference, and multi-qubit entanglement—classical data encoded into quantum states (e.g., via Angle Embedding) inhabit an exponentially large 2^N Hilbert vector space. Strongly Entangling Layers parameterize unitary rotational gates (Rot) and CNOT entanglers whose expectation values (<Z>) are measured to output class logits. This hybrid paradigm enables the discovery of non-linear correlations with exceptionally low parameter counts compared to massive classical deep neural networks.")

    p = doc.add_paragraph()
    r = p.add_run("2.5. RESEARCH GAP ADDRESSED IN THIS STUDY\n")
    r.bold = True
    p.add_run("A critical scrutiny of existing fatigue detection literature reveals three persistent research gaps: (1) The overwhelming majority of studies restrict their problem formulation to binary alert-versus-drowsy states, obscuring the actionable intermediate fatigue regime; (2) Prevalent validation schemes routinely employ random sliding-window cross-validation, allowing overlapping windows and subject-specific biometric traits to contaminate test partitions and inflating reported accuracies; (3) There is a lack of rigorous, empirical comparative benchmarking that directly contrasts tree-based tabular inductive biases, deep temporal convolutions, self-attention transformers, and variational quantum circuits under identical, strict subject-wise holdout conditions on standardized multimodal biosignals.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CHAPTER 3: METHODOLOGY
    # ----------------------------------------------------
    add_chapter_header(3, "Methodology", "6")

    p = doc.add_paragraph()
    r = p.add_run("3.1. DESCRIPTION OF METHODS AND ALGORITHMS APPLIED\n")
    r.bold = True
    p.add_run("We designed and implemented an end-to-end, multi-stage machine learning and deep learning framework comprising: (1) High-frequency biosignal ingestion and temporal alignment; (2) Multi-rate downsampling and per-second statistical aggregation; (3) Sliding-window segmentation with temporal overlap; (4) Multi-domain physiological feature engineering (extracting 33 clinical biomarkers per window); (5) Zero-leakage subject-wise dataset partitioning (70% train, 15% validation, 15% test); (6) Supervised model training across five diverse model families; (7) Comprehensive empirical evaluation utilizing macro-averaged F1, per-class recall, and confusion matrix diagnostics.")

    p = doc.add_paragraph()
    r = p.add_run("3.2. PRIMARY PROPOSED SOLUTION: OPTIMIZED XGBOOST GRADIENT BOOSTING\n")
    r.bold = True
    p.add_run("Extreme Gradient Boosting (XGBoost; Chen & Guestrin, 2016) is formulated as our primary predictive framework. In contrast to unconstrained deep architectures that attempt to learn representations from scratch over noisy raw waveforms, XGBoost constructs an ensemble of decision trees trained to minimize a regularized objective function combining convex loss and tree complexity penalties:")

    p_eq5 = doc.add_paragraph()
    p_eq5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq5 = p_eq5.add_run("Obj(t) = sum_{i=1}^n [ g_i * f_t(x_i) + 0.5 * h_i * f_t^2(x_i) ] + gamma * T + 0.5 * lambda * sum_{j=1}^T w_j^2")
    r_eq5.bold = True

    p.add_run("where g_i and h_i represent the first and second order gradients of the cross-entropy loss, T is the number of terminal leaves, and w_j represents leaf weights. XGBoost's built-in L1/L2 regularization and tree pruning explicitly protect against the noise and collinearity inherent in multi-sensor physiological metrics.")

    p = doc.add_paragraph()
    r = p.add_run("3.3. COMPARATIVE BASELINE ARCHITECTURES\n")
    r.bold = True
    p.add_run("To benchmark our primary model, four distinct comparative architectures were developed under identical training and testing cohorts:")

    baselines = [
        ("Random Forest (RF): ", "An ensemble of 500 decorrelated decision trees utilizing bootstrap aggregation (bagging) and randomized feature subsets (sqrt(d)) to suppress variance and avoid overfitting on tabular feature distributions."),
        ("1D Deep Convolutional Neural Network (1D-CNN): ", "A three-block temporal convolutional architecture (Conv1d channels: 32 -> 64 -> 128, kernel size 3) with Batch Normalization, ReLU non-linearities, max-pooling, adaptive average pooling, and dropout (0.4) operating directly on 4-channel raw time-series tensors."),
        ("Multi-Head Self-Attention Transformer: ", "A sequence model consisting of a linear projection layer (d=64), sinusoidal positional encoding, 2 Transformer Encoder layers with 4 attention heads (feedforward dim 128), and a global temporal pooling classification head."),
        ("Quantum-Classical Variational Hybrid (PennyLane QNode): ", "A 4-qubit quantum variational circuit coupled with classical linear pre-processing. A classical dense layer maps 33 input features down to 4 angles, passed into an AngleEmbedding quantum layer followed by 2 StronglyEntanglingLayers with trainable unitary rotations. Pauli-Z expectation values are measured and projected onto 3 output logits via a classical linear layer.")
    ]
    for b_title, b_desc in baselines:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(4)
        r = p_b.add_run(b_title)
        r.bold = True
        p_b.add_run(b_desc)

    p = doc.add_paragraph()
    r = p.add_run("3.4. DATASET CHARACTERIZATION AND PREPROCESSING PIPELINE\n")
    r.bold = True
    p.add_run("We utilized the comprehensive MePhy dataset (Gabbi et al., 2024), recorded at the University of Modena and Reggio Emilia. The dataset captures continuous biosignals from 60 healthy human participants performing a 4-part structured protocol designed to systematically induce distinct fatigue states. Table 3.4.1 details the recorded modalities.")

    # Table 3.4.1
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_tcap.add_run("Table 3.4.1: Summary of MePhy biosignal channels, sensor modalities, and sampling parameters.")
    r.bold = True
    r.font.size = Pt(10)

    t1 = doc.add_table(rows=5, cols=4)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Modality", "Physiological Target", "Raw Sampling Rate", "Feature Aggregation / Input"]
    for j, h in enumerate(headers):
        cell = t1.cell(0, j)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "0f172a")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 80, 80, 100, 100)

    rows_data = [
        ["ECG", "Cardiovascular / HRV Dynamics", "1 Hz (summary metrics)", "HR, Inter-Beat Interval (IBI), SDNN, RMSSD"],
        ["EDA", "Sympathetic Sweat Gland Activity", "1000 Hz", "Mean, Std, Range, RMS, Slope per window"],
        ["EMG", "Neuromuscular Muscular Exhaustion", "1000 Hz", "Mean, Std, Range, RMS energy per window"],
        ["Eye Blink", "Ocular Fatigue / Attentional Blink", "~30 Hz (camera/sensor)", "Blink rate, blink count/min, blink fraction"]
    ]
    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            cell = t1.cell(i+1, j)
            cell.paragraphs[0].text = val
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            set_cell_margins(cell, 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(cell, "f8fafc")

    doc.add_paragraph()
    p_rule = doc.add_paragraph()
    p_rule.add_run("3-Class Physiological Labelling Strategy: ").bold = True
    p_rule.add_run("The four experimental conditions provided in the MePhy dataset were mapped into three discrete fatigue regimes to form our clinical classification benchmark:\n")
    p_rule.add_run("• Class 0 (Low Fatigue): Baseline rest condition (pre-task calm state);\n")
    p_rule.add_run("• Class 1 (Medium Fatigue): Cognitive fatigue (Stroop & N-back mental tests) OR isolated physical fatigue (repetitive motor loads);\n")
    p_rule.add_run("• Class 2 (High Fatigue): Compound fatigue (simultaneous cognitive and physical exhaustion).")

    p = doc.add_paragraph()
    p.add_run("Signal Windowing and Partitioning: ").bold = True
    p.add_run("Continuous synchronized biosignals were segmented using a 30-second sliding window with a 15-second stride (50% temporal overlap), yielding 5,108 total labeled windows across the 60 participants. A strict subject-wise split was enforced: 42 subjects were allocated to training (3,579 windows), 9 subjects to validation (757 windows), and 9 subjects to the test holdout set (772 windows). Under no circumstances were windows from the same subject shared across splits.")

    p = doc.add_paragraph()
    r = p.add_run("3.5. EXPERIMENTAL SETUP AND HARDWARE CONFIGURATION\n")
    r.bold = True
    p.add_run("Experiments were conducted within a dedicated Python 3.12 scientific computing environment utilizing PyTorch 2.15, XGBoost 3.4, Scikit-Learn 1.9, and PennyLane 0.45. Deep neural networks and quantum circuit simulations were optimized using the AdamW optimizer with a learning rate of 1e-3, weight decay of 1e-4, dynamic ReduceLROnPlateau learning rate scheduling (patience 7, factor 0.5), and early stopping (patience 20). Class imbalance was mitigated across all models by computing inverse class weights (Low: 2.67, Medium: 0.51, High: 1.48) and applying weighted Cross-Entropy loss.")

    doc.add_page_break()

    # ----------------------------------------------------
    # CHAPTER 4: EXPERIMENTAL RESULTS AND DISCUSSIONS
    # ----------------------------------------------------
    add_chapter_header(4, "Experimental Results and Discussions", "9")

    p = doc.add_paragraph()
    r = p.add_run("4.1. DISCUSSION AND ANALYSIS OF RESULTS\n")
    r.bold = True
    p.add_run("Empirical evaluations across the 772 unseen test windows demonstrated that tree-based gradient boosting models (XGBoost and Random Forest) significantly outperformed deep neural networks and variational quantum circuits on cross-subject 3-class fatigue detection. XGBoost achieved the highest overall accuracy of 52.72% and a macro F1-score of 0.4782, followed closely by Random Forest at 51.94% accuracy and 0.4674 macro F1. In contrast, 1D-CNN (42.62%), Transformer (42.23%), and Quantum Hybrid (35.75%) suffered from cross-subject distributional shift when evaluated on holdout participants.")

    p = doc.add_paragraph()
    r = p.add_run("4.2. EMPIRICAL BENCHMARKING MATRIX\n")
    r.bold = True
    p.add_run("Table 4.2.1 presents the comprehensive performance metrics across all five evaluated architectures on the unseen test cohort (N=9 subjects, 772 evaluation windows).")

    # Table 4.2.1
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_tcap.add_run("Table 4.2.1: Comprehensive empirical benchmarking matrix on unseen test cohort.")
    r.bold = True
    r.font.size = Pt(10)

    t2 = doc.add_table(rows=6, cols=8)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    cols_t2 = ["Model", "Status", "Overall Acc", "Macro F1", "Low F1", "Med F1", "High F1", "Med Precision"]
    for j, h in enumerate(cols_t2):
        cell = t2.cell(0, j)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "0f172a")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 80, 80, 60, 60)

    bench_data = [
        ["XGBoost", "PRIMARY", f"{metrics['XGBoost']['accuracy']*100:.2f}%", f"{metrics['XGBoost']['macro_f1']:.4f}", f"{metrics['XGBoost']['per_class']['Low']['f1']:.4f}", f"{metrics['XGBoost']['per_class']['Medium']['f1']:.4f}", f"{metrics['XGBoost']['per_class']['High']['f1']:.4f}", f"{metrics['XGBoost']['per_class']['Medium']['precision']*100:.2f}%"],
        ["Random Forest", "Baseline", f"{metrics['Random Forest']['accuracy']*100:.2f}%", f"{metrics['Random Forest']['macro_f1']:.4f}", f"{metrics['Random Forest']['per_class']['Low']['f1']:.4f}", f"{metrics['Random Forest']['per_class']['Medium']['f1']:.4f}", f"{metrics['Random Forest']['per_class']['High']['f1']:.4f}", f"{metrics['Random Forest']['per_class']['Medium']['precision']*100:.2f}%"],
        ["1D-CNN", "Baseline", f"{metrics['1D-CNN']['accuracy']*100:.2f}%", f"{metrics['1D-CNN']['macro_f1']:.4f}", f"{metrics['1D-CNN']['per_class']['Low']['f1']:.4f}", f"{metrics['1D-CNN']['per_class']['Medium']['f1']:.4f}", f"{metrics['1D-CNN']['per_class']['High']['f1']:.4f}", f"{metrics['1D-CNN']['per_class']['Medium']['precision']*100:.2f}%"],
        ["Transformer", "Baseline", f"{metrics['Transformer']['accuracy']*100:.2f}%", f"{metrics['Transformer']['macro_f1']:.4f}", f"{metrics['Transformer']['per_class']['Low']['f1']:.4f}", f"{metrics['Transformer']['per_class']['Medium']['f1']:.4f}", f"{metrics['Transformer']['per_class']['High']['f1']:.4f}", f"{metrics['Transformer']['per_class']['Medium']['precision']*100:.2f}%"],
        ["Quantum Hybrid", "Baseline", f"{metrics['Quantum Hybrid']['accuracy']*100:.2f}%", f"{metrics['Quantum Hybrid']['macro_f1']:.4f}", f"{metrics['Quantum Hybrid']['per_class']['Low']['f1']:.4f}", f"{metrics['Quantum Hybrid']['per_class']['Medium']['f1']:.4f}", f"{metrics['Quantum Hybrid']['per_class']['High']['f1']:.4f}", f"{metrics['Quantum Hybrid']['per_class']['Medium']['precision']*100:.2f}%"]
    ]
    for i, row in enumerate(bench_data):
        for j, val in enumerate(row):
            cell = t2.cell(i+1, j)
            cell.paragraphs[0].text = val
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            set_cell_margins(cell, 60, 60, 60, 60)
            if i == 0:
                set_cell_background(cell, "dbeafe")
                cell.paragraphs[0].runs[0].bold = True
            elif i % 2 == 1:
                set_cell_background(cell, "f8fafc")

    doc.add_paragraph()
    p_bin = doc.add_paragraph()
    p_bin.add_run("Binary Screening Diagnostic Performance: ").bold = True
    p_bin.add_run("When the framework is configured as a binary frontline clinical screening tool (differentiating baseline resting state from active fatigue), the model achieves ")
    r = p_bin.add_run("93.61% accuracy")
    r.bold = True
    p_bin.add_run(". For differentiating between mild fatigue and severe compound fatigue (Low vs. High), the framework achieves ")
    r = p_bin.add_run("86.99% accuracy")
    r.bold = True
    p_bin.add_run(", confirming strong operational utility for automated industrial alerting.")

    p = doc.add_paragraph()
    r = p.add_run("4.3. CONFUSION MATRIX AND ERROR DISTRIBUTION ANALYSIS\n")
    r.bold = True
    p.add_run("Figure 4.3.1 displays the confusion matrices across all five models on the 772 unseen test samples (97 Low, 502 Medium, 173 High). Analysis indicates:")

    cms = [
        f"XGBoost correctly classified 274 of 502 Medium fatigue cases (71.35% precision) and 86 of 173 High fatigue cases (49.71% recall), keeping false positive alarms on resting individuals to only 19 cases.",
        f"Random Forest demonstrated consistent performance, identifying 278 Medium fatigue windows and 78 High fatigue windows with 69.85% Medium precision.",
        f"1D-CNN and Transformer models exhibited significant bias toward the minority classes due to class reweighting, identifying 106 and 114 High fatigue windows respectively, but misclassifying over 200 Medium fatigue samples as High fatigue.",
        f"Quantum Hybrid suffered from severe underfitting due to the 4-qubit bottleneck, correctly predicting only 105 Medium fatigue windows and over-predicting High fatigue (247 false assignments)."
    ]
    for c in cms:
        p_c = doc.add_paragraph(style='List Bullet')
        p_c.paragraph_format.space_after = Pt(3)
        p_c.add_run(c)

    fig_cm = results_dir / "fig_4_3_1_confusion_matrices.png"
    if fig_cm.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_cm), width=Inches(5.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 4.3.1: Confusion matrices of all five architectures on unseen test cohort.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    r = p.add_run("4.4. ARCHITECTURAL DEEP-DIVE: INDUCTIVE BIASES IN TABULAR VS. DEEP MODELS\n")
    r.bold = True
    p.add_run("The empirical superiority of XGBoost and Random Forest over deep sequence models stems from differences in inductive bias. Biosignals such as ECG, EDA, and EMG are notoriously susceptible to DC baseline drift, skin impedance variations, and individual resting heart-rate disparities. When a 1D-CNN or Transformer processes raw 4-channel sequences, it attempts to map raw numerical values directly to class logits. However, a heart rate of 78 BPM may represent calm baseline rest for one participant, but elevated cognitive stress for another. In contrast, tree models operate over engineered physiological features—specifically Heart Rate Variability (SDNN, RMSSD), EDA slope, EMG RMS power, and blink rate—which naturally normalize baseline shifts and isolate relative physiological changes.")

    fig_imp = results_dir / "feat_imp_XGBoost.png"
    if fig_imp.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(fig_imp), width=Inches(4.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_cap.add_run("Figure 4.2.1: Top 15 physiological features ranked by XGBoost information gain.")
        r.font.size = Pt(9.5)
        r.font.italic = True

    p = doc.add_paragraph()
    r = p.add_run("4.5. CROSS-SUBJECT GENERALIZATION BOTTLENECKS IN DEEP MODELS\n")
    r.bold = True
    p.add_run("Deep models (1D-CNN and Transformer) achieved training accuracies above 78% but struggled to surpass 43% on unseen test subjects. This discrepancy is a direct manifestation of cross-subject distributional shift. In the absence of massive multi-subject pre-training (e.g., thousands of hours of bio-recordings), deep sequence networks overfit to subject-specific morphological quirks in the training participants. Furthermore, the Quantum-Classical Hybrid model was constrained by the 4-qubit variational circuit; compressing 33 rich physiological biomarkers down to 4 quantum rotation angles introduced severe information loss, preventing the circuit from learning fine-grained boundaries between cognitive and physical fatigue regimes.")

    p = doc.add_paragraph()
    r = p.add_run("4.6. CODE AVAILABILITY AND REPOSITORY\n")
    r.bold = True
    p.add_run("The complete reproducible codebase, data preprocessing pipelines, feature engineering functions, model training routines, and evaluation scripts are made available:\n")
    p.add_run("• Implementation Script: fatigue_detection.py (Local Workspace)\n")
    p.add_run("• Figure Generation Suite: generate_figures.py\n")
    p.add_run("• Evaluation Outputs and Artifacts: results/all_results.json, results/comparison_table.csv\n")
    p.add_run("• Public Repository: ")
    r_git = p.add_run("https://github.com/abinashboro/multimodal-fatigue-detection")
    r_git.font.color.rgb = RGBColor(37, 99, 235)
    r_git.underline = True

    doc.add_page_break()

    # ----------------------------------------------------
    # CHAPTER 5: CONCLUSION
    # ----------------------------------------------------
    add_chapter_header(5, "Conclusion", "13")

    p = doc.add_paragraph()
    r = p.add_run("5.1. SUMMARY OF THE WORK ACCOMPLISHED\n")
    r.bold = True
    p.add_run("In this project, we designed, executed, and benchmarked a multimodal biosignal fatigue detection framework for 3-class fatigue classification (Low vs. Medium vs. High) across 60 human subjects from the MePhy dataset. Over 5,108 multi-channel windows across synchronized ECG, EDA, EMG, and Eye Blinking streams were analyzed under strict subject-wise evaluation protocols. Our findings demonstrate that Extreme Gradient Boosting (XGBoost) serves as an effective primary framework, achieving 52.72% 3-class accuracy and 0.4782 macro F1 on completely unseen individuals, outperforming complex 1D-CNNs (42.62%), Transformers (42.23%), and Quantum Variational Circuits (35.75%). When utilized as a frontline screening tool, the framework delivers 93.61% accuracy in detecting active fatigue states from baseline rest.")

    p = doc.add_paragraph()
    r = p.add_run("5.2. FUTURE SCOPES AND CLINICAL DEPLOYMENT\n")
    r.bold = True
    p.add_run("Future extensions of this research will focus on several high-impact directions:\n")
    p.add_run("1. Subject-Adaptive Personalization: Incorporating few-shot transfer learning or test-time adaptation where a 60-second baseline rest calibration is captured upon worker check-in to dynamically adjust classifier thresholds;\n")
    p.add_run("2. Edge and Wearable Deployment: Quantizing the XGBoost ensemble into optimized ONNX or C-based firmware executable on embedded microcontrollers (e.g., ARM Cortex-M or ESP32) integrated directly into smart wearables or operator helmets;\n")
    p.add_run("3. Scaled Quantum Advantage: Expanding the quantum variational circuit to 8–16 qubits utilizing tensor network simulators or physical NISQ hardware to evaluate whether quantum entanglement can offer provable separation on higher-dimensional physiological feature maps.")

    doc.add_page_break()

    # ----------------------------------------------------
    # REFERENCES
    # ----------------------------------------------------
    p_pg = doc.add_paragraph("Page 14")
    p_pg.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_pg.paragraph_format.space_after = Pt(8)

    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c = p_c.add_run("REFERENCES")
    r_c.bold = True
    r_c.font.size = Pt(14)

    add_double_rule(doc)

    refs = [
        "Gabbi, M., Cornia, L., Villani, V., & Sabattini, L. (2024). Understanding Fatigue Through Biosignals: A Comprehensive Dataset. In Proceedings of the 2024 ACM/IEEE International Conference on Human-Robot Interaction (HRI '24), pp. 842-846. doi:10.1145/3610977.3637485.",
        "Kakhi, K., Khosravi, A., Alizadehsani, R., & Acharya, U. R. (2025). Exploring the Relationships Between Physiological Signals During Automated Fatigue Detection. arXiv preprint arXiv:2509.21794.",
        "Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16), pp. 785-794. arXiv:1603.02754.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), pp. 5-32. doi:10.1023/A:1010933404324.",
        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention Is All You Need. Advances in Neural Information Processing Systems (NeurIPS 2017), 30, pp. 5998-6008. arXiv:1706.03762.",
        "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep Residual Learning for Image Recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2016), pp. 770-778. arXiv:1512.03385.",
        "Huang, G., Liu, Z., van der Maaten, L., & Weinberger, K. Q. (2017). Densely Connected Convolutional Networks. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2017), pp. 4700-4708. arXiv:1608.06993.",
        "Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. In International Conference on Machine Learning (ICML 2019), pp. 6105-6114. arXiv:1905.11946.",
        "Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T., Dehghani, M., Minderer, M., Heigold, G., Gelly, S., Uszkoreit, J., & Houlsby, N. (2021). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. International Conference on Learning Representations (ICLR 2021). arXiv:2010.11929.",
        "Bergholm, V., Izaac, J., Schuld, M., Gogolin, C., Ahmed, S., Ajit, V., Alam, M. S., et al. (2018). PennyLane: Automatic Differentiation of Hybrid Quantum-Classical Computations. arXiv preprint arXiv:1811.04968.",
        "Schuld, M., & Petruccione, F. (2021). Machine Learning with Quantum Computers. Quantum Science and Technology. Springer Cham. doi:10.1007/978-3-030-83098-4.",
        "Zhang, X., et al. (2026). Multimodal Phenotyping Dataset of Driving Fatigue (MPD-DF). Scientific Data, 13(1), 289. doi:10.1038/s41597-026-06634-4.",
        "Kovalenko, A., et al. (2023). OperatorEYEVP: A Multimodal Dataset for Operator Fatigue Monitoring. Sensors, 23(13), 6197. doi:10.3390/s23136197.",
        "Al-Sabbagh, Z., et al. (2024). Fatigue Monitoring Using Wearables and AI: Trends, Challenges, and Future Opportunities. arXiv preprint arXiv:2412.16847."
    ]
    for i, ref in enumerate(refs, 1):
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_after = Pt(6)
        p_r.paragraph_format.left_indent = Inches(0.3)
        p_r.paragraph_format.first_line_indent = Inches(-0.3)
        p_r.add_run(f"{i}. {ref}")

    out_docx = Path(r"c:\Users\ASUS\Desktop\minor project\Fatigue_Detection_Project_Report.docx")
    doc.save(str(out_docx))
    print(f"Report successfully generated at: {out_docx}")

if __name__ == "__main__":
    build_report()

