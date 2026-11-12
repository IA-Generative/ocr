# tesseract-fra — nielsr/funsd-layoutlmv3 (test)

**Date:** 2026-11-12T13:58:06+00:00  
**Status:** ✅ passed  
**Samples:** 50 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [nielsr/funsd-layoutlmv3](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) · revision `ccd2a77745b0`  
**Model:** `tesseract` lang=fra, psm=3, oem=1, threads=1

## Scores

| Metric | Value |
|---|---|
| cer | 0.4819 |
| wer | 0.7023 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.420s |
| Inference p50 / p90 / p95 / p99 | 0.395s / 0.628s / 0.748s / 0.828s |
| Inference max | 0.889s |
| Seconds per megapixel | 0.550 |
| Energy | 0.000069 kWh |
| Emissions | 0.000004 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 50 | 0.420s | 0.748s |

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
| 9 | 0.746 | COURT: JUDGE: Asbestos CASE FORM CASE NAME: LORILLARD ENTITIES: DATE FILED: DATE SERVED: … | CASE FORM Wanda G. Robinson and Carroll Robinson v. Raybestos-Manhattan, et al. CASE NAME… |
| 20 | 0.729 | 31 1818 22 15 24 19 15 209 32 151/15 81/9 138/9 140/13 117/9 118/8 166/15 115/13 163/11 D… | TO: S.P.ZOLOT REGION: DIVISION: SUBJECT: QLD GOLD - LIGHT BOX 199'S PROGRESS REPORT BEEN … |
| 3 | 0.723 | 17 cc: : From: Area: Region: 5 X Chains: Independents: 82251504 11/05/97 11: 03 813 384 0… | “A/08/07 11309 613 884 0669 LORILLARD TANPA \| GRBENSBOR @ooz/003 Retail Excel Progress R… |
| 44 | 0.722 | 10675 PROPOSAL FOR DATE TO ADDRESS CITY STATE Attn: ITEM: MATERIAL: ALUMINUM SIZE: GAUGE … | 10675 STOUT INDUSTRIES, INC. 6425 W. FLORISSANT AVE, ST LOUIS, MO: 63136 : (314) 385-2260… |
| 31 | 0.699 | TO: FROM: SUBJECT: X GEOGRAPHY REGION: DIVISION: FULL PARTIAL x FULL PARTIAL DISTRIBUTION… | 12712786 08:33 504 7348016 LORILLARD TOB @oo1/004 KA Sparron FROM: FSuietind oecCx] real]… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `373d4556b1de`
