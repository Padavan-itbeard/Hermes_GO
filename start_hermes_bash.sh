#!/usr/bin/env bash
# Запуск учителя Hermes с выбором уровня мышления и режима Remote Control

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

# Укажите вашу базовую версию Flash (например, gemini-3.8-flash или gemini-3.7-flash)
BASE_MODEL="gemini-3.8-flash"

echo "Выберите уровень мышления ($BASE_MODEL):"
echo "  1) low"
echo "  2) medium (по умолчанию)"
echo "  3) high"
echo "  4) default (не передавать флаг модели вообще)"
read -r -p "Ваш выбор [1-4, Enter = medium]: " choice

case "${choice}" in
  1|low|l)
    model_arg=(--model "${BASE_MODEL}-low")
    ;;
  2|medium|med|m|"")
    model_arg=(--model "${BASE_MODEL}-medium")
    ;;
  3|high|h)
    model_arg=(--model "${BASE_MODEL}-high")
    ;;
  4|default|d)
    model_arg=()
    ;;
  *)
    echo "Неизвестный вариант '$choice', используем medium."
    model_arg=(--model "${BASE_MODEL}-medium")
    ;;
esac

echo ""
echo "Режим запуска:"
echo "  1) С Remote Control — консоль + веб-интерфейс (по умолчанию)"
echo "  2) Только локальная консоль (без Remote Control)"
read -r -p "Ваш выбор [1-2, Enter = с Remote Control]: " rc_choice

case "${rc_choice}" in
  2|no|n|local)
    rc_arg=()
    ;;
  1|yes|y|rc|"")
    rc_arg=(--remote-control)
    ;;
  *)
    echo "Неизвестный вариант '$rc_choice', включаем Remote Control."
    rc_arg=(--remote-control)
    ;;
esac

echo "Запуск agy ${model_arg[*]} ${rc_arg[*]} --dangerously-skip-permissions..."
agy "${model_arg[@]}" "${rc_arg[@]}" --dangerously-skip-permissions "$@"
