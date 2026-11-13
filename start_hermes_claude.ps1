# Запуск учителя Hermes на Claude Code: claude внутри папки Hermes/.
# Правила он берёт из Hermes/CLAUDE.md (персона под Клода), память — общая с версией на Gemini.
# Версия на Gemini запускается отдельно: .\start_hermes.ps1
Set-Location -Path (Join-Path $PSScriptRoot "Hermes")
claude @args
