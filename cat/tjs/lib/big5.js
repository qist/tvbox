import { inRange, decoderError, encoderError, isASCIICodePoint,
  end_of_stream, finished, isASCIIByte, floor } from './text_decoder_utils.js'
import index, { indexBig5PointerFor, indexCodePointFor } from './text_decoder_indexes.js'

//
// 12. Legacy multi-byte Chinese (traditional) encodings
//

// 12.1 Big5

// 12.1.1 Big5 decoder
/**
 * @implements {Decoder}
 */
export class Big5Decoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal
    // Big5's decoder has an associated Big5 lead (initially 0x00).
    this.Big5_lead = 0x00
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
  // 1. If byte is end-of-stream and Big5 lead is not 0x00, set
  // Big5 lead to 0x00 and return error.
    if (bite === end_of_stream && this.Big5_lead !== 0x00) {
      this.Big5_lead = 0x00
      return decoderError(this.fatal)
    }

    // 2. If byte is end-of-stream and Big5 lead is 0x00, return
    // finished.
    if (bite === end_of_stream && this.Big5_lead === 0x00)
      return finished

    // 3. If Big5 lead is not 0x00, let lead be Big5 lead, let
    // pointer be null, set Big5 lead to 0x00, and then run these
    // substeps:
    if (this.Big5_lead !== 0x00) {
      const lead = this.Big5_lead
      let pointer = null
      this.Big5_lead = 0x00

      // 1. Let offset be 0x40 if byte is less than 0x7F and 0x62
      // otherwise.
      const offset = bite < 0x7F ? 0x40 : 0x62

      // 2. If byte is in the range 0x40 to 0x7E, inclusive, or 0xA1
      // to 0xFE, inclusive, set pointer to (lead − 0x81) × 157 +
      // (byte − offset).
      if (inRange(bite, 0x40, 0x7E) || inRange(bite, 0xA1, 0xFE))
        pointer = (lead - 0x81) * 157 + (bite - offset)

      // 3. If there is a row in the table below whose first column
      // is pointer, return the two code points listed in its second
      // column
      // Pointer | Code points
      // --------+--------------
      // 1133    | U+00CA U+0304
      // 1135    | U+00CA U+030C
      // 1164    | U+00EA U+0304
      // 1166    | U+00EA U+030C
      switch (pointer) {
      case 1133: return [0x00CA, 0x0304]
      case 1135: return [0x00CA, 0x030C]
      case 1164: return [0x00EA, 0x0304]
      case 1166: return [0x00EA, 0x030C]
      }

      // 4. Let code point be null if pointer is null and the index
      // code point for pointer in index Big5 otherwise.
      const code_point = (pointer === null) ? null :
        indexCodePointFor(pointer, index('big5'))

      // 5. If code point is null and byte is an ASCII byte, prepend
      // byte to stream.
      if (code_point === null && isASCIIByte(bite))
        stream.prepend(bite)

      // 6. If code point is null, return error.
      if (code_point === null)
        return decoderError(this.fatal)

      // 7. Return a code point whose value is code point.
      return code_point
    }

    // 4. If byte is an ASCII byte, return a code point whose value
    // is byte.
    if (isASCIIByte(bite))
      return bite

    // 5. If byte is in the range 0x81 to 0xFE, inclusive, set Big5
    // lead to byte and return continue.
    if (inRange(bite, 0x81, 0xFE)) {
      this.Big5_lead = bite
      return null
    }

    // 6. Return error.
    return decoderError(this.fatal)
  }
}


// 12.1.2 Big5 encoder
/**
 * @implements {Encoder}
 */
export class Big5Encoder {
  constructor() {
    /**
     * @param {Stream} stream Input stream.
     * @param {number} code_point Next code point read from the stream.
     */
    this.handler = function(stream, code_point) {
    // 1. If code point is end-of-stream, return finished.
      if (code_point === end_of_stream)
        return finished

      // 2. If code point is an ASCII code point, return a byte whose
      // value is code point.
      if (isASCIICodePoint(code_point))
        return code_point

      // 3. Let pointer be the index Big5 pointer for code point.
      const pointer = indexBig5PointerFor(code_point)

      // 4. If pointer is null, return error with code point.
      if (pointer === null)
        return encoderError(code_point)

      // 5. Let lead be floor(pointer / 157) + 0x81.
      const lead = floor(pointer / 157) + 0x81

      // 6. If lead is less than 0xA1, return error with code point.
      if (lead < 0xA1)
        return encoderError(code_point)

      // 7. Let trail be pointer % 157.
      const trail = pointer % 157

      // 8. Let offset be 0x40 if trail is less than 0x3F and 0x62
      // otherwise.
      const offset = trail < 0x3F ? 0x40 : 0x62

      // Return two bytes whose values are lead and trail + offset.
      return [lead, trail + offset]
    }
  }
}