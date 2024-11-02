/*
 * echo.c
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "oniguruma.h"

static int
echo(OnigCalloutArgs* args, void* user_data)
{
  int r;
  OnigCalloutIn in;
  OnigType type;
  OnigValue val;
  FILE* fp;

  fp = stdout;

  in = onig_get_callout_in_by_callout_args(args);

  r = onig_get_arg_by_callout_args(args, 1, &type, &val);
  if (r != ONIG_NORMAL) return r;

  if (in == ONIG_CALLOUT_IN_PROGRESS) {
    if (val.c == '<')
      return ONIG_CALLOUT_SUCCESS;
  }
  else {
    if (val.c != 'X' && val.c != '<')
      return ONIG_CALLOUT_SUCCESS;
  }

  r = onig_get_arg_by_callout_args(args, 0, &type, &val);
  if (r != ONIG_NORMAL) return r;


  fprintf(fp, "%s %s\n",
          (in == ONIG_CALLOUT_IN_PROGRESS ? "=>" : "<="),
          val.s.start);
  fflush(fp);

  return ONIG_CALLOUT_SUCCESS;
}


static int
test(OnigEncoding enc, char* in_pattern, char* in_str)
{
  int r;
  unsigned char *start, *range, *end;
  regex_t* reg;
  OnigErrorInfo einfo;
  OnigRegion *region;
  UChar* pattern;
  UChar* str;

  pattern = (UChar* )in_pattern;
  str = (UChar* )in_str;

  r = onig_new(&reg, pattern, pattern + strlen((char* )pattern),
               ONIG_OPTION_DEFAULT, enc, ONIG_SYNTAX_DEFAULT, &einfo);
  if (r != ONIG_NORMAL) {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r, &einfo);
    fprintf(stderr, "COMPILE ERROR: %d: %s\n", r, s);
    return -1;
  }

  region = onig_region_new();

  end   = str + strlen((char* )str);
  start = str;
  range = end;
  r = onig_search(reg, str, end, start, range, region, ONIG_OPTION_NONE);
  if (r >= 0) {
    int i;

    fprintf(stderr, "match at %d\n", r);
    for (i = 0; i < region->num_regs; i++) {
      fprintf(stderr, "%d: (%d-%d)\n", i, region->beg[i], region->end[i]);
    }
  }
  else if (r == ONIG_MISMATCH) {
    fprintf(stderr, "search fail\n");
  }
  else { /* error */
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r);
    fprintf(stderr, "SEARCH ERROR: %d: %s\n", r, s);
  }

  onig_region_free(region, 1 /* 1:free self, 0:free contents only */);
  onig_free(reg);
  return r;
}

extern int main(int argc, char* argv[])
{
  int r;
  int id;
  UChar* name;
  OnigEncoding use_encs[1];
  OnigType arg_types[4];
  OnigValue opt_defaults[4];
  OnigEncoding enc;

  enc = ONIG_ENCODING_UTF8;
  use_encs[0] = enc;

  r = onig_initialize(use_encs, sizeof(use_encs)/sizeof(use_encs[0]));
  if (r != ONIG_NORMAL) return -1;

  name = (UChar* )"echo";
  arg_types[0] = ONIG_TYPE_STRING;
  arg_types[1] = ONIG_TYPE_CHAR;
  opt_defaults[0].s.start = (UChar* )"echo";
  opt_defaults[0].s.end   = opt_defaults[0].s.start +
                                strlen((char* )opt_defaults[0].s.start);
  opt_defaults[1].c = '>';

  id = onig_set_callout_of_name(enc, ONIG_CALLOUT_TYPE_SINGLE,
                                name, name + strlen((char* )name),
                                ONIG_CALLOUT_IN_BOTH, echo, 0,
                                2, arg_types, 2, opt_defaults);
  if (id < 0) {
    fprintf(stderr, "ERROR: fail to set callout of name: %s\n", name);
    return -1;
  }

  test(enc, "(?:(*echo{abc!!!})a|b)*", "abba");
  test(enc, "(?:(*echo{xyz,X})a|b)*", "abba");

  onig_end();
  return 0;
}
