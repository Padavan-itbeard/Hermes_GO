# Запуск учителя Hermes на Codex CLI: codex внутри папки Hermes/.
# Правила он берёт из Hermes/AGENTS.override.md — Codex читает этот файл вместо AGENTS.md,
# поэтому agy (GEMINI.md + AGENTS.md) и Claude Code (CLAUDE.md) не затронуты.
# Персона общая с Клодом: rules-claude/. Память общая у всех трёх движков.
# Другие движки: .\start_hermes.ps1 (agy), .\start_hermes_claude.ps1 (Claude Code)
# Нет codex в PATH: npm i -g @openai/codex
Set-Location -Path (Join-Path $PSScriptRoot "Hermes")
Write-Host "Режим запуска:"
Write-Host "  1) Без песочницы (--yolo) — рекомендуется, по умолчанию"
Write-Host "     Отключает песочницу и подтверждения команд."
Write-Host "  2) С текущими настройками Codex"
$modeChoice = Read-Host "Ваш выбор [1-2, Enter = 1]"
$modeArgs = @('--yolo')
if ($modeChoice -eq '2') {
    $modeArgs = @()
}
codex @modeArgs @args
