#!/usr/bin/env bash
# Запуск Гермеса на Claude Code с выбором модели и уровня усилий.
# Персона под Клода — в Hermes/CLAUDE.md, память общая с версией на Gemini.
# Версия на Gemini запускается отдельно: ./start_hermes_bash.sh

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

echo "Модель:"
echo "  1) opus     — умнее, дороже по лимитам (по умолчанию)"
echo "  2) sonnet   — быстрее и экономнее, для простых тем"
echo "  3) из настроек — не передавать флаг"
read -r -p "Ваш выбор [1-3, Enter = opus]: " m

case "${m}" in
  2|sonnet|s) model_arg=(--model sonnet) ;;
  3|default|d) model_arg=() ;;
  *) model_arg=(--model opus) ;;
esac

echo ""
echo "Уровень усилий (сколько агент думает перед ответом):"
echo "  1) low     — быстрые ответы (по умолчанию)"
echo "  2) medium  — заметно подробнее рассуждает"
echo "  3) high    — для тяжёлых тем, медленно"
echo "  4) из настроек — не передавать флаг"
read -r -p "Ваш выбор [1-4, Enter = low]: " e

case "${e}" in
  2|medium|med) effort_arg=(--effort medium) ;;
  3|high|h) effort_arg=(--effort high) ;;
  4|default|d) effort_arg=() ;;
  *) effort_arg=(--effort low) ;;
esac

echo ""
echo "Запуск Гермеса: claude ${model_arg[*]} ${effort_arg[*]}"
claude "${model_arg[@]}" "${effort_arg[@]}" "$@"
