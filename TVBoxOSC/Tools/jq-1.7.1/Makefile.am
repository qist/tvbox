## Makefile.am for Oniguruma

ACLOCAL_AMFLAGS = -I m4

SUBDIRS = src test sample

EXTRA_DIST = oniguruma.pc.in HISTORY README_japanese README.md \
	index.html index_ja.html make_win.bat \
	CMakeLists.txt oniguruma.pc.cmake.in cmake/Config.cmake.in \
	onig-config.cmake.in src/config.h.cmake.in \
	doc/API doc/API.ja doc/RE doc/RE.ja doc/FAQ doc/FAQ.ja \
	doc/CALLOUTS.BUILTIN doc/CALLOUTS.BUILTIN.ja \
	doc/CALLOUTS.API doc/CALLOUTS.API.ja \
	doc/SYNTAX.md doc/UNICODE_PROPERTIES \
	src/Makefile.windows src/config.h.windows.in \
	src/config.h.win32 src/config.h.win64 \
	test/test.sh test/CMakeLists.txt \
        windows/testc.c windows/CMakeLists.txt

bin_SCRIPTS = onig-config

onig-config: onig-config.in

do_subst = sed                                          \
      -e 's,[@]datadir[@],$(datadir),g'                 \
      -e 's,[@]datarootdir[@],$(datarootdir),g'         \
      -e 's,[@]PACKAGE_VERSION[@],$(PACKAGE_VERSION),g' \
      -e 's,[@]prefix[@],$(prefix),g'                   \
      -e 's,[@]exec_prefix[@],$(exec_prefix),g'         \
      -e 's,[@]libdir[@],$(libdir),g'                   \
      -e 's,[@]includedir[@],$(includedir),g'

oniguruma.pc: $(srcdir)/oniguruma.pc.in Makefile
	$(do_subst) < $(srcdir)/oniguruma.pc.in > $(@)

pkgconfigdir   = $(libdir)/pkgconfig
pkgconfig_DATA = oniguruma.pc
DISTCLEANFILES = oniguruma.pc

all-test:
	cd test; make test

archive:
	git archive --format=tar --prefix=oniguruma/ HEAD | gzip > ../oniguruma-archive.tar.gz

tar:
	cd ..; tar cvf oniguruma-`date +%Y%m%d`.tar oniguruma; gzip oniguruma-`date +%Y%m%d`.tar

debug:
	make clean
	./configure CFLAGS="-O0 -g"
	make

debug_out:
	make clean
	./configure CFLAGS="-O0 -g -DONIG_DEBUG_PARSE -DONIG_DEBUG_COMPILE"
	make

sanitize:
	make clean
	./configure CFLAGS="-O -g -fsanitize=address" LDFLAGS="-fsanitize=address"
	make
	make all-test

debug_out_sanitize:
	make clean
	./configure CFLAGS="-O0 -g -fsanitize=address -DONIG_DEBUG_PARSE -DONIG_DEBUG_COMPILE" LDFLAGS="-fsanitize=address"
	make

cov:
	make lcov-clear
	cd test; make CFLAGS="--coverage" test
	make lcov

gcov:
	make CFLAGS="--coverage"

lcov:
	lcov -c -d src/.libs -o coverage.info
	genhtml -o coverage coverage.info

lcov-clear:
	lcov -z -d .

cov-clean: clean
	rm -rf coverage coverage.info
	find . -name '*.gcno' | xargs rm -f
