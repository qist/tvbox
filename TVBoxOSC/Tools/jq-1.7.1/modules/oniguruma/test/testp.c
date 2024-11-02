/*
 * testp.c
 * Copyright (c) 2020-2021  K.Kosako
 */
#include <stdio.h>
#include <string.h>

#include "onigposix.h"

#define SLEN(s)  strlen(s)

static int nsucc  = 0;
static int nfail  = 0;
static int nerror = 0;

static FILE* err_file;

static void
xx(char* pattern, char* str, int from, int to, int mem, int not)
{
  int r;
  regex_t reg;
  char buf[200];
  regmatch_t pmatch[25];

  r = regcomp(&reg, pattern, REG_EXTENDED | REG_NEWLINE);
  if (r) {
    regerror(r, &reg, buf, sizeof(buf));
    fprintf(err_file, "ERROR: %s\n", buf);
    nerror++;
    return ;
  }

  r = regexec(&reg, str, reg.re_nsub + 1, pmatch, 0);
  if (r != 0 && r != REG_NOMATCH) {
    regerror(r, &reg, buf, sizeof(buf));
    fprintf(err_file, "ERROR: %s\n", buf);
    nerror++;
    return ;
  }

  if (r == REG_NOMATCH) {
    if (not) {
      fprintf(stdout, "OK(N): /%s/ '%s'\n", pattern, str);
      nsucc++;
    }
    else {
      fprintf(stdout, "FAIL: /%s/ '%s'\n", pattern, str);
      nfail++;
    }
  }
  else {
    if (not) {
      fprintf(stdout, "FAIL(N): /%s/ '%s'\n", pattern, str);
      nfail++;
    }
    else {
      if (pmatch[mem].rm_so == from && pmatch[mem].rm_eo == to) {
        fprintf(stdout, "OK: /%s/ '%s'\n", pattern, str);
        nsucc++;
      }
      else {
        fprintf(stdout, "FAIL: /%s/ '%s' %d-%d : %d-%d\n", pattern, str,
                from, to, pmatch[mem].rm_so, pmatch[mem].rm_eo);
        nfail++;
      }
    }
  }
  regfree(&reg);
}

static void x2(char* pattern, char* str, int from, int to)
{
  xx(pattern, str, from, to, 0, 0);
}

static void x3(char* pattern, char* str, int from, int to, int mem)
{
  xx(pattern, str, from, to, mem, 0);
}

static void n(char* pattern, char* str)
{
  xx(pattern, str, 0, 0, 0, 1);
}

extern int main(int argc, char* argv[])
{
  err_file = stdout;

  reg_set_encoding(REG_POSIX_ENCODING_UTF8);

  x2("", "", 0, 0);
  x2("^", "", 0, 0);
  x2("$", "", 0, 0);
  x2("\\G", "", 0, 0);
  x2("\\A", "", 0, 0);
  x2("\\Z", "", 0, 0);
  x2("\\z", "", 0, 0);
  x2("^$", "", 0, 0);
  x2("\\ca", "\001", 0, 1);
  x2("\\C-b", "\002", 0, 1);
  x2("\\c\\\\", "\034", 0, 1);
  x2("q[\\c\\\\]", "q\034", 0, 2);
  x2("", "a", 0, 0);
  x2("a", "a", 0, 1);
  x2("\\x61", "a", 0, 1);
  x2("aa", "aa", 0, 2);
  x2("aaa", "aaa", 0, 3);
  x2("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 0, 35);
  x2("ab", "ab", 0, 2);
  x2("b", "ab", 1, 2);
  x2("bc", "abc", 1, 3);
  x2("(?i:#RET#)", "#INS##RET#", 5, 10);
  x2("\\17", "\017", 0, 1);
  x2("\\x1f", "\x1f", 0, 1);
  x2("a(?#....\\\\JJJJ)b", "ab", 0, 2);
  x2("(?x)  G (o O(?-x)oO) g L", "GoOoOgLe", 0, 7);
  x2(".", "a", 0, 1);
  n(".", "");
  x2("..", "ab", 0, 2);
  x2("\\w", "e", 0, 1);
  n("\\W", "e");
  x2("\\s", " ", 0, 1);
  x2("\\S", "b", 0, 1);
  x2("\\d", "4", 0, 1);
  n("\\D", "4");
  x2("\\b", "z ", 0, 0);
  x2("\\b", " z", 1, 1);
  x2("\\B", "zz ", 1, 1);
  x2("\\B", "z ", 2, 2);
  x2("\\B", " z", 0, 0);
  x2("[ab]", "b", 0, 1);
  n("[ab]", "c");
  x2("[a-z]", "t", 0, 1);
  n("[^a]", "a");
  x2("[^a]", "\n", 0, 1);
  x2("[]]", "]", 0, 1);
  n("[^]]", "]");
  x2("[\\^]+", "0^^1", 1, 3);
  x2("[b-]", "b", 0, 1);
  x2("[b-]", "-", 0, 1);
  x2("[\\w]", "z", 0, 1);
  n("[\\w]", " ");
  x2("[\\W]", "b$", 1, 2);
  x2("[\\d]", "5", 0, 1);
  n("[\\d]", "e");
  x2("[\\D]", "t", 0, 1);
  n("[\\D]", "3");
  x2("[\\s]", " ", 0, 1);
  n("[\\s]", "a");
  x2("[\\S]", "b", 0, 1);
  n("[\\S]", " ");
  x2("[\\w\\d]", "2", 0, 1);
  n("[\\w\\d]", " ");
  x2("[[:upper:]]", "B", 0, 1);
  x2("[*[:xdigit:]+]", "+", 0, 1);
  x2("[*[:xdigit:]+]", "GHIKK-9+*", 6, 7);
  x2("[*[:xdigit:]+]", "-@^+", 3, 4);
  n("[[:upper]]", "A");
  x2("[[:upper]]", ":", 0, 1);
  x2("[\\044-\\047]", "\046", 0, 1);
  x2("[\\x5a-\\x5c]", "\x5b", 0, 1);
  x2("[\\x6A-\\x6D]", "\x6c", 0, 1);
  n("[\\x6A-\\x6D]", "\x6E");
  n("^[0-9A-F]+ 0+ UNDEF ", "75F 00000000 SECT14A notype ()    External    | _rb_apply");
  x2("[\\[]", "[", 0, 1);
  x2("[\\]]", "]", 0, 1);
  x2("[&]", "&", 0, 1);
  x2("[[ab]]", "b", 0, 1);
  x2("[[ab]c]", "c", 0, 1);
  n("[[^a]]", "a");
  n("[^[a]]", "a");
  x2("[[ab]&&bc]", "b", 0, 1);
  n("[[ab]&&bc]", "a");
  n("[[ab]&&bc]", "c");
  x2("[a-z&&b-y&&c-x]", "w", 0, 1);
  n("[^a-z&&b-y&&c-x]", "w");
  x2("[[^a&&a]&&a-z]", "b", 0, 1);
  n("[[^a&&a]&&a-z]", "a");
  x2("[[^a-z&&bcdef]&&[^c-g]]", "h", 0, 1);
  n("[[^a-z&&bcdef]&&[^c-g]]", "c");
  x2("[^[^abc]&&[^cde]]", "c", 0, 1);
  x2("[^[^abc]&&[^cde]]", "e", 0, 1);
  n("[^[^abc]&&[^cde]]", "f");
  x2("[a-&&-a]", "-", 0, 1);
  n("[a\\-&&\\-a]", "&");
  n("\\wabc", " abc");
  x2("a\\Wbc", "a bc", 0, 4);
  x2("a.b.c", "aabbc", 0, 5);
  x2(".\\wb\\W..c", "abb bcc", 0, 7);
  x2("\\s\\wzzz", " zzzz", 0, 5);
  x2("aa.b", "aabb", 0, 4);
  n(".a", "ab");
  x2(".a", "aa", 0, 2);
  x2("^a", "a", 0, 1);
  x2("^a$", "a", 0, 1);
  x2("^\\w$", "a", 0, 1);
  n("^\\w$", " ");
  x2("^\\wab$", "zab", 0, 3);
  x2("^\\wabcdef$", "zabcdef", 0, 7);
  x2("^\\w...def$", "zabcdef", 0, 7);
  x2("\\w\\w\\s\\Waaa\\d", "aa  aaa4", 0, 8);
  x2("\\A\\Z", "", 0, 0);
  x2("\\Axyz", "xyz", 0, 3);
  x2("xyz\\Z", "xyz", 0, 3);
  x2("xyz\\z", "xyz", 0, 3);
  x2("a\\Z", "a", 0, 1);
  x2("\\Gaz", "az", 0, 2);
  n("\\Gz", "bza");
  n("az\\G", "az");
  n("az\\A", "az");
  n("a\\Az", "az");
  x2("\\^\\$", "^$", 0, 2);
  x2("^x?y", "xy", 0, 2);
  x2("^(x?y)", "xy", 0, 2);
  x2("\\w", "_", 0, 1);
  n("\\W", "_");
  x2("(?=z)z", "z", 0, 1);
  n("(?=z).", "a");
  x2("(?!z)a", "a", 0, 1);
  n("(?!z)a", "z");
  x2("(?i:a)", "a", 0, 1);
  x2("(?i:a)", "A", 0, 1);
  x2("(?i:A)", "a", 0, 1);
  n("(?i:A)", "b");
  x2("(?i:[A-Z])", "a", 0, 1);
  x2("(?i:[f-m])", "H", 0, 1);
  x2("(?i:[f-m])", "h", 0, 1);
  n("(?i:[f-m])", "e");
  x2("(?i:[A-c])", "D", 0, 1);
  n("(?i:[^a-z])", "A");
  n("(?i:[^a-z])", "a");
  x2("(?i:[!-k])", "Z", 0, 1);
  x2("(?i:[!-k])", "7", 0, 1);
  x2("(?i:[T-}])", "b", 0, 1);
  x2("(?i:[T-}])", "{", 0, 1);
  x2("(?i:\\?a)", "?A", 0, 2);
  x2("(?i:\\*A)", "*a", 0, 2);
  n(".", "\n");
  x2("(?m:.)", "\n", 0, 1);
  x2("(?m:a.)", "a\n", 0, 2);
  x2("(?m:.b)", "a\nb", 1, 3);
  x2(".*abc", "dddabdd\nddabc", 8, 13);
  x2("(?m:.*abc)", "dddabddabc", 0, 10);
  n("(?i)(?-i)a", "A");
  n("(?i)(?-i:a)", "A");
  x2("a?", "", 0, 0);
  x2("a?", "b", 0, 0);
  x2("a?", "a", 0, 1);
  x2("a*", "", 0, 0);
  x2("a*", "a", 0, 1);
  x2("a*", "aaa", 0, 3);
  x2("a*", "baaaa", 0, 0);
  n("a+", "");
  x2("a+", "a", 0, 1);
  x2("a+", "aaaa", 0, 4);
  x2("a+", "aabbb", 0, 2);
  x2("a+", "baaaa", 1, 5);
  x2(".?", "", 0, 0);
  x2(".?", "f", 0, 1);
  x2(".?", "\n", 0, 0);
  x2(".*", "", 0, 0);
  x2(".*", "abcde", 0, 5);
  x2(".+", "z", 0, 1);
  x2(".+", "zdswer\n", 0, 6);
  x2("(.*)a\\1f", "babfbac", 0, 4);
  x2("(.*)a\\1f", "bacbabf", 3, 7);
  x2("((.*)a\\2f)", "bacbabf", 3, 7);
  x2("(.*)a\\1f", "baczzzzzz\nbazz\nzzzzbabf", 19, 23);
  x2("a|b", "a", 0, 1);
  x2("a|b", "b", 0, 1);
  x2("|a", "a", 0, 0);
  x2("(|a)", "a", 0, 0);
  x2("ab|bc", "ab", 0, 2);
  x2("ab|bc", "bc", 0, 2);
  x2("z(?:ab|bc)", "zbc", 0, 3);
  x2("a(?:ab|bc)c", "aabc", 0, 4);
  x2("ab|(?:ac|az)", "az", 0, 2);
  x2("a|b|c", "dc", 1, 2);
  x2("a|b|cd|efg|h|ijk|lmn|o|pq|rstuvwx|yz", "pqr", 0, 2);
  n("a|b|cd|efg|h|ijk|lmn|o|pq|rstuvwx|yz", "mn");
  x2("a|^z", "ba", 1, 2);
  x2("a|^z", "za", 0, 1);
  x2("a|\\Gz", "bza", 2, 3);
  x2("a|\\Gz", "za", 0, 1);
  x2("a|\\Az", "bza", 2, 3);
  x2("a|\\Az", "za", 0, 1);
  x2("a|b\\Z", "ba", 1, 2);
  x2("a|b\\Z", "b", 0, 1);
  x2("a|b\\z", "ba", 1, 2);
  x2("a|b\\z", "b", 0, 1);
  x2("\\w|\\s", " ", 0, 1);
  n("\\w|\\w", " ");
  x2("\\w|%", "%", 0, 1);
  x2("\\w|[&$]", "&", 0, 1);
  x2("[b-d]|[^e-z]", "a", 0, 1);
  x2("(?:a|[c-f])|bz", "dz", 0, 1);
  x2("(?:a|[c-f])|bz", "bz", 0, 2);
  x2("abc|(?=zz)..f", "zzf", 0, 3);
  x2("abc|(?!zz)..f", "abf", 0, 3);
  x2("(?=za)..a|(?=zz)..a", "zza", 0, 3);
  n("(?>a|abd)c", "abdc");
  x2("(?>abd|a)c", "abdc", 0, 4);
  x2("a?|b", "a", 0, 1);
  x2("a?|b", "b", 0, 0);
  x2("a?|b", "", 0, 0);
  x2("a*|b", "aa", 0, 2);
  x2("a*|b*", "ba", 0, 0);
  x2("a*|b*", "ab", 0, 1);
  x2("a+|b*", "", 0, 0);
  x2("a+|b*", "bbb", 0, 3);
  x2("a+|b*", "abbb", 0, 1);
  n("a+|b+", "");
  x2("(a|b)?", "b", 0, 1);
  x2("(a|b)*", "ba", 0, 2);
  x2("(a|b)+", "bab", 0, 3);
  x2("(ab|ca)+", "caabbc", 0, 4);
  x2("(ab|ca)+", "aabca", 1, 5);
  x2("(ab|ca)+", "abzca", 0, 2);
  x2("(a|bab)+", "ababa", 0, 5);
  x2("(a|bab)+", "ba", 1, 2);
  x2("(a|bab)+", "baaaba", 1, 4);
  x2("(?:a|b)(?:a|b)", "ab", 0, 2);
  x2("(?:a*|b*)(?:a*|b*)", "aaabbb", 0, 3);
  x2("(?:a*|b*)(?:a+|b+)", "aaabbb", 0, 6);
  x2("(?:a+|b+){2}", "aaabbb", 0, 6);
  x2("h{0,}", "hhhh", 0, 4);
  x2("(?:a+|b+){1,2}", "aaabbb", 0, 6);
  n("ax{2}*a", "0axxxa1");
  n("a.{0,2}a", "0aXXXa0");
  n("a.{0,2}?a", "0aXXXa0");
  n("a.{0,2}?a", "0aXXXXa0");
  x2("^a{2,}?a$", "aaa", 0, 3);
  x2("^[a-z]{2,}?$", "aaa", 0, 3);
  x2("(?:a+|\\Ab*)cc", "cc", 0, 2);
  n("(?:a+|\\Ab*)cc", "abcc");
  x2("(?:^a+|b+)*c", "aabbbabc", 6, 8);
  x2("(?:^a+|b+)*c", "aabbbbc", 0, 7);
  x2("a|(?i)c", "C", 0, 1);
  x2("(?i)c|a", "C", 0, 1);
  x2("(?i)c|a", "A", 0, 1);
  x2("(?i:c)|a", "C", 0, 1);
  n("(?i:c)|a", "A");
  x2("[abc]?", "abc", 0, 1);
  x2("[abc]*", "abc", 0, 3);
  x2("[^abc]*", "abc", 0, 0);
  n("[^abc]+", "abc");
  x2("a?\?", "aaa", 0, 0);
  x2("ba?\?b", "bab", 0, 3);
  x2("a*?", "aaa", 0, 0);
  x2("ba*?", "baa", 0, 1);
  x2("ba*?b", "baab", 0, 4);
  x2("a+?", "aaa", 0, 1);
  x2("ba+?", "baa", 0, 2);
  x2("ba+?b", "baab", 0, 4);
  x2("(?:a?)?\?", "a", 0, 0);
  x2("(?:a?\?)?", "a", 0, 0);
  x2("(?:a?)+?", "aaa", 0, 1);
  x2("(?:a+)?\?", "aaa", 0, 0);
  x2("(?:a+)?\?b", "aaab", 0, 4);
  x2("(?:ab)?{2}", "", 0, 0);
  x2("(?:ab)?{2}", "ababa", 0, 4);
  x2("(?:ab)*{0}", "ababa", 0, 0);
  x2("(?:ab){3,}", "abababab", 0, 8);
  n("(?:ab){3,}", "abab");
  x2("(?:ab){2,4}", "ababab", 0, 6);
  x2("(?:ab){2,4}", "ababababab", 0, 8);
  x2("(?:ab){2,4}?", "ababababab", 0, 4);
  x2("(?:ab){,}", "ab{,}", 0, 5);
  x2("(?:abc)+?{2}", "abcabcabc", 0, 6);
  x2("(?:X*)(?i:xa)", "XXXa", 0, 4);
  x2("(d+)([^abc]z)", "dddz", 0, 4);
  x2("([^abc]*)([^abc]z)", "dddz", 0, 4);
  x2("(\\w+)(\\wz)", "dddz", 0, 4);
  x3("(a)", "a", 0, 1, 1);
  x3("(ab)", "ab", 0, 2, 1);
  x2("((ab))", "ab", 0, 2);
  x3("((ab))", "ab", 0, 2, 1);
  x3("((ab))", "ab", 0, 2, 2);
  x3("((((((((((((((((((((ab))))))))))))))))))))", "ab", 0, 2, 20);
  x3("(ab)(cd)", "abcd", 0, 2, 1);
  x3("(ab)(cd)", "abcd", 2, 4, 2);
  x3("()(a)bc(def)ghijk", "abcdefghijk", 3, 6, 3);
  x3("(()(a)bc(def)ghijk)", "abcdefghijk", 3, 6, 4);
  x2("(^a)", "a", 0, 1);
  x3("(a)|(a)", "ba", 1, 2, 1);
  x3("(^a)|(a)", "ba", 1, 2, 2);
  x3("(a?)", "aaa", 0, 1, 1);
  x3("(a*)", "aaa", 0, 3, 1);
  x3("(a*)", "", 0, 0, 1);
  x3("(a+)", "aaaaaaa", 0, 7, 1);
  x3("(a+|b*)", "bbbaa", 0, 3, 1);
  x3("(a+|b?)", "bbbaa", 0, 1, 1);
  x3("(abc)?", "abc", 0, 3, 1);
  x3("(abc)*", "abc", 0, 3, 1);
  x3("(abc)+", "abc", 0, 3, 1);
  x3("(xyz|abc)+", "abc", 0, 3, 1);
  x3("([xyz][abc]|abc)+", "abc", 0, 3, 1);
  x3("((?i:abc))", "AbC", 0, 3, 1);
  x2("(abc)(?i:\\1)", "abcABC", 0, 6);
  x3("((?m:a.c))", "a\nc", 0, 3, 1);
  x3("((?=az)a)", "azb", 0, 1, 1);
  x3("abc|(.abd)", "zabd", 0, 4, 1);
  x2("(?:abc)|(ABC)", "abc", 0, 3);
  x3("(?i:(abc))|(zzz)", "ABC", 0, 3, 1);
  x3("a*(.)", "aaaaz", 4, 5, 1);
  x3("a*?(.)", "aaaaz", 0, 1, 1);
  x3("a*?(c)", "aaaac", 4, 5, 1);
  x3("[bcd]a*(.)", "caaaaz", 5, 6, 1);
  x3("(\\Abb)cc", "bbcc", 0, 2, 1);
  n("(\\Abb)cc", "zbbcc");
  x3("(^bb)cc", "bbcc", 0, 2, 1);
  n("(^bb)cc", "zbbcc");
  x3("cc(bb$)", "ccbb", 2, 4, 1);
  n("cc(bb$)", "ccbbb");
  n("(\\1)", "");
  n("\\1(a)", "aa");
  n("(a(b)\\1)\\2+", "ababb");
  n("(?:(?:\\1|z)(a))+$", "zaa");
  x2("(?:(?:\\1|z)(a))+$", "zaaa", 0, 4);
  x2("(a)(?=\\1)", "aa", 0, 1);
  n("(a)$|\\1", "az");
  x2("(a)\\1", "aa", 0, 2);
  n("(a)\\1", "ab");
  x2("(a?)\\1", "aa", 0, 2);
  x2("(a?\?)\\1", "aa", 0, 0);
  x2("(a*)\\1", "aaaaa", 0, 4);
  x3("(a*)\\1", "aaaaa", 0, 2, 1);
  x2("a(b*)\\1", "abbbb", 0, 5);
  x2("a(b*)\\1", "ab", 0, 1);
  x2("(a*)(b*)\\1\\2", "aaabbaaabb", 0, 10);
  x2("(a*)(b*)\\2", "aaabbbb", 0, 7);
  x2("(((((((a*)b))))))c\\7", "aaabcaaa", 0, 8);
  x3("(((((((a*)b))))))c\\7", "aaabcaaa", 0, 3, 7);
  x2("(a)(b)(c)\\2\\1\\3", "abcbac", 0, 6);
  x2("([a-d])\\1", "cc", 0, 2);
  x2("(\\w\\d\\s)\\1", "f5 f5 ", 0, 6);
  n("(\\w\\d\\s)\\1", "f5 f5");
  x2("(who|[a-c]{3})\\1", "whowho", 0, 6);
  x2("...(who|[a-c]{3})\\1", "abcwhowho", 0, 9);
  x2("(who|[a-c]{3})\\1", "cbccbc", 0, 6);
  x2("(^a)\\1", "aa", 0, 2);
  n("(^a)\\1", "baa");
  n("(a$)\\1", "aa");
  n("(ab\\Z)\\1", "ab");
  x2("(a*\\Z)\\1", "a", 1, 1);
  x2(".(a*\\Z)\\1", "ba", 1, 2);
  x3("(.(abc)\\2)", "zabcabc", 0, 7, 1);
  x3("(.(..\\d.)\\2)", "z12341234", 0, 9, 1);
  x2("((?i:az))\\1", "AzAz", 0, 4);
  n("((?i:az))\\1", "Azaz");
  x2("(?<=a)b", "ab", 1, 2);
  n("(?<=a)b", "bb");
  x2("(?<=a|b)b", "bb", 1, 2);
  x2("(?<=a|bc)b", "bcb", 2, 3);
  x2("(?<=a|bc)b", "ab", 1, 2);
  x2("(?<=a|bc||defghij|klmnopq|r)z", "rz", 1, 2);
  x2("(a)\\g<1>", "aa", 0, 2);
  x2("(?<!a)b", "cb", 1, 2);
  n("(?<!a)b", "ab");
  x2("(?<!a|bc)b", "bbb", 0, 1);
  n("(?<!a|bc)z", "bcz");
  x2("(?<name1>a)", "a", 0, 1);
  x2("(?<name_2>ab)\\g<name_2>", "abab", 0, 4);
  x2("(?<name_3>.zv.)\\k<name_3>", "azvbazvb", 0, 8);
  x2("(?<=\\g<ab>)|-\\zEND (?<ab>XyZ)", "XyZ", 3, 3);
  x2("(?<n>|a\\g<n>)+", "", 0, 0);
  x2("(?<n>|\\(\\g<n>\\))+$", "()(())", 0, 6);
  x3("\\g<n>(?<n>.){0}", "X", 0, 1, 1);
  x2("\\g<n>(abc|df(?<n>.YZ){2,8}){0}", "XYZ", 0, 3);
  x2("\\A(?<n>(a\\g<n>)|)\\z", "aaaa", 0, 4);
  x2("(?<n>|\\g<m>\\g<n>)\\z|\\zEND (?<m>a|(b)\\g<m>)", "bbbbabba", 0, 8);
  x2("(?<name1240>\\w+\\sx)a+\\k<name1240>", "  fg xaaaaaaaafg x", 2, 18);
  x3("(z)()()(?<_9>a)\\g<_9>", "zaa", 2, 3, 1);
  x2("(.)(((?<_>a)))\\k<_>", "zaa", 0, 3);
  x2("((?<name1>\\d)|(?<name2>\\w))(\\k<name1>|\\k<name2>)", "ff", 0, 2);
  x2("(?:(?<x>)|(?<x>efg))\\k<x>", "", 0, 0);
  x2("(?:(?<x>abc)|(?<x>efg))\\k<x>", "abcefgefg", 3, 9);
  n("(?:(?<x>abc)|(?<x>efg))\\k<x>", "abcefg");
  x2("(?:(?<n1>.)|(?<n1>..)|(?<n1>...)|(?<n1>....)|(?<n1>.....)|(?<n1>......)|(?<n1>.......)|(?<n1>........)|(?<n1>.........)|(?<n1>..........)|(?<n1>...........)|(?<n1>............)|(?<n1>.............)|(?<n1>..............))\\k<n1>$", "a-pyumpyum", 2, 10);
  x3("(?:(?<n1>.)|(?<n1>..)|(?<n1>...)|(?<n1>....)|(?<n1>.....)|(?<n1>......)|(?<n1>.......)|(?<n1>........)|(?<n1>.........)|(?<n1>..........)|(?<n1>...........)|(?<n1>............)|(?<n1>.............)|(?<n1>..............))\\k<n1>$", "xxxxabcdefghijklmnabcdefghijklmn", 4, 18, 14);
  x3("(?<name1>)(?<name2>)(?<name3>)(?<name4>)(?<name5>)(?<name6>)(?<name7>)(?<name8>)(?<name9>)(?<name10>)(?<name11>)(?<name12>)(?<name13>)(?<name14>)(?<name15>)(?<name16>aaa)(?<name17>)$", "aaa", 0, 3, 16);
  x2("(?<foo>a|\\(\\g<foo>\\))", "a", 0, 1);
  x2("(?<foo>a|\\(\\g<foo>\\))", "((((((a))))))", 0, 13);
  x3("(?<foo>a|\\(\\g<foo>\\))", "((((((((a))))))))", 0, 17, 1);
  x2("\\g<bar>|\\zEND(?<bar>.*abc$)", "abcxxxabc", 0, 9);
  x2("\\g<1>|\\zEND(.a.)", "bac", 0, 3);
  x3("\\g<_A>\\g<_A>|\\zEND(.a.)(?<_A>.b.)", "xbxyby", 3, 6, 1);
  x2("\\A(?:\\g<pon>|\\g<pan>|\\zEND  (?<pan>a|c\\g<pon>c)(?<pon>b|d\\g<pan>d))$", "cdcbcdc", 0, 7);
  x2("\\A(?<n>|a\\g<m>)\\z|\\zEND (?<m>\\g<n>)", "aaaa", 0, 4);
  x2("(?<n>(a|b\\g<n>c){3,5})", "baaaaca", 1, 5);
  x2("(?<n>(a|b\\g<n>c){3,5})", "baaaacaaaaa", 0, 10);
  x2("(?<pare>\\(([^\\(\\)]++|\\g<pare>)*+\\))", "((a))", 0, 5);
  x2("()*\\1", "", 0, 0);
  x2("(?:()|())*\\1\\2", "", 0, 0);
  x3("(?:\\1a|())*", "a", 0, 0, 1);
  x2("x((.)*)*x", "0x1x2x3", 1, 6);
  x2("x((.)*)*x(?i:\\1)\\Z", "0x1x2x1X2", 1, 9);
  x2("(?:()|()|()|()|()|())*\\2\\5", "", 0, 0);
  x2("(?:()|()|()|(x)|()|())*\\2b\\5", "b", 0, 1);
  x2("[0-9-a]", "-", 0, 1);   // PR#44
  n("[0-9-a]", ":");          // PR#44
  x3("(\\(((?:[^(]|\\g<1>)*)\\))", "(abc)(abc)", 1, 4, 2); // PR#43
  x2("\\o{101}", "A", 0, 1);
  x2("(?:\\k'+1'B|(A)C)*", "ACAB", 0, 4); // relative backref by postitive number
  x2("\\g<+2>(abc)(ABC){0}", "ABCabc", 0, 6); // relative call by positive number
  x2("A\\g'0'|B()", "AAAAB", 0, 5);
  x3("(A\\g'0')|B", "AAAAB", 0, 5, 1);
  x2("(a*)(?(1))aa", "aaaaa", 0, 5);
  x2("(a*)(?(-1))aa", "aaaaa", 0, 5);
  x2("(?<name>aaa)(?('name'))aa", "aaaaa", 0, 5);
  x2("(a)(?(1)aa|bb)a", "aaaaa", 0, 4);
  x2("(?:aa|())(?(<1>)aa|bb)a", "aabba", 0, 5);
  x2("(?:aa|())(?('1')aa|bb|cc)a", "aacca", 0, 5);
  x3("(a*)(?(1)aa|a)b", "aaab", 0, 1, 1);
  n("(a)(?(1)a|b)c", "abc");
  x2("(a)(?(1)|)c", "ac", 0, 2);
  n("(?()aaa|bbb)", "bbb");
  x2("(a)(?(1+0)b|c)d", "abd", 0, 3);
  x2("(?:(?'name'a)|(?'name'b))(?('name')c|d)e", "ace", 0, 3);
  x2("(?:(?'name'a)|(?'name'b))(?('name')c|d)e", "bce", 0, 3);
  x2("\\R", "\r\n", 0, 2);
  x2("\\R", "\r", 0, 1);
  x2("\\R", "\n", 0, 1);
  x2("\\R", "\x0b", 0, 1);
  n("\\R\\n", "\r\n");
  x2("\\N", "a", 0, 1);
  n("\\N", "\n");
  n("(?m:\\N)", "\n");
  n("(?-m:\\N)", "\n");
  x2("\\O", "a", 0, 1);
  x2("\\O", "\n", 0, 1);
  x2("(?m:\\O)", "\n", 0, 1);
  x2("(?-m:\\O)", "\n", 0, 1);
  x2("\\K", "a", 0, 0);
  x2("a\\K", "a", 1, 1);
  x2("a\\Kb", "ab", 1, 2);
  x2("(a\\Kb|ac\\Kd)", "acd", 2, 3);
  x2("(a\\Kb|\\Kac\\K)*", "acababacab", 9, 10);

  x2("(?~)", "", 0, 0);
  x2("(?~)", "A", 0, 0);
  x2("aaaaa(?~)", "aaaaaaaaaa", 0, 5);
  x2("(?~(?:|aaa))", "aaa", 0, 0);
  x2("(?~aaa|)", "aaa", 0, 0);
  x2("a(?~(?~)).", "abcdefghijklmnopqrstuvwxyz", 0, 26); // !!!
  x2("/\\*(?~\\*/)\\*/", "/* */ */", 0, 5);
  x2("(?~\\w+)zzzzz", "zzzzz", 0, 5);
  x2("(?~\\w*)zzzzz", "zzzzz", 0, 5);
  x2("(?~A.C|B)", "ABC", 0, 0);
  x2("(?~XYZ|ABC)a", "ABCa", 1, 4);
  x2("(?~XYZ|ABC)a", "aABCa", 0, 1);
  x2("<[^>]*>(?~[<>])</[^>]*>", "<a>vvv</a>   <b>  </b>", 0, 10);
  x2("(?~ab)", "ccc\ndab", 0, 5);
  x2("(?m:(?~ab))", "ccc\ndab", 0, 5);
  x2("(?-m:(?~ab))", "ccc\ndab", 0, 5);
  x2("(?~abc)xyz", "xyz012345678901234567890123456789abc", 0, 3);

  // absent with expr
  x2("(?~|78|\\d*)", "123456789", 0, 6);
  x2("(?~|def|(?:abc|de|f){0,100})", "abcdedeabcfdefabc", 0, 11);
  x2("(?~|ab|.*)", "ccc\nddd", 0, 3);
  x2("(?~|ab|\\O*)", "ccc\ndab", 0, 5);
  x2("(?~|ab|\\O{2,10})", "ccc\ndab", 0, 5);
  x2("(?~|ab|\\O{1,10})", "ab", 1, 2);
  n("(?~|ab|\\O{2,10})", "ab");
  x2("(?~|abc|\\O{1,10})", "abc", 1, 3);
  x2("(?~|ab|\\O{5,10})|abc", "abc", 0, 3);
  x2("(?~|ab|\\O{1,10})", "cccccccccccab", 0, 10);
  x2("(?~|aaa|)", "aaa", 0, 0);
  x2("(?~||a*)", "aaaaaa", 0, 0);
  x2("(?~||a*?)", "aaaaaa", 0, 0);
  x2("(a)(?~|b|\\1)", "aaaaaa", 0, 2);
  x2("(a)(?~|bb|(?:a\\1)*)", "aaaaaa", 0, 5);
  x2("(b|c)(?~|abac|(?:a\\1)*)", "abababacabab", 1, 4);
  n("(?~|c|a*+)a", "aaaaa");
  x2("(?~|aaaaa|a*+)", "aaaaa", 0, 0);
  x2("(?~|aaaaaa|a*+)b", "aaaaaab", 1, 7);
  x2("(?~|abcd|(?>))", "zzzabcd", 0, 0);
  x2("(?~|abc|a*?)", "aaaabc", 0, 0);

  // absent stopper
  x2("(?~|abc)a*", "aaaaaabc", 0, 5);
  x2("(?~|abc)a*z|aaaaaabc", "aaaaaabc", 0, 8);
  x2("(?~|aaaaaa)a*", "aaaaaa", 0, 0);
  x2("(?~|abc)aaaa|aaaabc", "aaaabc", 0, 6);
  x2("(?>(?~|abc))aaaa|aaaabc", "aaaabc", 0, 6);
  x2("(?~|)a", "a", 0, 1);
  n("(?~|a)a", "a");
  x2("(?~|a)(?~|)a", "a", 0, 1);
  x2("(?~|a).*(?~|)a", "bbbbbbbbbbbbbbbbbbbba", 0, 21);
  x2("(?~|abc).*(xyz|pqr)(?~|)abc", "aaaaxyzaaapqrabc", 0, 16);
  x2("(?~|abc).*(xyz|pqr)(?~|)abc", "aaaaxyzaaaabcpqrabc", 11, 19);
  n("\\A(?~|abc).*(xyz|pqrabc)(?~|)abc", "aaaaxyzaaaabcpqrabcabc");
  x2("(?~|a)(?~|)c|ab|a|", "ab", 0, 2);
  x2("(?~|a)((?~|)c|ab|a|)", "ab", 0, 0);
  x2("(?~|a)((?>(?~|))c|ab|a|)", "ab", 0, 0);

  // extended grapheme cluster
  // CR + LF
  n(".\\y\\O", "\x0d\x0a");
  x2(".\\Y\\O", "\x0d\x0a", 0, 2);
  n("\\X\\X", "\x0d\x0a");
  x2("^\\X$", "\x0d\x0a", 0, 2);
  x2("^\\X\\X\\X$", "ab\x0d\x0a", 0, 4);

  fprintf(stdout,
       "\nRESULT   SUCC: %4d,  FAIL: %d,  ERROR: %d      (by Oniguruma %s)\n",
       nsucc, nfail, nerror, onig_version());

  return ((nfail == 0 && nerror == 0) ? 0 : -1);
}
