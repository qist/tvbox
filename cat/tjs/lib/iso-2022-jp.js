import { inRange, decoderError, encoderError, isASCIICodePoint,
  end_of_stream, finished, floor } from './text_decoder_utils.js'
import index, { indexCodePointFor, indexPointerFor } from './text_decoder_indexes.js'

// 13.2 iso-2022-jp

// 13.2.1 iso-2022-jp decoder
/**
 * @implements {Decoder}
 */
export class ISO2022JPDecoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal
    /** @enum */
    this.states = {
      ASCII: 0,
      Roman: 1,
      Katakana: 2,
      LeadByte: 3,
      TrailByte: 4,
      EscapeStart: 5,
      Escape: 6,
    }
    // iso-2022-jp's decoder has an associated iso-2022-jp decoder
    // state (initially ASCII), iso-2022-jp decoder output state
    // (initially ASCII), iso-2022-jp lead (initially 0x00), and
    // iso-2022-jp output flag (initially unset).
    this.iso2022jp_decoder_state = this.states.ASCII
    this.iso2022jp_decoder_output_state = this.states.ASCII,
    this.iso2022jp_lead = 0x00
    this.iso2022jp_output_flag = false
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
  // switching on iso-2022-jp decoder state:
    switch (this.iso2022jp_decoder_state) {
    default:
    case this.states.ASCII:
    // ASCII
    // Based on byte:

      // 0x1B
      if (bite === 0x1B) {
      // Set iso-2022-jp decoder state to escape start and return
      // continue.
        this.iso2022jp_decoder_state = this.states.EscapeStart
        return null
      }

      // 0x00 to 0x7F, excluding 0x0E, 0x0F, and 0x1B
      if (inRange(bite, 0x00, 0x7F) && bite !== 0x0E
        && bite !== 0x0F && bite !== 0x1B) {
      // Unset the iso-2022-jp output flag and return a code point
      // whose value is byte.
        this.iso2022jp_output_flag = false
        return bite
      }

      // end-of-stream
      if (bite === end_of_stream) {
      // Return finished.
        return finished
      }

      // Otherwise
      // Unset the iso-2022-jp output flag and return error.
      this.iso2022jp_output_flag = false
      return decoderError(this.fatal)

    case this.states.Roman:
    // Roman
    // Based on byte:

      // 0x1B
      if (bite === 0x1B) {
      // Set iso-2022-jp decoder state to escape start and return
      // continue.
        this.iso2022jp_decoder_state = this.states.EscapeStart
        return null
      }

      // 0x5C
      if (bite === 0x5C) {
      // Unset the iso-2022-jp output flag and return code point
      // U+00A5.
        this.iso2022jp_output_flag = false
        return 0x00A5
      }

      // 0x7E
      if (bite === 0x7E) {
      // Unset the iso-2022-jp output flag and return code point
      // U+203E.
        this.iso2022jp_output_flag = false
        return 0x203E
      }

      // 0x00 to 0x7F, excluding 0x0E, 0x0F, 0x1B, 0x5C, and 0x7E
      if (inRange(bite, 0x00, 0x7F) && bite !== 0x0E && bite !== 0x0F
        && bite !== 0x1B && bite !== 0x5C && bite !== 0x7E) {
      // Unset the iso-2022-jp output flag and return a code point
      // whose value is byte.
        this.iso2022jp_output_flag = false
        return bite
      }

      // end-of-stream
      if (bite === end_of_stream) {
      // Return finished.
        return finished
      }

      // Otherwise
      // Unset the iso-2022-jp output flag and return error.
      this.iso2022jp_output_flag = false
      return decoderError(this.fatal)

    case this.states.Katakana:
    // Katakana
    // Based on byte:

      // 0x1B
      if (bite === 0x1B) {
      // Set iso-2022-jp decoder state to escape start and return
      // continue.
        this.iso2022jp_decoder_state = this.states.EscapeStart
        return null
      }

      // 0x21 to 0x5F
      if (inRange(bite, 0x21, 0x5F)) {
      // Unset the iso-2022-jp output flag and return a code point
      // whose value is 0xFF61 − 0x21 + byte.
        this.iso2022jp_output_flag = false
        return 0xFF61 - 0x21 + bite
      }

      // end-of-stream
      if (bite === end_of_stream) {
      // Return finished.
        return finished
      }

      // Otherwise
      // Unset the iso-2022-jp output flag and return error.
      this.iso2022jp_output_flag = false
      return decoderError(this.fatal)

    case this.states.LeadByte:
    // Lead byte
    // Based on byte:

      // 0x1B
      if (bite === 0x1B) {
      // Set iso-2022-jp decoder state to escape start and return
      // continue.
        this.iso2022jp_decoder_state = this.states.EscapeStart
        return null
      }

      // 0x21 to 0x7E
      if (inRange(bite, 0x21, 0x7E)) {
      // Unset the iso-2022-jp output flag, set iso-2022-jp lead
      // to byte, iso-2022-jp decoder state to trail byte, and
      // return continue.
        this.iso2022jp_output_flag = false
        this.iso2022jp_lead = bite
        this.iso2022jp_decoder_state = this.states.TrailByte
        return null
      }

      // end-of-stream
      if (bite === end_of_stream) {
      // Return finished.
        return finished
      }

      // Otherwise
      // Unset the iso-2022-jp output flag and return error.
      this.iso2022jp_output_flag = false
      return decoderError(this.fatal)

    case this.states.TrailByte:
    // Trail byte
    // Based on byte:

      // 0x1B
      if (bite === 0x1B) {
      // Set iso-2022-jp decoder state to escape start and return
      // continue.
        this.iso2022jp_decoder_state = this.states.EscapeStart
        return decoderError(this.fatal)
      }

      // 0x21 to 0x7E
      if (inRange(bite, 0x21, 0x7E)) {
      // 1. Set the iso-2022-jp decoder state to lead byte.
        this.iso2022jp_decoder_state = this.states.LeadByte

        // 2. Let pointer be (iso-2022-jp lead − 0x21) × 94 + byte − 0x21.
        const pointer = (this.iso2022jp_lead - 0x21) * 94 + bite - 0x21

        // 3. Let code point be the index code point for pointer in
        // index jis0208.
        const code_point = indexCodePointFor(pointer, index('jis0208'))

        // 4. If code point is null, return error.
        if (code_point === null)
          return decoderError(this.fatal)

        // 5. Return a code point whose value is code point.
        return code_point
      }

      // end-of-stream
      if (bite === end_of_stream) {
      // Set the iso-2022-jp decoder state to lead byte, prepend
      // byte to stream, and return error.
        this.iso2022jp_decoder_state = this.states.LeadByte
        stream.prepend(bite)
        return decoderError(this.fatal)
      }

      // Otherwise
      // Set iso-2022-jp decoder state to lead byte and return
      // error.
      this.iso2022jp_decoder_state = this.states.LeadByte
      return decoderError(this.fatal)

    case this.states.EscapeStart:
    // Escape start

      // 1. If byte is either 0x24 or 0x28, set iso-2022-jp lead to
      // byte, iso-2022-jp decoder state to escape, and return
      // continue.
      if (bite === 0x24 || bite === 0x28) {
        this.iso2022jp_lead = bite
        this.iso2022jp_decoder_state = this.states.Escape
        return null
      }

      // 2. Prepend byte to stream.
      stream.prepend(bite)

      // 3. Unset the iso-2022-jp output flag, set iso-2022-jp
      // decoder state to iso-2022-jp decoder output state, and
      // return error.
      this.iso2022jp_output_flag = false
      this.iso2022jp_decoder_state = this.iso2022jp_decoder_output_state
      return decoderError(this.fatal)

    case this.states.Escape: {
    // Escape

      // 1. Let lead be iso-2022-jp lead and set iso-2022-jp lead to
      // 0x00.
      const lead = this.iso2022jp_lead
      this.iso2022jp_lead = 0x00

      // 2. Let state be null.
      let state = null

      // 3. If lead is 0x28 and byte is 0x42, set state to ASCII.
      if (lead === 0x28 && bite === 0x42)
        state = this.states.ASCII

      // 4. If lead is 0x28 and byte is 0x4A, set state to Roman.
      if (lead === 0x28 && bite === 0x4A)
        state = this.states.Roman

      // 5. If lead is 0x28 and byte is 0x49, set state to Katakana.
      if (lead === 0x28 && bite === 0x49)
        state = this.states.Katakana

      // 6. If lead is 0x24 and byte is either 0x40 or 0x42, set
      // state to lead byte.
      if (lead === 0x24 && (bite === 0x40 || bite === 0x42))
        state = this.states.LeadByte

      // 7. If state is non-null, run these substeps:
      if (state !== null) {
      // 1. Set iso-2022-jp decoder state and iso-2022-jp decoder
      // output state to this.states.
        this.iso2022jp_decoder_state = this.iso2022jp_decoder_state = state

        // 2. Let output flag be the iso-2022-jp output flag.
        const output_flag = this.iso2022jp_output_flag

        // 3. Set the iso-2022-jp output flag.
        this.iso2022jp_output_flag = true

        // 4. Return continue, if output flag is unset, and error
        // otherwise.
        return !output_flag ? null : decoderError(this.fatal)
      }

      // 8. Prepend lead and byte to stream.
      stream.prepend([lead, bite])

      // 9. Unset the iso-2022-jp output flag, set iso-2022-jp
      // decoder state to iso-2022-jp decoder output state and
      // return error.
      this.iso2022jp_output_flag = false
      this.iso2022jp_decoder_state = this.iso2022jp_decoder_output_state
      return decoderError(this.fatal)
    }
    }
  }
}

// 13.2.2 iso-2022-jp encoder
/**
 * @implements {Encoder}
 */
export class ISO2022JPEncoder {
  constructor() {
    // iso-2022-jp's encoder has an associated iso-2022-jp encoder
    // state which is one of ASCII, Roman, and jis0208 (initially
    // ASCII).
    /** @enum */
    this.states = {
      ASCII: 0,
      Roman: 1,
      jis0208: 2,
    }
    this.iso2022jp_state = this.states.ASCII
  }
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   */
  handler(stream, code_point) {
  // 1. If code point is end-of-stream and iso-2022-jp encoder
  // state is not ASCII, prepend code point to stream, set
  // iso-2022-jp encoder state to ASCII, and return three bytes
  // 0x1B 0x28 0x42.
    if (code_point === end_of_stream &&
      this.iso2022jp_state !== this.states.ASCII) {
      stream.prepend(code_point)
      this.iso2022jp_state = this.states.ASCII
      return [0x1B, 0x28, 0x42]
    }

    // 2. If code point is end-of-stream and iso-2022-jp encoder
    // state is ASCII, return finished.
    if (code_point === end_of_stream && this.iso2022jp_state === this.states.ASCII)
      return finished

    // 3. If ISO-2022-JP encoder state is ASCII or Roman, and code
    // point is U+000E, U+000F, or U+001B, return error with U+FFFD.
    if ((this.iso2022jp_state === this.states.ASCII ||
        this.iso2022jp_state === this.states.Roman) &&
      (code_point === 0x000E || code_point === 0x000F ||
        code_point === 0x001B)) {
      return encoderError(0xFFFD)
    }

    // 4. If iso-2022-jp encoder state is ASCII and code point is an
    // ASCII code point, return a byte whose value is code point.
    if (this.iso2022jp_state === this.states.ASCII &&
      isASCIICodePoint(code_point))
      return code_point

    // 5. If iso-2022-jp encoder state is Roman and code point is an
    // ASCII code point, excluding U+005C and U+007E, or is U+00A5
    // or U+203E, run these substeps:
    if (this.iso2022jp_state === this.states.Roman &&
      ((isASCIICodePoint(code_point) &&
        code_point !== 0x005C && code_point !== 0x007E) ||
      (code_point == 0x00A5 || code_point == 0x203E))) {
    // 1. If code point is an ASCII code point, return a byte
    // whose value is code point.
      if (isASCIICodePoint(code_point))
        return code_point

      // 2. If code point is U+00A5, return byte 0x5C.
      if (code_point === 0x00A5)
        return 0x5C

      // 3. If code point is U+203E, return byte 0x7E.
      if (code_point === 0x203E)
        return 0x7E
    }

    // 6. If code point is an ASCII code point, and iso-2022-jp
    // encoder state is not ASCII, prepend code point to stream, set
    // iso-2022-jp encoder state to ASCII, and return three bytes
    // 0x1B 0x28 0x42.
    if (isASCIICodePoint(code_point) &&
      this.iso2022jp_state !== this.states.ASCII) {
      stream.prepend(code_point)
      this.iso2022jp_state = this.states.ASCII
      return [0x1B, 0x28, 0x42]
    }

    // 7. If code point is either U+00A5 or U+203E, and iso-2022-jp
    // encoder state is not Roman, prepend code point to stream, set
    // iso-2022-jp encoder state to Roman, and return three bytes
    // 0x1B 0x28 0x4A.
    if ((code_point === 0x00A5 || code_point === 0x203E) &&
      this.iso2022jp_state !== this.states.Roman) {
      stream.prepend(code_point)
      this.iso2022jp_state = this.states.Roman
      return [0x1B, 0x28, 0x4A]
    }

    // 8. If code point is U+2212, set it to U+FF0D.
    if (code_point === 0x2212)
      code_point = 0xFF0D

    // 9. Let pointer be the index pointer for code point in index
    // jis0208.
    const pointer = indexPointerFor(code_point, index('jis0208'))

    // 10. If pointer is null, return error with code point.
    if (pointer === null)
      return encoderError(code_point)

    // 11. If iso-2022-jp encoder state is not jis0208, prepend code
    // point to stream, set iso-2022-jp encoder state to jis0208,
    // and return three bytes 0x1B 0x24 0x42.
    if (this.iso2022jp_state !== this.states.jis0208) {
      stream.prepend(code_point)
      this.iso2022jp_state = this.states.jis0208
      return [0x1B, 0x24, 0x42]
    }

    // 12. Let lead be floor(pointer / 94) + 0x21.
    const lead = floor(pointer / 94) + 0x21

    // 13. Let trail be pointer % 94 + 0x21.
    const trail = pointer % 94 + 0x21

    // 14. Return two bytes whose values are lead and trail.
    return [lead, trail]
  }
}