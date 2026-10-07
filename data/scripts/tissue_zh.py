# -*- coding: utf-8 -*-
"""GTEx tissue English name → Chinese short label mapping for GenePage Gazette."""

from __future__ import annotations

# Prefer exact GTEx tissueSiteDetailId / display names.
TISSUE_ZH: dict[str, str] = {
    # Blood / immune / cells
    "Whole Blood": "全血",
    "Cells - EBV-transformed lymphocytes": "淋巴细胞",
    "Cells - Cultured fibroblasts": "成纤维细胞",
    "Spleen": "脾脏",
    "Bone Marrow": "骨髓",
    # Brain
    "Brain - Amygdala": "杏仁核",
    "Brain - Anterior cingulate cortex (BA24)": "前扣带皮层",
    "Brain - Caudate (basal ganglia)": "尾状核",
    "Brain - Cerebellar Hemisphere": "小脑半球",
    "Brain - Cerebellum": "小脑",
    "Brain - Cortex": "脑皮层",
    "Brain - Frontal Cortex (BA9)": "额叶皮层",
    "Brain - Hippocampus": "海马",
    "Brain - Hypothalamus": "下丘脑",
    "Brain - Nucleus accumbens (basal ganglia)": "伏隔核",
    "Brain - Putamen (basal ganglia)": "壳核",
    "Brain - Spinal cord (cervical c-1)": "脊髓",
    "Brain - Substantia nigra": "黑质",
    # Heart / vessel / muscle
    "Heart - Atrial Appendage": "心房",
    "Heart - Left Ventricle": "左心室",
    "Artery - Aorta": "主动脉",
    "Artery - Coronary": "冠状动脉",
    "Artery - Tibial": "胫动脉",
    "Muscle - Skeletal": "骨骼肌",
    # Lung / airway
    "Lung": "肺",
    # Digestive
    "Esophagus - Gastroesophageal Junction": "食管胃交界",
    "Esophagus - Mucosa": "食管黏膜",
    "Esophagus - Muscularis": "食管肌层",
    "Stomach": "胃",
    "Colon - Sigmoid": "乙状结肠",
    "Colon - Transverse": "横结肠",
    "Small Intestine - Terminal Ileum": "回肠末端",
    # Liver / pancreas / kidney / adrenal
    "Liver": "肝脏",
    "Pancreas": "胰腺",
    "Kidney - Cortex": "肾皮质",
    "Kidney - Medulla": "肾髓质",
    "Adrenal Gland": "肾上腺",
    # Skin / adipose / breast
    "Skin - Not Sun Exposed (Suprapubic)": "皮肤（非日照）",
    "Skin - Sun Exposed (Lower leg)": "皮肤（日照）",
    "Adipose - Subcutaneous": "皮下脂肪",
    "Adipose - Visceral (Omentum)": "内脏脂肪",
    "Breast - Mammary Tissue": "乳腺",
    # Reproductive / endocrine
    "Testis": "睾丸",
    "Ovary": "卵巢",
    "Uterus": "子宫",
    "Vagina": "阴道",
    "Prostate": "前列腺",
    "Cervix - Ectocervix": "宫颈外口",
    "Cervix - Endocervix": "宫颈内口",
    "Fallopian Tube": "输卵管",
    "Thyroid": "甲状腺",
    "Pituitary": "垂体",
    # Minor salivary
    "Minor Salivary Gland": "小唾液腺",
    "Bladder": "膀胱",
    "Nerve - Tibial": "胫神经",
}

# Extra aliases sometimes returned by API (tissueSiteDetailId style)
_ALIASES: dict[str, str] = {
    "Cells_EBV-transformed_lymphocytes": "Cells - EBV-transformed lymphocytes",
    "Cells_Cultured_fibroblasts": "Cells - Cultured fibroblasts",
    "Whole_Blood": "Whole Blood",
    "Skin_Sun_Exposed_Lower_leg": "Skin - Sun Exposed (Lower leg)",
    "Skin_Not_Sun_Exposed_Suprapubic": "Skin - Not Sun Exposed (Suprapubic)",
    "Breast_Mammary_Tissue": "Breast - Mammary Tissue",
    "Colon_Transverse": "Colon - Transverse",
    "Colon_Sigmoid": "Colon - Sigmoid",
    "Esophagus_Mucosa": "Esophagus - Mucosa",
    "Esophagus_Muscularis": "Esophagus - Muscularis",
    "Esophagus_Gastroesophageal_Junction": "Esophagus - Gastroesophageal Junction",
    "Small_Intestine_Terminal_Ileum": "Small Intestine - Terminal Ileum",
    "Kidney_Cortex": "Kidney - Cortex",
    "Kidney_Medulla": "Kidney - Medulla",
    "Adipose_Subcutaneous": "Adipose - Subcutaneous",
    "Adipose_Visceral_Omentum": "Adipose - Visceral (Omentum)",
    "Heart_Atrial_Appendage": "Heart - Atrial Appendage",
    "Heart_Left_Ventricle": "Heart - Left Ventricle",
    "Muscle_Skeletal": "Muscle - Skeletal",
    "Artery_Aorta": "Artery - Aorta",
    "Artery_Coronary": "Artery - Coronary",
    "Artery_Tibial": "Artery - Tibial",
    "Nerve_Tibial": "Nerve - Tibial",
    "Brain_Cortex": "Brain - Cortex",
    "Brain_Cerebellum": "Brain - Cerebellum",
    "Brain_Cerebellar_Hemisphere": "Brain - Cerebellar Hemisphere",
    "Brain_Frontal_Cortex_BA9": "Brain - Frontal Cortex (BA9)",
    "Brain_Hippocampus": "Brain - Hippocampus",
    "Brain_Hypothalamus": "Brain - Hypothalamus",
    "Brain_Amygdala": "Brain - Amygdala",
    "Brain_Spinal_cord_cervical_c-1": "Brain - Spinal cord (cervical c-1)",
    "Brain_Substantia_nigra": "Brain - Substantia nigra",
    "Minor_Salivary_Gland": "Minor Salivary Gland",
    "Adrenal_Gland": "Adrenal Gland",
    "Bone_Marrow": "Bone Marrow",
    "Cervix_Ectocervix": "Cervix - Ectocervix",
    "Cervix_Endocervix": "Cervix - Endocervix",
    "Fallopian_Tube": "Fallopian Tube",
    "Brain_Anterior_cingulate_cortex_BA24": "Brain - Anterior cingulate cortex (BA24)",
    "Brain_Caudate_basal_ganglia": "Brain - Caudate (basal ganglia)",
    "Brain_Nucleus_accumbens_basal_ganglia": "Brain - Nucleus accumbens (basal ganglia)",
    "Brain_Putamen_basal_ganglia": "Brain - Putamen (basal ganglia)",
}



def normalize_tissue_name(name: str) -> str:
    """Map tissueSiteDetailId-style ids to GTEx display names when possible."""
    if not name:
        return name
    if name in TISSUE_ZH:
        return name
    if name in _ALIASES:
        return _ALIASES[name]
    # underscore → spaced GTEx-ish guess
    spaced = name.replace("_", " ")
    if spaced in TISSUE_ZH:
        return spaced
    # Underscore id with organ_detail → "Organ - Detail" (common GTEx pattern)
    if "_" in name and " - " not in name:
        parts = name.split("_", 1)
        dashed = f"{parts[0]} - {parts[1].replace('_', ' ')}"
        if dashed in TISSUE_ZH:
            return dashed
        if dashed in _ALIASES.values():
            return dashed
    return name


def tissue_name_zh(name: str) -> str:
    """Return short Chinese label (≤8 chars preferred); fall back to truncated EN."""
    canon = normalize_tissue_name(name)
    if canon in TISSUE_ZH:
        return TISSUE_ZH[canon]
    # heuristic short label
    short = canon.split(" - ")[0].strip() if " - " in canon else canon
    return short[:8] if len(short) > 8 else short


def short_zh_for_headline(name: str) -> str:
    """Headline top_tissue.value: short Chinese ≤8 characters."""
    zh = tissue_name_zh(name)
    return zh if len(zh) <= 8 else zh[:8]
