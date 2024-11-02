/*
 * callback_each_match.c
 */
#include <stdio.h>
#include <string.h>
#include "oniguruma.h"

static int
each_match_callback(const UChar* str, const UChar* end,
     const UChar* match_start, OnigRegion* region, void* user_data)
{
#if 1
  fprintf(stdout, "each_match_callback:\n");
  fprintf(stdout, "  match at:  %ld - %d: %p\n", match_start - str, region->end[0],
          user_data);
  fprintf(stdout, "  region[0]: %d - %d\n", region->beg[0], region->end[0]);
#else
  int i;
  i = region->beg[0];
  fputc('<', stdout);
  while (i < region->end[0]) {
    fputc((int )str[i], stdout);
    i++;
  }
  fputc('>', stdout);
#endif

#if 0
  /* terminate match/search if returns error code < 0 */
  return ONIG_ABORT;
#endif

  return ONIG_NORMAL;
}

static int
search(UChar* pattern, UChar* str, OnigOptionType options, OnigOptionType runtime_options)
{
  int r;
  unsigned char *start, *range, *end;
  regex_t* reg;
  OnigErrorInfo einfo;
  OnigRegion *region;
  OnigMatchParam* mp;
  void* user_data;

  r = onig_new(&reg, pattern, pattern + strlen((char* )pattern),
               options, ONIG_ENCODING_ASCII, ONIG_SYNTAX_DEFAULT, &einfo);
  if (r != ONIG_NORMAL) {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r, &einfo);
    fprintf(stderr, "ERROR: %s\n", s);
    return -1;
  }

  region = onig_region_new();

  end   = str + strlen((char* )str);
  start = str;
  range = end;
  mp = onig_new_match_param();
  if (mp == 0) return -2;

  user_data = (void* )0x1234;
  onig_set_callout_user_data_of_match_param(mp, user_data);

  r = onig_search_with_param(reg, str, end, start, range, region,
                             runtime_options, mp);
  onig_free_match_param(mp);
  if (r >= 0) {
    /* If ONIG_OPTION_CALLBACK_EACH_MATCH is used with
       ONIG_OPTION_FIND_LONGEST, it may also return positive value. */
    fprintf(stdout, "\nr: %d\n", r);
  }
  else if (r == ONIG_MISMATCH) {
    /* always return ONIG_MISMATCH if ONIG_OPTION_CALLBACK_EACH_MATCH */
    fprintf(stdout, "\n");
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

  return 0;
}

static int
match(UChar* pattern, UChar* str, UChar* at, OnigOptionType options, OnigOptionType runtime_options)
{
  int r;
  unsigned char *start, *range, *end;
  regex_t* reg;
  OnigErrorInfo einfo;
  OnigRegion *region;
  OnigMatchParam* mp;
  void* user_data;

  r = onig_new(&reg, pattern, pattern + strlen((char* )pattern),
               options, ONIG_ENCODING_ASCII, ONIG_SYNTAX_DEFAULT, &einfo);
  if (r != ONIG_NORMAL) {
    char s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str((UChar* )s, r, &einfo);
    fprintf(stderr, "ERROR: %s\n", s);
    return -1;
  }

  region = onig_region_new();

  end   = str + strlen((char* )str);
  start = str;
  range = end;
  mp = onig_new_match_param();
  if (mp == 0) return -2;

  user_data = (void* )0x1234;
  onig_set_callout_user_data_of_match_param(mp, user_data);

  r = onig_match_with_param(reg, str, end, at, region, runtime_options, mp);
  onig_free_match_param(mp);
  if (r >= 0) {
    /* If ONIG_OPTION_CALLBACK_EACH_MATCH is used with
       ONIG_OPTION_FIND_LONGEST, it may also return positive value. */
    fprintf(stdout, "\nr: %d\n", r);
  }
  else if (r == ONIG_MISMATCH) {
    /* always return ONIG_MISMATCH if ONIG_OPTION_CALLBACK_EACH_MATCH */
    fprintf(stdout, "\n");
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

  return 0;
}

extern int main(int argc, char* argv[])
{
  OnigEncoding use_encs[1];

  static UChar* pattern = (UChar* )"a(.*)\\Kb|[e-f]+";
  static UChar* str     = (UChar* )"zzzzafffb";

  use_encs[0] = ONIG_ENCODING_ASCII;
  onig_initialize(use_encs, sizeof(use_encs)/sizeof(use_encs[0]));
  onig_set_callback_each_match(each_match_callback);

  fprintf(stdout, "<search>\n");
  search(pattern, str, ONIG_OPTION_NONE, ONIG_OPTION_CALLBACK_EACH_MATCH);
  fprintf(stdout, "<search with FIND_LONGEST>\n");
  search(pattern, str, ONIG_OPTION_FIND_LONGEST, ONIG_OPTION_CALLBACK_EACH_MATCH);

  fprintf(stdout, "<match>\n");
  match(pattern, str, str + 5, ONIG_OPTION_NONE, ONIG_OPTION_CALLBACK_EACH_MATCH);

  onig_end();
  return 0;
}
