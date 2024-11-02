## Makefile.am for Oniguruma
lib_onig = ../src/libonig.la

AM_LDFLAGS  = -L$(libdir)
AM_CFLAGS = -Wall -Wno-invalid-source-encoding
AM_CPPFLAGS = -I$(top_srcdir)/src

if ENABLE_POSIX_API
TESTS = test_utf8 test_syntax test_options testc testp testcu test_regset test_back
else
TESTS = test_utf8 test_syntax test_options testc testcu test_regset test_back
endif

check_PROGRAMS = $(TESTS)

test: test_uchar test_regex_t $(TESTS)
	@echo "[Oniguruma API, UTF-8 check]"
	@./test_utf8  | grep RESULT
	@echo "[Oniguruma API, SYNTAX check]"
	@./test_syntax  | grep RESULT
	@echo "[Oniguruma API, Options check]"
	@./test_options  | grep RESULT
	@echo "[Oniguruma API, EUC-JP check]"
	@./testc  | grep RESULT
if ENABLE_POSIX_API
	@echo "[POSIX API, UTF-8 check]"
	@./testp  | grep RESULT
endif
	@echo "[Oniguruma API, UTF-16 check]"
	@./testcu | grep RESULT
	@echo ""
	@echo "[Oniguruma API, regset check]"
	@./test_regset
	@echo "[Oniguruma API, backward search check]"
	@./test_back  | grep RESULT

test_uchar:
	@echo "[UChar in oniguruma.h check]"
	@grep "\(^\|[^g]\)UChar" $(top_srcdir)/src/oniguruma.h
	@echo ""

test_regex_t:
	@echo "[regex_t in oniguruma.h check]"
	@grep "\(^\|[^[:alnum:]]\)regex_t" $(top_srcdir)/src/oniguruma.h
	@echo ""


test_utf8_SOURCES = test_utf8.c
test_utf8_LDADD = $(lib_onig)

test_syntax_SOURCES = test_syntax.c
test_syntax_LDADD = $(lib_onig)

test_options_SOURCES = test_options.c
test_options_LDADD = $(lib_onig)

testc_SOURCES = testc.c
testc_LDADD = $(lib_onig)

testp_SOURCES = testp.c
testp_LDADD = $(lib_onig)

testcu_SOURCES = testu.c
testcu_LDADD = $(lib_onig)

test_regset_SOURCES = test_regset.c
test_regset_LDADD = $(lib_onig)

test_back_SOURCES = test_back.c
test_back_LDADD = $(lib_onig)


gcov:
	make CFLAGS="--coverage" test_utf8
	make CFLAGS="--coverage" test_syntax
	make CFLAGS="--coverage" test_options
	make CFLAGS="--coverage" testc
if ENABLE_POSIX_API
	make CFLAGS="--coverage" testp
endif
	make CFLAGS="--coverage" testcu
	make CFLAGS="--coverage" test_regset
	make CFLAGS="--coverage" test_back
