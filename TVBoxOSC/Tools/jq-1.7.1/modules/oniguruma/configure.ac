dnl Process this file with autoconf to produce a configure script.
AC_INIT(onig, 6.9.8)

AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([-Wno-portability])
AC_CONFIG_HEADERS([src/config.h])


AC_ARG_WITH([statistics],
  [AS_HELP_STRING([--with-statistics],
    [take matching time statistical data])],
  AS_VAR_APPEND([CFLAGS], [" -DONIG_DEBUG_STATISTICS"]))


dnl check for POSIX API
AC_ARG_ENABLE([posix-api],
  [AS_HELP_STRING([--enable-posix-api],
    [turn on to include POSIX API [default=no]])],
[\
case "${enableval}" in
 yes) enable_posix_api=yes ;;
 no)  enable_posix_api=no ;;
 *)   AC_MSG_ERROR(bad value for --enable-posix-api) ;;
esac],
enable_posix_api=no)

dnl check for Binary compatible POSIX API
AC_ARG_ENABLE([binary-compatible-posix-api],
  [AS_HELP_STRING([--enable-binary-compatible-posix-api],
    [turn on to Binary compatible POSIX API [default=no]])],
[\
case "${enableval}" in
 yes) enable_binary_compatible_posix_api=yes; enable_posix_api=yes ;;
 no)  enable_binary_compatible_posix_api=no ;;
 *)   AC_MSG_ERROR(bad value for --enable-binary-compatible-posix-api) ;;
esac],
enable_binary_compatible_posix_api=no)

AM_CONDITIONAL(ENABLE_BINARY_COMPATIBLE_POSIX_API, test x"${enable_binary_compatible_posix_api}" = xyes)
AM_CONDITIONAL(ENABLE_POSIX_API, test x"${enable_posix_api}" = xyes)


dnl check for CRNL_AS_LINE_TERMINATOR
AC_ARG_ENABLE([crnl-as-line-terminator],
  [AS_HELP_STRING([--enable-crnl-as-line-terminator],
    [deprecated])],
  [crnl_as_line_terminator=$enableval])
if test "${crnl_as_line_terminator}" = yes; then
  AC_DEFINE(USE_CRNL_AS_LINE_TERMINATOR,1,[Define if enable CR+NL as line terminator])
fi


dnl Checks for programs.
AC_PROG_CC
LT_INIT
LTVERSION="8:0:3"
AC_SUBST(LTVERSION)

AC_PROG_INSTALL
AC_PROG_MAKE_SET

dnl Checks for libraries.

dnl Checks for header files.
AC_CHECK_HEADERS(sys/time.h unistd.h sys/times.h)

dnl Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_SIZEOF([int])
AC_CHECK_SIZEOF([long])
AC_CHECK_SIZEOF([long long])
AC_CHECK_SIZEOF([void*])

dnl Checks for library functions.
AC_FUNC_ALLOCA

AC_CONFIG_FILES([Makefile src/Makefile test/Makefile sample/Makefile onig-config])
AC_CONFIG_COMMANDS([default],[chmod +x onig-config],[])

# for Issue #220
LIBONIG_DEF_FILE=
FIX_TO_LDFLAGS=
case $host_os in
  cygwin* | mingw* )
    if test X"$enable_shared" = Xyes; then
      LIBONIG_DEF_FILE=libonig.def
      FIX_TO_LDFLAGS="-no-undefined"
    fi
    ;;
esac

EXTRA_LIBONIG_LDFLAGS="$EXTRA_LIBONIG_LDFLAGS $FIX_TO_LDFLAGS"
AC_SUBST(EXTRA_LIBONIG_LDFLAGS)

AM_CONDITIONAL(USE_LIBONIG_DEF_FILE, test -n "${LIBONIG_DEF_FILE}")
AC_SUBST(LIBONIG_DEF_FILE)

AC_OUTPUT
