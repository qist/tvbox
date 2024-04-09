import { inRange, decoderError, isASCIICodePoint,
  end_of_stream, finished } from './text_decoder_utils.js'

/**
 * @implements {Decoder}
 */
export class UTF8Decoder {
  /**
   * @param {{fatal: boolean}} options
   */
  constructor(options) {
    const { fatal } = options

    // utf-8's decoder's has an associated utf-8 code point, utf-8
    // bytes seen, and utf-8 bytes needed (all initially 0), a utf-8
    // lower boundary (initially 0x80), and a utf-8 upper boundary
    // (initially 0xBF).
    let /** @type {number} */ utf8_code_point = 0,
      /** @type {number} */ utf8_bytes_seen = 0,
      /** @type {number} */ utf8_bytes_needed = 0,
      /** @type {number} */ utf8_lower_boundary = 0x80,
      /** @type {number} */ utf8_upper_boundary = 0xBF

    /**
     * @param {Stream} stream The stream of bytes being decoded.
     * @param {number} bite The next byte read from the stream.
     * @return {?(number|!Array.<number>)} The next code point(s)
     *     decoded, or null if not enough data exists in the input
     *     stream to decode a complete code point.
     */
    this.handler = function(stream, bite) {
      // 1. If byte is end-of-stream and utf-8 bytes needed is not 0,
      // set utf-8 bytes needed to 0 and return error.
      if (bite === end_of_stream && utf8_bytes_needed !== 0) {
        utf8_bytes_needed = 0
        return decoderError(fatal)
      }

      // 2. If byte is end-of-stream, return finished.
      if (bite === end_of_stream)
        return finished

      // 3. If utf-8 bytes needed is 0, based on byte:
      if (utf8_bytes_needed === 0) {
        // 0x00 to 0x7F
        if (inRange(bite, 0x00, 0x7F)) {
          // Return a code point whose value is byte.
          return bite
        }

        // 0xC2 to 0xDF
        else if (inRange(bite, 0xC2, 0xDF)) {
          // 1. Set utf-8 bytes needed to 1.
          utf8_bytes_needed = 1

          // 2. Set UTF-8 code point to byte & 0x1F.
          utf8_code_point = bite & 0x1F
        }

        // 0xE0 to 0xEF
        else if (inRange(bite, 0xE0, 0xEF)) {
          // 1. If byte is 0xE0, set utf-8 lower boundary to 0xA0.
          if (bite === 0xE0)
            utf8_lower_boundary = 0xA0
          // 2. If byte is 0xED, set utf-8 upper boundary to 0x9F.
          if (bite === 0xED)
            utf8_upper_boundary = 0x9F
          // 3. Set utf-8 bytes needed to 2.
          utf8_bytes_needed = 2
          // 4. Set UTF-8 code point to byte & 0xF.
          utf8_code_point = bite & 0xF
        }

        // 0xF0 to 0xF4
        else if (inRange(bite, 0xF0, 0xF4)) {
          // 1. If byte is 0xF0, set utf-8 lower boundary to 0x90.
          if (bite === 0xF0)
            utf8_lower_boundary = 0x90
          // 2. If byte is 0xF4, set utf-8 upper boundary to 0x8F.
          if (bite === 0xF4)
            utf8_upper_boundary = 0x8F
          // 3. Set utf-8 bytes needed to 3.
          utf8_bytes_needed = 3
          // 4. Set UTF-8 code point to byte & 0x7.
          utf8_code_point = bite & 0x7
        }

        // Otherwise
        else {
          // Return error.
          return decoderError(fatal)
        }

        // Return continue.
        return null
      }

      // 4. If byte is not in the range utf-8 lower boundary to utf-8
      // upper boundary, inclusive, run these substeps:
      if (!inRange(bite, utf8_lower_boundary, utf8_upper_boundary)) {
        // 1. Set utf-8 code point, utf-8 bytes needed, and utf-8
        // bytes seen to 0, set utf-8 lower boundary to 0x80, and set
        // utf-8 upper boundary to 0xBF.
        utf8_code_point = utf8_bytes_needed = utf8_bytes_seen = 0
        utf8_lower_boundary = 0x80
        utf8_upper_boundary = 0xBF

        // 2. Prepend byte to stream.
        stream.prepend(bite)

        // 3. Return error.
        return decoderError(fatal)
      }

      // 5. Set utf-8 lower boundary to 0x80 and utf-8 upper boundary
      // to 0xBF.
      utf8_lower_boundary = 0x80
      utf8_upper_boundary = 0xBF

      // 6. Set UTF-8 code point to (UTF-8 code point << 6) | (byte &
      // 0x3F)
      utf8_code_point = (utf8_code_point << 6) | (bite & 0x3F)

      // 7. Increase utf-8 bytes seen by one.
      utf8_bytes_seen += 1

      // 8. If utf-8 bytes seen is not equal to utf-8 bytes needed,
      // continue.
      if (utf8_bytes_seen !== utf8_bytes_needed)
        return null

      // 9. Let code point be utf-8 code point.
      var code_point = utf8_code_point

      // 10. Set utf-8 code point, utf-8 bytes needed, and utf-8 bytes
      // seen to 0.
      utf8_code_point = utf8_bytes_needed = utf8_bytes_seen = 0

      // 11. Return a code point whose value is code point.
      return code_point
    }
  }
}

// 9.1.2 utf-8 encoder

/**
 * @implements {Encoder}
 */
export class UTF8Encoder {
  constructor() {
    /**
     * @param {Stream} stream Input stream.
     * @param {number} code_point Next code point read from the stream.
     * @return {(number|!Array.<number>)} Byte(s) to emit.
     */
    this.handler = function(stream, code_point) {
      // 1. If code point is end-of-stream, return finished.
      if (code_point === end_of_stream)
        return finished

      // 2. If code point is an ASCII code point, return a byte whose
      // value is code point.
      if (isASCIICodePoint(code_point))
        return code_point

      // 3. Set count and offset based on the range code point is in:
      var count, offset
      // U+0080 to U+07FF, inclusive:
      if (inRange(code_point, 0x0080, 0x07FF)) {
        // 1 and 0xC0
        count = 1
        offset = 0xC0
      }
      // U+0800 to U+FFFF, inclusive:
      else if (inRange(code_point, 0x0800, 0xFFFF)) {
        // 2 and 0xE0
        count = 2
        offset = 0xE0
      }
      // U+10000 to U+10FFFF, inclusive:
      else if (inRange(code_point, 0x10000, 0x10FFFF)) {
        // 3 and 0xF0
        count = 3
        offset = 0xF0
      }

      // 4. Let bytes be a byte sequence whose first byte is (code
      // point >> (6 × count)) + offset.
      var bytes = [(code_point >> (6 * count)) + offset]

      // 5. Run these substeps while count is greater than 0:
      while (count > 0) {
        // 1. Set temp to code point >> (6 × (count − 1)).
        var temp = code_point >> (6 * (count - 1))

        // 2. Append to bytes 0x80 | (temp & 0x3F).
        bytes.push(0x80 | (temp & 0x3F))

        // 3. Decrease count by one.
        count -= 1
      }

      // 6. Return bytes bytes, in order.
      return bytes
    }
  }
}