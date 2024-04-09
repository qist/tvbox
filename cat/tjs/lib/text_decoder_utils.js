//
// Utilities
//
/**
 * @param {number} a The number to test.
 * @param {number} min The minimum value in the range, inclusive.
 * @param {number} max The maximum value in the range, inclusive.
 * @return {boolean} True if a >= min and a <= max.
 */
export function inRange(a, min, max) {
  return min <= a && a <= max
}

export const floor = Math.floor

/**
 * @param {string} string Input string of UTF-16 code units.
 * @return {!Array.<number>} Code points.
 */
export function stringToCodePoints(string) {
  // https://heycam.github.io/webidl/#dfn-obtain-unicode

  // 1. Let S be the DOMString value.
  var s = String(string)

  // 2. Let n be the length of S.
  var n = s.length

  // 3. Initialize i to 0.
  var i = 0

  // 4. Initialize U to be an empty sequence of Unicode characters.
  var u = []

  // 5. While i < n:
  while (i < n) {
    // 1. Let c be the code unit in S at index i.
    var c = s.charCodeAt(i)

    // 2. Depending on the value of c:

    // c < 0xD800 or c > 0xDFFF
    if (c < 0xD800 || c > 0xDFFF) {
      // Append to U the Unicode character with code point c.
      u.push(c)
    }

    // 0xDC00 ≤ c ≤ 0xDFFF
    else if (0xDC00 <= c && c <= 0xDFFF) {
      // Append to U a U+FFFD REPLACEMENT CHARACTER.
      u.push(0xFFFD)
    }

    // 0xD800 ≤ c ≤ 0xDBFF
    else if (0xD800 <= c && c <= 0xDBFF) {
      // 1. If i = n−1, then append to U a U+FFFD REPLACEMENT
      // CHARACTER.
      if (i === n - 1) {
        u.push(0xFFFD)
      }
      // 2. Otherwise, i < n−1:
      else {
        // 1. Let d be the code unit in S at index i+1.
        var d = s.charCodeAt(i + 1)

        // 2. If 0xDC00 ≤ d ≤ 0xDFFF, then:
        if (0xDC00 <= d && d <= 0xDFFF) {
          // 1. Let a be c & 0x3FF.
          var a = c & 0x3FF

          // 2. Let b be d & 0x3FF.
          var b = d & 0x3FF

          // 3. Append to U the Unicode character with code point
          // 2^16+2^10*a+b.
          u.push(0x10000 + (a << 10) + b)

          // 4. Set i to i+1.
          i += 1
        }

        // 3. Otherwise, d < 0xDC00 or d > 0xDFFF. Append to U a
        // U+FFFD REPLACEMENT CHARACTER.
        else  {
          u.push(0xFFFD)
        }
      }
    }

    // 3. Set i to i+1.
    i += 1
  }

  // 6. Return U.
  return u
}

/**
 * @param {!Array.<number>} code_points Array of code points.
 * @return {string} string String of UTF-16 code units.
 */
export function codePointsToString(code_points) {
  var s = ''
  for (var i = 0; i < code_points.length; ++i) {
    var cp = code_points[i]
    if (cp <= 0xFFFF) {
      s += String.fromCharCode(cp)
    } else {
      cp -= 0x10000
      s += String.fromCharCode((cp >> 10) + 0xD800,
        (cp & 0x3FF) + 0xDC00)
    }
  }
  return s
}

/**
 * @param {boolean} fatal If true, decoding errors raise an exception.
 * @param {number=} opt_code_point Override the standard fallback code point.
 * @return The code point to insert on a decoding error.
 */
export function decoderError(fatal, opt_code_point) {
  if (fatal)
    throw TypeError('Decoder error')
  return opt_code_point || 0xFFFD
}

/**
 * @param {number} code_point The code point that could not be encoded.
 * @return {number} Always throws, no value is actually returned.
 */
export function encoderError(code_point) {
  throw TypeError('The code point ' + code_point + ' could not be encoded.')
}

/**
 * @param {number} code_unit
 * @param {boolean} utf16be
 */
export function convertCodeUnitToBytes(code_unit, utf16be) {
  // 1. Let byte1 be code unit >> 8.
  const byte1 = code_unit >> 8

  // 2. Let byte2 be code unit & 0x00FF.
  const byte2 = code_unit & 0x00FF

  // 3. Then return the bytes in order:
  // utf-16be flag is set: byte1, then byte2.
  if (utf16be)
    return [byte1, byte2]
  // utf-16be flag is unset: byte2, then byte1.
  return [byte2, byte1]
}


//
// 4. Terminology
//

/**
 * An ASCII byte is a byte in the range 0x00 to 0x7F, inclusive.
 * @param {number} a The number to test.
 * @return {boolean} True if a is in the range 0x00 to 0x7F, inclusive.
 */
export function isASCIIByte(a) {
  return 0x00 <= a && a <= 0x7F
}

/**
 * An ASCII code point is a code point in the range U+0000 to
 * U+007F, inclusive.
 */
export const isASCIICodePoint = isASCIIByte

/**
 * End-of-stream is a special token that signifies no more tokens are in the stream.
 */
export const end_of_stream = -1

export const finished = -1