# paddleocr-v6-small-onnx — nielsr/funsd-layoutlmv3 (test)

**Date:** 2026-11-12T13:58:22+00:00  
**Status:** ✅ passed  
**Samples:** 50 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [nielsr/funsd-layoutlmv3](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) · revision `ccd2a77745b0`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_small_det, rec_model=PP-OCRv6_small_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4018 |
| wer | 0.5588 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.840s |
| Inference p50 / p90 / p95 / p99 | 0.797s / 1.261s / 1.433s / 1.701s |
| Inference max | 1.755s |
| Seconds per megapixel | 1.099 |
| Energy | 0.000156 kWh |
| Emissions | 0.000009 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 50 | 0.840s | 1.433s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 9V45 96-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 10 | 0.741 | COURT: Asbestos JUDGE: CASE FORM CASE NAME: LORILLARD ENTITIES DATE FILED DATE SERVED CAS… | CASE FORM CASE NAME: Donald D. Sellers and Robin J. Sellers v. Raybestos-Manhattan, et al… |
| 37 | 0.724 | Date: on BLEND CASTING RECASING MENIHOL Filters Cigarettes Maker Length Circumference Wei… | Date: 3/14/90 90-B-1 Sample No. 1194-90 Type of Cigarette 100 mm Filter Batch Size 47.5 l… |
| 9 | 0.721 | COURT: JUDGE: Asbestos CASE FORM CASE NAME: LORILLARD ENTITIES: DATE FILED: DATE SERVED: … | CASEFORM CASE NAME: Wanda G. Robinson and Carroll Robinson v. Raybestos-Manhattan, et al.… |
| 31 | 0.669 | TO: FROM: SUBJECT: X GEOGRAPHY REGION: DIVISION: FULL PARTIAL x FULL PARTIAL DISTRIBUTION… | 12/12/96 08:33 504 7348616 LORILLARD TOB →→→ NY0 1 001/004 TO: SUBMISSION DATE K. A. Sper… |
| 28 | 0.668 | From: To: CC: Circulation(#) 86075409 Tiers II, & IV Lynnette Stevens Kelli Scruggs Vince… | From: Lynnette Stevens To: Kelli Scruggs CC: Vincent Losito Don Kisling George Baroody S.… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `60efb44a794a`
