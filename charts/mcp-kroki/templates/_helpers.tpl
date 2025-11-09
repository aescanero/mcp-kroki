{{/*
Expand the name of the chart.
*/}}
{{- define "mcp-kroki.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "mcp-kroki.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "mcp-kroki.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mcp-kroki.labels" -}}
helm.sh/chart: {{ include "mcp-kroki.chart" . }}
{{ include "mcp-kroki.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mcp-kroki.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mcp-kroki.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "mcp-kroki.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "mcp-kroki.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Kroki service name
*/}}
{{- define "mcp-kroki.krokiServiceName" -}}
{{- printf "%s-kroki" (include "mcp-kroki.fullname" .) }}
{{- end }}

{{/*
Kroki URL
*/}}
{{- define "mcp-kroki.krokiUrl" -}}
{{- if .Values.kroki.enabled }}
{{- printf "http://%s:%d" (include "mcp-kroki.krokiServiceName" .) (int .Values.kroki.service.port) }}
{{- else }}
{{- .Values.config.krokiUrl }}
{{- end }}
{{- end }}
