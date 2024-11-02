/*
 * test_regset.c  --- test for regset API
 * Copyright (c) 2019  K.Kosako
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "oniguruma.h"

static int nsucc  = 0;
static int nfail  = 0;
static int nerror = 0;


static int
make_regset(int line_no, int n, char* pat[], OnigRegSet** rset, int error_no)
{
  int r;
  int i;
  OnigRegSet* set;
  regex_t* reg;
  OnigErrorInfo einfo;

  *rset = NULL;
  r = onig_regset_new(&set, 0, NULL);
  if (r != 0) return r;

  for (i = 0; i < n; i++) {
    r = onig_new(&reg, (UChar* )pat[i], (UChar* )(pat[i] + strlen(pat[i])),
                 ONIG_OPTION_DEFAULT, ONIG_ENCODING_UTF8, ONIG_SYNTAX_DEFAULT,
                 &einfo);
    if (r != 0) {
      char s[ONIG_MAX_ERROR_MESSAGE_LEN];

      if (error_no == 0) {
        onig_error_code_to_str((UChar* )s, r, &einfo);
        fprintf(stderr, "ERROR: %d: %s  /%s/\n", line_no, s, pat[i]);
        nerror++;
      }
      else {
        if (r == error_no) {
          fprintf(stdout, "OK(ERROR): %d: /%s/ %d\n", line_no, pat[i], r);
          nsucc++;
        }
        else {
          fprintf(stdout, "FAIL(ERROR): %d: /%s/ %d, %d\n",
                  line_no, pat[i], error_no, r);
          nfail++;
        }
      }
      onig_regset_free(set);
      return r;
    }

    r = onig_regset_add(set, reg);
    if (r != 0) {
      onig_regset_free(set);
      fprintf(stderr, "ERROR: %d: onig_regset_add(): /%s/\n", line_no, pat[i]);
      nerror++;
      return r;
    }
  }

  *rset = set;
  return 0;
}

static double
get_sec(clock_t start, clock_t end)
{
  double t;

  t = (double )(end - start) / CLOCKS_PER_SEC;
  return t;
}

/* use clock(), because clock_gettime() doesn't exist in Windows and old Unix. */

static int
time_test(int repeat, int n, char* ps[], char* s, char* end, double* rt_set, double* rt_reg)
{
  int r;
  int i;
  int match_pos;
  OnigRegSet* set;
  clock_t ts1, ts2;
  double t_set, t_reg;

  r = make_regset(0, n, ps, &set, 0);
  if (r != 0) return r;

  ts1 = clock();
  for (i = 0; i < repeat; i++) {
    r = onig_regset_search(set, (UChar* )s, (UChar* )end, (UChar* )s, (UChar* )end,
                           ONIG_REGSET_POSITION_LEAD, ONIG_OPTION_NONE, &match_pos);
    if (r < 0) {
      fprintf(stderr, "FAIL onig_regset_search(POSITION_LEAD): %d\n", r);
      onig_regset_free(set);
      return r;
    }
  }

  ts2 = clock();
  t_set = get_sec(ts1, ts2);

  ts1 = clock();
  for (i = 0; i < repeat; i++) {
    r = onig_regset_search(set, (UChar* )s, (UChar* )end, (UChar* )s, (UChar* )end,
                           ONIG_REGSET_REGEX_LEAD, ONIG_OPTION_NONE, &match_pos);
    if (r < 0) {
      fprintf(stderr, "FAIL onig_regset_search(REGEX_LEAD): %d\n", r);
      onig_regset_free(set);
      return r;
    }
  }

  ts2 = clock();
  t_reg = get_sec(ts1, ts2);

  onig_regset_free(set);

  *rt_set = t_set;
  *rt_reg = t_reg;
  return 0;
}

static void
fisher_yates_shuffle(int n, char* ps[], char* cps[])
{
#define GET_RAND(n)  (rand()%(n+1))
#define SWAP(a,b)    { char* tmp = a; a = b; b = tmp; }

  int i;

  for (i = 0; i < n; i++)
    cps[i] = ps[i];

  for (i = n - 1; i > 0; i--) {
    int x = GET_RAND(i);
    SWAP(cps[i], cps[x]);
  }
}

static void
time_compare(int n, char* ps[], char* s, char* end)
{
  int r;
  int i;
  int repeat;
  double t_set, t_reg;
  double total_set, total_reg;
  char** cps;

  cps = (char** )malloc(sizeof(char*) * n);
  if (cps == 0) return ;

  repeat = 100 / n;
  total_set = total_reg = 0.0;
  for (i = 0; i < n; i++) {
    fisher_yates_shuffle(n, ps, cps);
    r = time_test(repeat, n, cps, s, end, &t_set, &t_reg);
    if (r != 0) {
      free(cps);
      return ;
    }
    total_set += t_set;
    total_reg += t_reg;
  }

  free(cps);

  fprintf(stdout, "POS lead: %6.2lfmsec.  REG lead: %6.2lfmsec.\n",
          total_set * 1000.0, total_reg * 1000.0);
}


static OnigRegSetLead XX_LEAD = ONIG_REGSET_POSITION_LEAD;

static void
xx(int line_no, int n, char* ps[], char* s, int from, int to, int mem, int not, int error_no)
{
  int r;
  int match_pos;
  int match_index;
  OnigRegSet* set;
  char *end;

  r = make_regset(line_no, n, ps, &set, error_no);
  if (r != 0) return ;

  end = s + strlen(s);

  r = onig_regset_search(set, (UChar* )s, (UChar* )end, (UChar* )s, (UChar* )end,
                         XX_LEAD, ONIG_OPTION_NONE, &match_pos);
  if (r < 0) {
    if (r == ONIG_MISMATCH) {
      if (not) {
        fprintf(stdout, "OK(N): %d\n", line_no);
        nsucc++;
      }
      else {
        fprintf(stdout, "FAIL: %d\n", line_no);
        nfail++;
      }
    }
    else {
      if (error_no == 0) {
        char buf[ONIG_MAX_ERROR_MESSAGE_LEN];
        onig_error_code_to_str((UChar* )buf, r);
        fprintf(stderr, "ERROR: %d: %s\n", line_no, buf);
        nerror++;
      }
      else {
        if (r == error_no) {
          fprintf(stdout, "OK(ERROR): %d: %d\n", line_no, r);
          nsucc++;
        }
        else {
          fprintf(stdout, "FAIL ERROR NO: %d: %d, %d\n", line_no, error_no, r);
          nfail++;
        }
      }
    }
  }
  else {
    if (not) {
      fprintf(stdout, "FAIL(N): %d\n", line_no);
      nfail++;
    }
    else {
      OnigRegion* region;

      match_index = r;
      region = onig_regset_get_region(set, match_index);
      if (region == 0) {
        fprintf(stderr, "ERROR: %d: can't get region.\n", line_no);
        nerror++;
        onig_regset_free(set);
        return ;
      }

      if (region->beg[mem] == from && region->end[mem] == to) {
        fprintf(stdout, "OK: %d\n", line_no);
        nsucc++;
      }
      else {
        char buf[1000];
        int len;
        len = region->end[mem] - region->beg[mem];
        strncpy(buf, s + region->beg[mem], len);
        buf[len] = '\0';
        fprintf(stdout, "FAIL: %d: %d-%d : %d-%d (%s)\n", line_no,
                from, to, region->beg[mem], region->end[mem], buf);
        nfail++;
      }
    }
  }

  onig_regset_free(set);
}

static void
x2(int line_no, int n, char* ps[], char* s, int from, int to)
{
  xx(line_no, n, ps, s, from, to, 0, 0, 0);
}

static void
x3(int line_no, int n, char* ps[], char* s, int from, int to, int mem)
{
  xx(line_no, n, ps, s, from, to, mem, 0, 0);
}

static void
n(int line_no, int n, char* ps[], char* s)
{
  xx(line_no, n, ps, s, 0, 0, 0, 1, 0);
}

#define ASIZE(a)              sizeof(a)/sizeof(a[0])
#define X2(ps,s,from,to)      x2(__LINE__,ASIZE(ps),ps,s,from,to)
#define X3(ps,s,from,to,mem)  x3(__LINE__,ASIZE(ps),ps,s,from,to,mem)
#define N(ps,s)                n(__LINE__,ASIZE(ps),ps,s)
#define NZERO(s)               n(__LINE__,0,(char** )0,s)

#ifndef _WIN32

/* getdelim() doesn't exist in Windows */

static int
get_all_content_of_file(char* path, char** rs, char** rend)
{
  ssize_t len;
  size_t n;
  char* line;
  FILE* fp;

  fp = fopen(path, "r");
  if (fp == 0) return -1;

  n = 0;
  line = NULL;
  len = getdelim(&line, &n, EOF, fp);
  fclose(fp);
  if (len < 0) return -2;

  *rs   = line;
  *rend = line + len;
  return 0;
}
#endif


#define TEXT_PATH    "kofu-utf8.txt"

/* --- To get kofu.txt ---
   $ wget https://www.aozora.gr.jp/cards/000148/files/774_ruby_1640.zip
   $ unzip 774_ruby_1640.zip
   $ nkf -Lu -w8 kofu.txt > kofu-utf8.txt
     (convert encoding to utf-8 with BOM and line terminator to be Unix-form)
*/

static char* p1[] = {
  "abc",
  "(bca)",
  "(cab)"
};

static char* p2[] = {
  "小説",
  "9",
  "夏目漱石",
};

static char* p3[] = {
  "^いる。",
  "^校正",
  "^底本",
  "^　翌日",
};

static char* p4[] = {
  "《[^》]{5}》",
  "《[^》]{6}》",
  "《[^》]{7}》",
  "《[^》]{8}》",
  "《[^》]{9}》",
  "《[^》]{10}》",
  "《[^》]{11}》",
  "《[^》]{12}》",
  "《[^》]{13}》",
  "《[^》]{14}》",
  "《[^》]{15}》",
  "《[^》]{16}》",
  "《[^》]{17}》",
  "《[^》]{18}》",
  "《[^》]{19}》",
  "《[^》]{20}》",
};

static char* p5[] = {
  "小室圭",
  "bbbbbb",
  "ドナルド・トランプ",
  "筑摩書房",
  "松原",
  "aaaaaaaaa",
  "bbbbbbbbb",
  "ccccc",
  "ddddddddddd",
  "eee",
  "ffffffffffff",
  "gggggggggg",
  "hhhhhhhhhhhhhh",
  "iiiiiii",
};

static char* p6[] = {
  "^.{1000,}",
  "松原",
  "小室圭",
  "ドナルド・トランプ",
  "筑摩書房",
};

static char* p7[] = {
  "0+", "1+", "2+", "3+", "4+", "5+", "6+", "7+", "8+", "9+",
};

static char* p8[] = {"a", ".*"};

extern int
main(int argc, char* argv[])
{
#ifndef _WIN32
  int file_exist;
#endif
  int r;
  char *s, *end;
  OnigEncoding use_encs[1];

  use_encs[0] = ONIG_ENCODING_UTF8;
  onig_initialize(use_encs, sizeof(use_encs)/sizeof(use_encs[0]));

  srand(12345);

  XX_LEAD = ONIG_REGSET_POSITION_LEAD;

  NZERO(" abab bccab ca");
  X2(p1, " abab bccab ca", 8, 11);
  X3(p1, " abab bccab ca", 8, 11, 1);
  N(p2, " XXXX AAA 1223 012345678bbb");
  X2(p2, "0123456789", 9, 10);
  X2(p7, "abcde 555 qwert", 6, 9);
  X2(p8, "", 0, 0);

  XX_LEAD = ONIG_REGSET_REGEX_LEAD;

  NZERO(" abab bccab ca");
  X2(p1, " abab bccab ca", 8, 11);
  X3(p1, " abab bccab ca", 8, 11, 1);
  N(p2, " XXXX AAA 1223 012345678bbb");
  X2(p2, "0123456789", 9, 10);
  X2(p7, "abcde 555 qwert", 6, 9);

#ifndef _WIN32
  r = get_all_content_of_file(TEXT_PATH, &s, &end);
  if (r == 0) {
    fprintf(stdout, "FILE: %s, size: %d\n", TEXT_PATH, (int )(end - s));
    file_exist = 1;
  }
  else {
    fprintf(stdout, "Ignore %s\n", TEXT_PATH);
    file_exist = 0;
  }

  if (file_exist != 0) {
    X2(p2, s, 10, 22);
    X2(p3, s, 496079, 496088);
    X2(p4, s, 1294, 1315);
  }
#endif

  fprintf(stdout,
          "\nRESULT   SUCC: %4d,  FAIL: %d,  ERROR: %d      (by Oniguruma %s)\n",
          nsucc, nfail, nerror, onig_version());

#ifndef _WIN32
  if (file_exist != 0) {
    fprintf(stdout, "\n");
    time_compare(ASIZE(p2), p2, s, end);
    time_compare(ASIZE(p3), p3, s, end);
    time_compare(ASIZE(p4), p4, s, end);
    time_compare(ASIZE(p5), p5, s, end);
    time_compare(ASIZE(p6), p6, s, end);
    fprintf(stdout, "\n");
    free(s);
  }
#endif

  onig_end();

  return ((nfail == 0 && nerror == 0) ? 0 : -1);
}
