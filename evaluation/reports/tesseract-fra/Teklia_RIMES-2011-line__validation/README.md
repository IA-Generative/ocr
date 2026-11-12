# tesseract-fra — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T14:00:12+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `tesseract` lang=fra, psm=3, oem=1, threads=1

## Scores

| Metric | Value |
|---|---|
| cer | 0.6365 |
| wer | 1.1874 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.120s |
| Inference p50 / p90 / p95 / p99 | 0.122s / 0.153s / 0.164s / 0.184s |
| Inference max | 0.231s |
| Seconds per megapixel | 0.563 |
| Energy | 0.000395 kWh |
| Emissions | 0.000023 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.120s | 0.164s |

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
| 685 | 3.867 | quelques mois ? | vb dnle + pourtg-amue ma Ja ee Ale ailure à all que 4 âme nue A y à |
| 374 | 3.250 | DISTINGUEES. | Aeeors , VLEXPAESIN DE des lauTAnsns DSTIVGUEES |
| 676 | 1.656 | Madame, Monsieur, en l'assurance | or 2'odhmt de AO SRE de aome que de Pont, Plgaunn, Mars, on À ammense |
| 62 | 1.650 | 25430 Sancey Le Long | LL nc AE SE dé CR, js PR. à 2s 430 Sancey Re Feng |
| 95 | 1.250 | mariée depuis le 10/12/2006. | rs à Le } JAL\| 25,6. ARE RE ox ds À} \| \| |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `81734b015b89`
