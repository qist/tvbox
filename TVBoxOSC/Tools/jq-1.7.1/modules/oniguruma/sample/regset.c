/*
 * regset.c
 */
#include <stdio.h>
#include <string.h>
#include "oniguruma.h"

extern int main(int argc, char* argv[])
{
  int r;
  int i, n;
  int match_pos;
  unsigned char *start, *range, *end;
  OnigRegSet* set;
  OnigRegSetLead lead;
  regex_t* reg;
  OnigErrorInfo einfo;
  char ebuf[ONIG_MAX_ERROR_MESSAGE_LEN];
  OnigEncoding use_encs[1];

  static UChar* str = (UChar* )"aaaaaaaaaaaaaaaaaaaaaaca";

  static char* pat[] = {
    "a(.*)b|a(.)c",
    "^(abc)",
    "a(.....)c"
  };

  use_encs[0] = ONIG_ENCODING_UTF8;
  onig_initialize(use_encs, sizeof(use_encs)/sizeof(use_encs[0]));

  r = onig_regset_new(&set, 0, NULL);
  if (r != ONIG_NORMAL) {
    onig_error_code_to_str((UChar* )ebuf, r);
    fprintf(stderr, "ERROR: %s\n", ebuf);
    onig_end();
    return -1;
  }

  n = sizeof(pat) / sizeof(pat[0]);

  for (i = 0; i < n; i++) {
    r = onig_new(&reg, (UChar* )pat[i], (UChar* )(pat[i] + strlen(pat[i])),
                 ONIG_OPTION_DEFAULT, ONIG_ENCODING_UTF8, ONIG_SYNTAX_DEFAULT,
                 &einfo);
    if (r != ONIG_NORMAL) {
      onig_error_code_to_str((UChar* )ebuf, r, &einfo);
      fprintf(stderr, "ERROR: %s\n", ebuf);
      onig_regset_free(set);
      onig_end();
      return -1;
    }

    r = onig_regset_add(set, reg);
    if (r != ONIG_NORMAL) {
      onig_free(reg);
      onig_regset_free(set);
      onig_end();
      return -1;
    }
  }

  end   = str + strlen((char* )str);
  start = str;
  range = end;
  lead = ONIG_REGSET_POSITION_LEAD;
  //lead = ONIG_REGSET_PRIORITY_TO_REGEX_ORDER;
  r = onig_regset_search(set, str, end, start, range, lead, ONIG_OPTION_NONE,
                         &match_pos);
  if (r >= 0) {
    OnigRegion *region;

    fprintf(stderr, "match regex index: %d\n", r);
    fprintf(stderr, "match position: %d\n", match_pos);

    region = onig_regset_get_region(set, r);
    for (i = 0; i < region->num_regs; i++) {
      fprintf(stderr, "%d: (%d-%d)\n", i, region->beg[i], region->end[i]);
    }
  }
  else if (r == ONIG_MISMATCH) {
    fprintf(stderr, "search fail\n");
  }
  else { /* error */
    onig_error_code_to_str((UChar* )ebuf, r);
    fprintf(stderr, "ERROR: %s\n", ebuf);
    onig_regset_free(set);
    onig_end();
    return -1;
  }

  onig_regset_free(set);
  onig_end();
  return 0;
}
