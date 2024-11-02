/*
 * user_property.c
 */
#include <stdio.h>
#include <string.h>
#include "oniguruma.h"

extern int
main(int argc, char* argv[])
{
  int r;
  unsigned char *start, *range, *end;
  regex_t* reg;
  OnigErrorInfo einfo;
  OnigRegion *region;
  OnigEncoding use_encs[1];

  static OnigCodePoint handakuon_hiragana[] = {
    5, /* number of ranges */
    0x3071, 0x3071, /* PA */
    0x3074, 0x3074, /* PI */
    0x3077, 0x3077, /* PU */
    0x307a, 0x307a, /* PE */
    0x307d, 0x307d  /* PO */
  };

  static UChar* pattern = (UChar* )"\\A(\\p{HandakuonHiragana}{5})\\p{^HandakuonHiragana}\\z";
  //static UChar* pattern = (UChar* )"\\p{Handakuon_Hiragana}{5}\\P{Handakuon Hiragana}";

  /* "PA PI PU PE PO a" */
  static UChar* str = (UChar* )"\343\201\261\343\201\264\343\201\267\343\201\272\343\201\275a";

  use_encs[0] = ONIG_ENCODING_UTF8;
  onig_initialize(use_encs, sizeof(use_encs)/sizeof(use_encs[0]));

  r = onig_unicode_define_user_property("HandakuonHiragana", handakuon_hiragana);
  if (r == ONIG_NORMAL) {
    fprintf(stdout, "define HandakuonHiragana\n");
  }
  else {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r);
    fprintf(stderr, "ERROR: %s\n", s);
    onig_end();
    return -1;
  }

  r = onig_new(&reg, pattern, pattern + strlen((char* )pattern),
       ONIG_OPTION_DEFAULT, ONIG_ENCODING_UTF8, ONIG_SYNTAX_DEFAULT, &einfo);
  if (r == ONIG_NORMAL) {
    fprintf(stdout, "onig_new: success.\n");
  }
  else {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r, &einfo);
    fprintf(stderr, "onig_new: ERROR: %s\n", s);
    onig_end();
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
    fprintf(stderr, "ERROR: %s\n", s);
    onig_region_free(region, 1 /* 1:free self, 0:free contents only */);
    onig_free(reg);
    onig_end();
    return -1;
  }

  onig_region_free(region, 1 /* 1:free self, 0:free contents only */);
  onig_free(reg);
  onig_end();
  return 0;
}
