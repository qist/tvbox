#!/bin/sh

echo "[Oniguruma API, UTF-8 check]"
./test_utf8  | grep RESULT
echo "[Oniguruma API, SYNTAX check]"
./test_syntax  | grep RESULT
echo "[Oniguruma API, Options check]"
./test_options  | grep RESULT
echo "[Oniguruma API, EUC-JP check]"
./testc  | grep RESULT
echo "[Oniguruma API, UTF-16 check]"
./testcu | grep RESULT
echo ""
echo "[Oniguruma API, regset check]"
./test_regset
echo "[Oniguruma API, backward search check]"
./test_back  | grep RESULT
