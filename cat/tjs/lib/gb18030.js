import { inRange, decoderError, encoderError, isASCIICodePoint,
  end_of_stream, finished, isASCIIByte, floor } from './text_decoder_utils.js'
import index, {
  indexGB18030RangesCodePointFor, indexGB18030RangesPointerFor,
  indexCodePointFor, indexPointerFor } from './text_decoder_indexes.js'

// 11.2 gb18030

// 11.2.1 gb18030 decoder
/**
 * @constructor
 * @implements {Decoder}
 * @param {{fatal: boolean}} options
 */
export class GB18030Decoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal
    // gb18030's decoder has an associated gb18030 first, gb18030
    // second, and gb18030 third (all initially 0x00).
    this.gb18030_first = 0x00
    this.gb18030_second = 0x00,
    this.gb18030_third = 0x00
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   * @return The next code point(s) decoded, or null if not enough data exists in the input stream to decode a complete code point.
   */
  handler(stream, bite) {
    // 1. If byte is end-of-stream and gb18030 first, gb18030
    // second, and gb18030 third are 0x00, return finished.
    if (bite === end_of_stream && this.gb18030_first === 0x00 &&
        this.gb18030_second === 0x00 && this.gb18030_third === 0x00) {
      return finished
    }
    // 2. If byte is end-of-stream, and gb18030 first, gb18030
    // second, or gb18030 third is not 0x00, set gb18030 first,
    // gb18030 second, and gb18030 third to 0x00, and return error.
    if (bite === end_of_stream &&
        (this.gb18030_first !== 0x00 || this.gb18030_second !== 0x00 ||
          this.gb18030_third !== 0x00)) {
      this.gb18030_first = 0x00
      this.gb18030_second = 0x00
      this.gb18030_third = 0x00
      decoderError(this.fatal)
    }
    var code_point
    // 3. If gb18030 third is not 0x00, run these substeps:
    if (this.gb18030_third !== 0x00) {
      // 1. Let code point be null.
      code_point = null
      // 2. If byte is in the range 0x30 to 0x39, inclusive, set
      // code point to the index gb18030 ranges code point for
      // (((gb18030 first − 0x81) × 10 + gb18030 second − 0x30) ×
      // 126 + gb18030 third − 0x81) × 10 + byte − 0x30.
      if (inRange(bite, 0x30, 0x39)) {
        code_point = indexGB18030RangesCodePointFor(
          (((this.gb18030_first - 0x81) * 10 + this.gb18030_second - 0x30) * 126 +
              this.gb18030_third - 0x81) * 10 + bite - 0x30)
      }

      // 3. Let buffer be a byte sequence consisting of gb18030
      // second, gb18030 third, and byte, in order.
      var buffer = [this.gb18030_second, this.gb18030_third, bite]

      // 4. Set gb18030 first, gb18030 second, and gb18030 third to
      // 0x00.
      this.gb18030_first = 0x00
      this.gb18030_second = 0x00
      this.gb18030_third = 0x00

      // 5. If code point is null, prepend buffer to stream and
      // return error.
      if (code_point === null) {
        stream.prepend(buffer)
        return decoderError(this.fatal)
      }

      // 6. Return a code point whose value is code point.
      return code_point
    }

    // 4. If gb18030 second is not 0x00, run these substeps:
    if (this.gb18030_second !== 0x00) {
      // 1. If byte is in the range 0x81 to 0xFE, inclusive, set
      // gb18030 third to byte and return continue.
      if (inRange(bite, 0x81, 0xFE)) {
        this.gb18030_third = bite
        return null
      }

      // 2. Prepend gb18030 second followed by byte to stream, set
      // gb18030 first and gb18030 second to 0x00, and return error.
      stream.prepend([this.gb18030_second, bite])
      this.gb18030_first = 0x00
      this.gb18030_second = 0x00
      return decoderError(this.fatal)
    }

    // 5. If gb18030 first is not 0x00, run these substeps:
    if (this.gb18030_first !== 0x00) {
      // 1. If byte is in the range 0x30 to 0x39, inclusive, set
      // gb18030 second to byte and return continue.
      if (inRange(bite, 0x30, 0x39)) {
        this.gb18030_second = bite
        return null
      }

      // 2. Let lead be gb18030 first, let pointer be null, and set
      // gb18030 first to 0x00.
      var lead = this.gb18030_first
      var pointer = null
      this.gb18030_first = 0x00

      // 3. Let offset be 0x40 if byte is less than 0x7F and 0x41
      // otherwise.
      var offset = bite < 0x7F ? 0x40 : 0x41

      // 4. If byte is in the range 0x40 to 0x7E, inclusive, or 0x80
      // to 0xFE, inclusive, set pointer to (lead − 0x81) × 190 +
      // (byte − offset).
      if (inRange(bite, 0x40, 0x7E) || inRange(bite, 0x80, 0xFE))
        pointer = (lead - 0x81) * 190 + (bite - offset)

      // 5. Let code point be null if pointer is null and the index
      // code point for pointer in index gb18030 otherwise.
      code_point = pointer === null ? null :
        indexCodePointFor(pointer, index('gb18030'))

      // 6. If code point is null and byte is an ASCII byte, prepend
      // byte to stream.
      if (code_point === null && isASCIIByte(bite))
        stream.prepend(bite)

      // 7. If code point is null, return error.
      if (code_point === null)
        return decoderError(this.fatal)

      // 8. Return a code point whose value is code point.
      return code_point
    }

    // 6. If byte is an ASCII byte, return a code point whose value
    // is byte.
    if (isASCIIByte(bite))
      return bite

    // 7. If byte is 0x80, return code point U+20AC.
    if (bite === 0x80)
      return 0x20AC

    // 8. If byte is in the range 0x81 to 0xFE, inclusive, set
    // gb18030 first to byte and return continue.
    if (inRange(bite, 0x81, 0xFE)) {
      this.gb18030_first = bite
      return null
    }

    // 9. Return error.
    return decoderError(this.fatal)
  }
}

// 11.2.2 gb18030 encoder
/**
 * @implements {Encoder}
 */
export class GB18030Encoder {
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   * @return Byte(s) to emit.
   */
  handler(stream, code_point) {
    // 1. If code point is end-of-stream, return finished.
    if (code_point === end_of_stream)
      return finished

    // 2. If code point is an ASCII code point, return a byte whose
    // value is code point.
    if (isASCIICodePoint(code_point))
      return code_point

    // 3. If code point is U+E5E5, return error with code point.
    if (code_point === 0xE5E5)
      return encoderError(code_point)

    // 4. If the gbk flag is set and code point is U+20AC, return
    // byte 0x80.
    if (this.gbk_flag && code_point === 0x20AC)
      return 0x80

    // 5. Let pointer be the index pointer for code point in index
    // gb18030.
    var pointer = indexPointerFor(code_point, index('gb18030'))

    // 6. If pointer is not null, run these substeps:
    if (pointer !== null) {
    // 1. Let lead be floor(pointer / 190) + 0x81.
      var lead = floor(pointer / 190) + 0x81

      // 2. Let trail be pointer % 190.
      var trail = pointer % 190

      // 3. Let offset be 0x40 if trail is less than 0x3F and 0x41 otherwise.
      var offset = trail < 0x3F ? 0x40 : 0x41

      // 4. Return two bytes whose values are lead and trail + offset.
      return [lead, trail + offset]
    }

    // 7. If gbk flag is set, return error with code point.
    if (this.gbk_flag)
      return encoderError(code_point)

    // 8. Set pointer to the index gb18030 ranges pointer for code
    // point.
    pointer = indexGB18030RangesPointerFor(code_point)

    // 9. Let byte1 be floor(pointer / 10 / 126 / 10).
    var byte1 = floor(pointer / 10 / 126 / 10)

    // 10. Set pointer to pointer − byte1 × 10 × 126 × 10.
    pointer = pointer - byte1 * 10 * 126 * 10

    // 11. Let byte2 be floor(pointer / 10 / 126).
    var byte2 = floor(pointer / 10 / 126)

    // 12. Set pointer to pointer − byte2 × 10 × 126.
    pointer = pointer - byte2 * 10 * 126

    // 13. Let byte3 be floor(pointer / 10).
    var byte3 = floor(pointer / 10)

    // 14. Let byte4 be pointer − byte3 × 10.
    var byte4 = pointer - byte3 * 10

    // 15. Return four bytes whose values are byte1 + 0x81, byte2 +
    // 0x30, byte3 + 0x81, byte4 + 0x30.
    return [byte1 + 0x81,
      byte2 + 0x30,
      byte3 + 0x81,
      byte4 + 0x30]
  }

  constructor(options = {}, gbk_flag = false) {
    // gb18030's decoder has an associated gbk flag (initially unset).
    this.gbk_flag = gbk_flag
  }
}
