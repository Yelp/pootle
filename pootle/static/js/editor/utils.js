/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */


/* Normalizes language codes in order to use them in MT services */
export function normalizeCode(locale) {
  if (!locale) {
    return locale;
  }

  const atIndex = locale.indexOf('@');
  let clean = locale.replace('_', '-');
  if (atIndex !== -1) {
    clean = clean.slice(0, atIndex);
  }
  return clean;
}


/*
 * Escape unsafe regular expression symbols:
 * ! $ & ( ) * + - . : < = > ? [ \ ] ^ { | }
 *
 * Special characters can be written as
 * Regular Expression class:
 * [!$&(-+\-.:<-?\[-^{-}]
 */
export function escapeUnsafeRegexSymbols(s) {
  // Replace doesn't modify original variable and it recreates a
  // new string with special characters escaped.
  return s.replace(/[!$&(-+\-.:<-?\[-^{-}]/g, '\\$&');
}


/*
 * Make regular expression using every word in input string.
 *
 * This function has these steps:
 *  1) escape unsafe regular expression symbols;
 *  2) trim ' ' (whitespaces) to avoid multiple '|' at the beginning
 *    and at the end;
 *  3) replace ' ' (one or more whitespaces) with '|'. In this way every word
 *    can be searched by regular expression;
 *  4) add brackets.
 */
export function makeRegexForMultipleWords(s) {
  return [
    '(', escapeUnsafeRegexSymbols(s).trim().replace(/ +/g, '|'), ')',
  ].join('');
}
