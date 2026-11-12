# paddleocr-v6-tiny-onnx — lightonai/fc-amf-ocr (train)

**Date:** 2026-11-12T14:19:36+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [lightonai/fc-amf-ocr](https://huggingface.co/datasets/lightonai/fc-amf-ocr) · revision `036bd28ba275`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_tiny_det, rec_model=PP-OCRv6_tiny_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.7224 |
| wer | 0.3980 |

## Speed and energy

| | |
|---|---|
| Inference mean | 1.066s |
| Inference p50 / p90 / p95 / p99 | 0.983s / 1.695s / 2.094s / 3.398s |
| Inference max | 5.236s |
| Seconds per megapixel | 0.532 |
| Energy | 0.005186 kWh |
| Emissions | 0.000313 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| 1-4MP | 998 | 1.058s | 2.076s |
| >=4MP | 2 | 4.809s | 5.194s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 9V74 80-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 163_2013_07_FC16303… | 339.000 | a | KPMG Rapport des commissaires aux comptes sur les comptes consolidés Richel Serres de Fra… |
| 163_2013_07_FC16303… | 150.273 | 2 3 € e 3 3 | w 2 pomEs Exercice clos le 31 mars 2013 Associé John Evans les documents adressés aux act… |
| pdf_323_2021_09_FC3… | 10.856 | a A a L L DLDDDIDDI a X L D D E a 00 L. D &00 0 D0 800 0 D - 9 D D e00 800 800 Q00 000 00… | of el Jo o7oq el e uēis pee eep‘s/} eI (se)xoq errts esn s uondo etpM - aeeno np srq ne a… |
| pdf_323_2022_07_FC3… | 5.945 | a € a (D D a - & 8 - E E o a a P 1 1 : 8 e N co 8 9 S 5 N 00 8 2 : 5 N a W S - E 2 8 B d … | les " résultats avant amortissements et provisions " sont obérés des moins-values liées à… |
| pdf_182_2022_04_FC1… | 4.594 | o o o o o o o o 0 o o O O o & d8 4 o o o a de & a 0 o o o b de  9 Bs o o o e 6 8 6 8 o 4 … | epuve,p y sequuop) (seęs\|ençoe 09000 609 LLL 8 96 0 0 0 0 0 0 1 3 8 00LO 0910 OLLO 0810 … |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `073dd3f351b3`
