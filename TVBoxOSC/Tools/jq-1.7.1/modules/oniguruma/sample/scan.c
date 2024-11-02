/*
 * scan.c
 */
#include <stdio.h>
#include <stdlib.h>
#include "oniguruma.h"

static int
scan_callback(int n, int r, OnigRegion* region, void* arg)
{
  int i;

  fprintf(stdout, "scan: %d\n", n);

  fprintf(stdout, "match at %d\n", r);
  for (i = 0; i < region->num_regs; i++) {
    fprintf(stdout, "%d: (%d-%d)\n", i, region->beg[i], region->end[i]);
  }

  return 0;
}

static int
scan(regex_t* reg, OnigOptionType options, unsigned char* str, unsigned char* end)
{
  int r;
  OnigRegion *region;

  region = onig_region_new();

  r = onig_scan(reg, str, end, region, options, scan_callback, NULL);
  if (r >= 0) {
    fprintf(stdout, "total: %d match\n", r);
  }
  else { /* error */
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((OnigUChar* )s, r);
    fprintf(stderr, "ERROR: %s\n", s);
    onig_region_free(region, 1 /* 1:free self, 0:free contents only */);
    return -1;
  }

  onig_region_free(region, 1 /* 1:free self, 0:free contents only */);
  return 0;
}

static int
exec(OnigEncoding enc, OnigOptionType options, OnigOptionType runtime_options, char* apattern, char* astr)
{
  int r;
  unsigned char *end;
  regex_t* reg;
  OnigErrorInfo einfo;
  UChar* pattern_end;
  UChar* pattern = (UChar* )apattern;
  UChar* str     = (UChar* )astr;

  onig_initialize(&enc, 1);

  pattern_end = pattern + onigenc_str_bytelen_null(enc, pattern);

  r = onig_new(&reg, pattern, pattern_end, options, enc, ONIG_SYNTAX_DEFAULT, &einfo);
  if (r != ONIG_NORMAL) {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((OnigUChar* )s, r, &einfo);
    fprintf(stderr, "ERROR: %s\n", s);
    onig_end();
    return -1;
  }

  end = str + onigenc_str_bytelen_null(enc, str);
  r = scan(reg, runtime_options, str, end);

  onig_free(reg);
  onig_end();
  return 0;
}


extern int main(int argc, char* argv[])
{
  exec(ONIG_ENCODING_UTF8, ONIG_OPTION_NONE, ONIG_OPTION_NONE,
       "\\Ga+\\s*", "a aa aaa baaa");
  fprintf(stdout, "\n");

  exec(ONIG_ENCODING_UTF8, ONIG_OPTION_NONE, ONIG_OPTION_NOT_BEGIN_POSITION,
       "\\Ga+\\s*", "a aa aaa baaa");
  fprintf(stdout, "\n");

  exec(ONIG_ENCODING_UTF8, ONIG_OPTION_NONE, ONIG_OPTION_NONE,
       "(?!\\G)a+\\s*", "a aa aaa baaa");
  fprintf(stdout, "\n");

  exec(ONIG_ENCODING_UTF8, ONIG_OPTION_NONE, ONIG_OPTION_NOT_BEGIN_POSITION,
       "(?!\\G)a+\\s*", "a aa aaa baaa");
  fprintf(stdout, "\n");

  exec(ONIG_ENCODING_UTF8, ONIG_OPTION_NONE, ONIG_OPTION_NONE,
       "a+\\s*", "a aa aaa baaa");

  return 0;
}
