# Запуск учителя Hermes: agy внутри папки Hermes/ с умеренным "мышлением".
# medium по замерам вдвое быстрее high без потери качества.
Set-Location -Path (Join-Path $PSScriptRoot "Hermes")
agy --effort medium @args
