# paddleocr-v5-mobile-onnx — nielsr/funsd-layoutlmv3 (test)

**Date:** 2026-11-12T13:59:08+00:00  
**Status:** ✅ passed  
**Samples:** 50 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [nielsr/funsd-layoutlmv3](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) · revision `ccd2a77745b0`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_mobile_det, rec_model=PP-OCRv5_mobile_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4160 |
| wer | 0.6167 |

## Speed and energy

| | |
|---|---|
| Inference mean | 1.681s |
| Inference p50 / p90 / p95 / p99 | 1.598s / 2.474s / 3.039s / 4.029s |
| Inference max | 4.225s |
| Seconds per megapixel | 2.200 |
| Energy | 0.005666 kWh |
| Emissions | 0.000319 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 50 | 1.681s | 3.039s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 7763 64-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 10 | 0.736 | COURT: Asbestos JUDGE: CASE FORM CASE NAME: LORILLARD ENTITIES DATE FILED DATE SERVED CAS… | CASE FORM CASE NAME: Donald D. Selers and Robin J. Sellers v. Raybestos-Manhattan, et al.… |
| 9 | 0.725 | COURT: JUDGE: Asbestos CASE FORM CASE NAME: LORILLARD ENTITIES: DATE FILED: DATE SERVED: … |  CASE FORM CASE NAME: Wanda G. Robinson and Carroll Robinson v. Raybestos-Manhattan, et a… |
| 37 | 0.725 | Date: on BLEND CASTING RECASING MENIHOL Filters Cigarettes Maker Length Circumference Wei… | Date: 3/14/90 90-B-1 Sanple No.1194-90 Type of Cigarette 1o0 mm Filter Batch Size 47.5 1b… |
| 28 | 0.676 | From: To: CC: Circulation(#) 86075409 Tiers II, & IV Lynnette Stevens Kelli Scruggs Vince… | From: Lynnette Stevens To: Kelli Scruggs CC: Vincent Losito Don Kisling George Baroody S.… |
| 31 | 0.655 | TO: FROM: SUBJECT: X GEOGRAPHY REGION: DIVISION: FULL PARTIAL x FULL PARTIAL DISTRIBUTION… | 12/12/96 08:33 504 7348616 LORILLARD TOB +→→NYO1 001/004 - TO: K.A.Sperrow SUBMISSION.DAT… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `d492a85cf464`
