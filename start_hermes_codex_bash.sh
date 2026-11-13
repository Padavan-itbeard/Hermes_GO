#!/usr/bin/env bash
# Запуск Гермеса на Codex CLI с выбором модели и уровня рассуждений.
# Персона — в Hermes/AGENTS.override.md (Codex читает его вместо AGENTS.md), правила общие с Клодом.
# Другие движки: ./start_hermes_bash.sh (agy), ./start_hermes_claude_bash.sh (Claude Code)

cd "$(dirname "$0")/Hermes" || exit 1

# В правилах интерпретатор называется `python`, а на macOS и Linux он часто только `python3`.
# Если `python` нет, на время этой сессии подставляем обёртку, чтобы команды учителя работали как написаны.
if ! command -v python >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  shim="${TMPDIR:-/tmp}/hermes-python-shim"
  mkdir -p "$shim" && printf '#!/bin/sh
exec python3 "$@"
' > "$shim/python" && chmod +x "$shim/python"
  PATH="$shim:$PATH"; export PATH
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex не найден в PATH. Поставить: npm i -g @openai/codex"
  exit 1
fi

echo "Модель:"
echo "  1) из настроек Codex — не передавать флаг (по умолчанию)"
echo "  2) своя — ввести имя модели"
read -r -p "Ваш выбор [1-2, Enter = из настроек]: " m

case "$m" in
  2)
    read -r -p "Имя модели: " model_name
    if [ -n "$model_name" ]; then model_arg=(--model "$model_name"); else model_arg=(); fi
    ;;
  *) model_arg=() ;;
esac

echo ""
echo "Уровень рассуждений (сколько агент думает перед ответом):"
echo "  1) low     — быстрые ответы (по умолчанию)"
echo "  2) medium  — заметно подробнее рассуждает"
echo "  3) high    — для тяжёлых тем, медленно"
echo "  4) из настроек — не передавать флаг"
read -r -p "Ваш выбор [1-4, Enter = low]: " e

case "${e}" in
  2|medium|med) effort_arg=(--config model_reasoning_effort=medium) ;;
  3|high|h) effort_arg=(--config model_reasoning_effort=high) ;;
  4|default|d) effort_arg=() ;;
  *) effort_arg=(--config model_reasoning_effort=low) ;;
esac

echo ""
echo "Режим запуска:"
echo "  1) Без песочницы (--yolo) — рекомендуется, по умолчанию"
echo "     Отключает песочницу и подтверждения команд: иначе /end не сможет сделать push, а Ivy — открыть карточки."
echo "  2) С текущими настройками Codex"
read -r -p "Ваш выбор [1-2, Enter = 1]: " mode_choice

case "$mode_choice" in
  2) mode_arg=() ;;
  *) mode_arg=(--yolo) ;;
esac

echo "Запуск Гермеса: codex ${model_arg[*]} ${effort_arg[*]} ${mode_arg[*]}"
codex "${model_arg[@]}" "${effort_arg[@]}" "${mode_arg[@]}" "$@"
