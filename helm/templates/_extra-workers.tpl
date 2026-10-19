{{/*
Extra Celery workers (layout, table) deployed from the same image as `worker`, each on its own
queue. Their values (`.Values.layoutWorker`, `.Values.tableWorker`) are overrides merged on top
of `.Values.worker`, so only what differs (command/queue, env, resources, ...) has to be set.
Parameters (all helpers below):
- root: The root context.
- name: The component name (e.g. "layout-worker"), used to derive its labels and resource names.
- key: The component's key in `.Values` (e.g. "layoutWorker").
*/}}

{{/*
Merged values of an extra worker, rendered as YAML (use with `fromYaml`).
Note: sprig's merge ignores zero-value overrides (`false`, `0`, `""`), so a worker default that
is non-empty can't be reset to an empty value from here.
*/}}
{{- define "helper.extraWorker.values" -}}
{{- $overrides := deepCopy (index .root.Values .key) -}}
{{- mustMergeOverwrite (deepCopy .root.Values.worker) (omit $overrides "enabled") | toYaml -}}
{{- end -}}

{{- define "helper.extraWorker.configmap" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
{{- if or $c.envCm $root.Values.global.envCm -}}
kind: ConfigMap
apiVersion: v1
metadata:
  name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" .name)) | nindent 4 }}
data:
  {{- if $root.Values.global.envCm -}}
  {{- include "helper.env" $root.Values.global.envCm | indent 2 }}
  {{- end -}}
  {{- if $c.envCm -}}
  {{- include "helper.env" $c.envCm | indent 2 }}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "helper.extraWorker.secret" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
{{- if or $c.envSecret $root.Values.global.envSecret -}}
kind: Secret
apiVersion: v1
metadata:
  name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" .name)) | nindent 4 }}
data:
  {{- if $root.Values.global.envSecret -}}
  {{- include "helper.secret" $root.Values.global.envSecret | indent 2 }}
  {{- end -}}
  {{- if $c.envSecret -}}
  {{- include "helper.secret" $c.envSecret | indent 2 }}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "helper.extraWorker.pullsecret" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
{{- range $index, $value := $c.imagePullSecrets }}
{{- if and $value.create $value.username $value.password }}
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "helper.imagePullSecretName" (dict "root" $root "componentName" $.name "index" $index "value" $value) }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" $.name)) | nindent 4 }}
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: {{ template "helper.imagePullSecret" dict "username" $value.username "password" $value.password "email" $value.email "registry" $value.registry }}
{{- end }}
{{- end }}
{{- end -}}

{{- define "helper.extraWorker.deployment" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" .name)) | nindent 4 }}
spec:
  {{- if not $c.autoscaling.enabled }}
  replicas: {{ $c.replicaCount }}
  {{- end }}
  revisionHistoryLimit: {{ $c.revisionHistoryLimit | default 10 }}
  selector:
    matchLabels: {{- include "helper.selectorLabels" (dict "root" $root "componentName" .name) | nindent 6 }}
  strategy:
    type: {{ $c.strategy.type }}
    {{- if eq $c.strategy.type "RollingUpdate" }}
    rollingUpdate:
      maxUnavailable: {{ $c.strategy.rollingUpdate.maxUnavailable }}
      maxSurge: {{ $c.strategy.rollingUpdate.maxSurge }}
    {{- end }}
  template:
    {{- include "helper.component.podTemplate" (dict "root" $root "name" .name "component" $c) | nindent 4 }}
{{- end -}}

{{- define "helper.extraWorker.scaledobject" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
{{- $keda := $c.kedaAutoscaler -}}
{{- if $keda.enabled -}}
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" .name)) | nindent 4 }}
spec:
  scaleTargetRef:
    name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
    kind: Deployment
    apiVersion: apps/v1
  minReplicaCount: {{ $keda.minReplicaCount }}
  maxReplicaCount: {{ $keda.maxReplicaCount }}
  {{- if $keda.pollingInterval }}
  pollingInterval: {{ $keda.pollingInterval }}
  {{- end }}
  {{- if $keda.cooldownPeriod }}
  cooldownPeriod: {{ $keda.cooldownPeriod }}
  {{- end }}
  {{- if $keda.fallback }}
  fallback:
    failureThreshold: {{ $keda.fallback.failureThreshold }}
    replicas: {{ $keda.fallback.replicas }}
  {{- end }}
  {{- if $keda.behavior }}
  advanced:
    horizontalPodAutoscalerConfig:
      behavior: {{- toYaml $keda.behavior | nindent 8 }}
  {{- end }}
  triggers:
  - type: redis
    metricType: AverageValue
    metadata:
      address: {{ tpl $keda.redis.address $root | default (printf "%s-master.%s:6379" $root.Values.redis.fullnameOverride $root.Release.Namespace) | quote }}
      listName: {{ $keda.redis.listName | quote }}
      listLength: {{ $keda.redis.listLength | quote }}
      {{- if $keda.redis.password }}
      password: {{ $keda.redis.password | quote }}
      {{- end }}
    {{- if and $keda.redis.secretRef $keda.redis.secretKey }}
    authenticationRef:
      name: {{ $keda.redis.authenticationRef | default "ocr-worker" }}
    {{- end }}
{{- end -}}
{{- end -}}

{{- define "helper.extraWorker.pdb" -}}
{{- $root := .root -}}
{{- $c := include "helper.extraWorker.values" . | fromYaml -}}
{{- if $c.pdb.enabled -}}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ printf "%s-%s" (include "helper.fullname" $root) .name }}
  labels: {{- (include "helper.labels" (dict "root" $root "componentName" .name)) | nindent 4 }}
spec:
  {{- with $c.pdb.maxUnavailable }}
  maxUnavailable: {{ . }}
  {{- else }}
  minAvailable: {{ $c.pdb.minAvailable | default 0 }}
  {{- end }}
  selector:
    matchLabels: {{- include "helper.selectorLabels" (dict "root" $root "componentName" .name) | nindent 6 }}
{{- end -}}
{{- end -}}
