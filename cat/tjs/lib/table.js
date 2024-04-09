import Encodings from './encodings.js'
import { UTF8Decoder, UTF8Encoder } from './utf8.js'
import { UTF16Decoder, UTF16Encoder } from './utf16.js'
import { GB18030Decoder, GB18030Encoder } from './gb18030.js'
import { Big5Decoder, Big5Encoder } from './big5.js'
import { EUCJPDecoder, EUCJPEncoder } from './euc-jp.js'
import { EUCKRDecoder, EUCKREncoder } from './euc-kr.js'
import { ISO2022JPDecoder, ISO2022JPEncoder } from './iso-2022-jp.js'
import { XUserDefinedDecoder, XUserDefinedEncoder } from './x-user-defined.js'
import { ShiftJISDecoder, ShiftJISEncoder } from './shift-jis.js'
import { SingleByteDecoder, SingleByteEncoder } from './single-byte.js'
import index from './text_decoder_indexes.js';

// 5.2 Names and labels

// TODO: Define @typedef for Encoding: {name:string,labels:Array.<string>}
// https://github.com/google/closure-compiler/issues/247


// Label to encoding registry.
/** @type {Object.<string,{name:string,labels:Array.<string>}>} */
export const label_to_encoding = {}
Encodings.forEach(({ encodings }) => {
  encodings.forEach((encoding) => {
    encoding.labels.forEach((label) => {
      label_to_encoding[label] = encoding
    })
  })
})

// Registry of of encoder/decoder factories, by encoding name.
export const encoders = {
  'UTF-8'() { // 9.1 utf-8
    return new UTF8Encoder()
  },
  'GBK'(options) { // 11.1.2 gbk encoder;
    // gbk's encoder is gb18030's encoder with its gbk flag set.
    return new GB18030Encoder(options, true)
  },
  'gb18030'() {
    return new GB18030Encoder()
  },
  'Big5'() {
    return new Big5Encoder()
  },
  'EUC-JP'() {
    return new EUCJPEncoder()
  },
  'EUC-KR'() {
    return new EUCKREncoder()
  },
  'ISO-2022-JP'() {
    return new ISO2022JPEncoder()
  },
  'UTF-16BE'() { // 15.3 utf-16be
    return new UTF16Encoder(true)
  },
  'UTF-16LE'() { // 15.4 utf-16le
    return new UTF16Encoder()
  },
  'x-user-defined'() {
    return new XUserDefinedEncoder()
  },
  'Shift_JIS'() {
    return new ShiftJISEncoder()
  },
}

/** @type {Object.<string, function({fatal:boolean}): Decoder>} */
export const decoders = {
  'UTF-8'(options) { // 9.1.1 utf-8 decoder
    return new UTF8Decoder(options)
  },
  'GBK'(options) { // 11.1.1 gbk decoder;  gbk's decoder is gb18030's decoder.
    return new GB18030Decoder(options)
  },
  'gb18030'(options) {
    return new GB18030Decoder(options)
  },
  'Big5'(options) {
    return new Big5Decoder(options)
  },
  'EUC-JP'(options) {
    return new EUCJPDecoder(options)
  },
  'EUC-KR'(options) {
    return new EUCKRDecoder(options)
  },
  'ISO-2022-JP'(options) {
    return new ISO2022JPDecoder(options)
  },
  'UTF-16BE'(options) { // 15.3.1 utf-16be decoder
    return new UTF16Decoder(true, options)
  },
  'UTF-16LE'(options) { // 15.4.1 utf-16le decoder
    return new UTF16Decoder(false, options)
  },
  'x-user-defined'() {
    return new XUserDefinedDecoder()
  },
  'Shift_JIS'(options) {
    return new ShiftJISDecoder(options)
  },
}

Encodings.forEach(({ heading, encodings }) => {
  if (heading != 'Legacy single-byte encodings')
    return
  encodings.forEach((encoding) => {
    const name = encoding.name
    const idx = index(name.toLowerCase())
    decoders[name] = (options) => {
      return new SingleByteDecoder(idx, options)
    }
    encoders[name] = (options) => {
      return new SingleByteEncoder(idx, options)
    }
  })
})