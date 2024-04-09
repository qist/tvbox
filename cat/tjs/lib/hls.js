/*
* @File     : hls.js.js
* @Author   : jade
* @Date     : 2024/2/5 16:07
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
let t = {};

function e(e) {
    if (t.strictMode) throw e;
    t.silent || console.error(e.message)
}

function s(t, ...s) {
    for (const [i, n] of s.entries()) n || e(new Error(`${t} : Failed at [${i}]`))
}

function i(...t) {
    for (const [s, [i, n]] of t.entries()) i && (n || e(new Error(`Conditional Assert : Failed at [${s}]`)))
}

function n(...t) {
    for (const [s, i] of t.entries()) void 0 === i && e(new Error(`Param Check : Failed at [${s}]`))
}

function a(...t) {
    for (const [s, [i, n]] of t.entries()) i && void 0 === n && e(new Error(`Conditional Param Check : Failed at [${s}]`))
}

function r(t) {
    e(new Error(`Invalid Playlist : ${t}`))
}

function o(t, e = 10) {
    if ("number" == typeof t) return t;
    const s = 10 === e ? Number.parseFloat(t) : Number.parseInt(t, e);
    return Number.isNaN(s) ? 0 : s
}

function E(t) {
    (t.startsWith("0x") || t.startsWith("0X")) && (t = t.slice(2));
    const e = new Uint8Array(t.length / 2);
    for (let s = 0; s < t.length; s += 2) e[s / 2] = o(t.slice(s, s + 2), 16);
    return e
}

function T(t, s = 0, i = t.length) {
    i <= s && e(new Error(`end must be larger than start : start=${s}, end=${i}`));
    const n = [];
    for (let e = s; e < i; e++) n.push(`0${(255 & t[e]).toString(16).toUpperCase()}`.slice(-2));
    return `0x${n.join("")}`
}

function u(t, e, s = 0) {
    let i = -1;
    for (let n = 0, a = 0; n < t.length; n++) if (t[n] === e) {
        if (a++ === s) return [t.slice(0, n), t.slice(n + 1)];
        i = n
    }
    return -1 !== i ? [t.slice(0, i), t.slice(i + 1)] : [t]
}

function c(t) {
    const e = [];
    let s = !1;
    for (const i of t) "-" !== i && "_" !== i ? s ? (e.push(i.toUpperCase()), s = !1) : e.push(i.toLowerCase()) : s = !0;
    return e.join("")
}

function l(t) {
    return `${t.getUTCFullYear()}-${("0" + (t.getUTCMonth() + 1)).slice(-2)}-${("0" + t.getUTCDate()).slice(-2)}T${("0" + t.getUTCHours()).slice(-2)}:${("0" + t.getUTCMinutes()).slice(-2)}:${("0" + t.getUTCSeconds()).slice(-2)}.${("00" + t.getUTCMilliseconds()).slice(-3)}Z`
}

function h(e = {}) {
    t = Object.assign(t, e)
}

function X() {
    return Object.assign({}, t)
}

function p(t, e) {
    e = Math.trunc(e) || 0;
    const s = t.length >>> 0;
    if (e < 0 && (e = s + e), !(e < 0 || e >= s)) return t[e]
}

class I {
    constructor({
                    type: t,
                    uri: e,
                    groupId: s,
                    language: a,
                    assocLanguage: r,
                    name: o,
                    isDefault: E,
                    autoselect: T,
                    forced: u,
                    instreamId: c,
                    characteristics: l,
                    channels: h
                }) {
        n(t, s, o), i(["SUBTITLES" === t, e], ["CLOSED-CAPTIONS" === t, c], ["CLOSED-CAPTIONS" === t, !e], [u, "SUBTITLES" === t]), this.type = t, this.uri = e, this.groupId = s, this.language = a, this.assocLanguage = r, this.name = o, this.isDefault = E, this.autoselect = T, this.forced = u, this.instreamId = c, this.characteristics = l, this.channels = h
    }
}

class N {
    constructor({
                    uri: t,
                    isIFrameOnly: e = !1,
                    bandwidth: s,
                    averageBandwidth: i,
                    score: a,
                    codecs: r,
                    resolution: o,
                    frameRate: E,
                    hdcpLevel: T,
                    allowedCpc: u,
                    videoRange: c,
                    stableVariantId: l,
                    programId: h,
                    audio: X = [],
                    video: p = [],
                    subtitles: I = [],
                    closedCaptions: N = [],
                    currentRenditions: d = {audio: 0, video: 0, subtitles: 0, closedCaptions: 0}
                }) {
        n(t, s), this.uri = t, this.isIFrameOnly = e, this.bandwidth = s, this.averageBandwidth = i, this.score = a, this.codecs = r, this.resolution = o, this.frameRate = E, this.hdcpLevel = T, this.allowedCpc = u, this.videoRange = c, this.stableVariantId = l, this.programId = h, this.audio = X, this.video = p, this.subtitles = I, this.closedCaptions = N, this.currentRenditions = d
    }
}

class d {
    constructor({id: t, value: e, uri: i, language: a}) {
        n(t, e || i), s("SessionData cannot have both value and uri, shoud be either.", !(e && i)), this.id = t, this.value = e, this.uri = i, this.language = a
    }
}

class A {
    constructor({method: t, uri: e, iv: s, format: r, formatVersion: o}) {
        n(t), a(["NONE" !== t, e]), i(["NONE" === t, !(e || s || r || o)]), this.method = t, this.uri = e, this.iv = s, this.format = r, this.formatVersion = o
    }
}

class f {
    constructor({hint: t = !1, uri: e, mimeType: s, byterange: i}) {
        n(e), this.hint = t, this.uri = e, this.mimeType = s, this.byterange = i
    }
}

class S {
    constructor({
                    id: t,
                    classId: e,
                    start: s,
                    end: r,
                    duration: o,
                    plannedDuration: E,
                    endOnNext: T,
                    attributes: u = {}
                }) {
        n(t), a([!0 === T, e]), i([r, s], [r, s <= r], [o, o >= 0], [E, E >= 0]), this.id = t, this.classId = e, this.start = s, this.end = r, this.duration = o, this.plannedDuration = E, this.endOnNext = T, this.attributes = u
    }
}

class R {
    constructor({type: t, duration: e, tagName: s, value: i}) {
        n(t), a(["OUT" === t, e]), a(["RAW" === t, s]), this.type = t, this.duration = e, this.tagName = s, this.value = i
    }
}

class m {
    constructor(t) {
        n(t), this.type = t
    }
}

class g extends m {
    constructor({isMasterPlaylist: t, uri: e, version: s, independentSegments: i = !1, start: a, source: r}) {
        super("playlist"), n(t), this.isMasterPlaylist = t, this.uri = e, this.version = s, this.independentSegments = i, this.start = a, this.source = r
    }
}

class O extends g {
    constructor(t = {}) {
        super(Object.assign(Object.assign({}, t), {isMasterPlaylist: !0}));
        const {variants: e = [], currentVariant: s, sessionDataList: i = [], sessionKeyList: n = []} = t;
        this.variants = e, this.currentVariant = s, this.sessionDataList = i, this.sessionKeyList = n
    }
}

class D extends g {
    constructor(t = {}) {
        super(Object.assign(Object.assign({}, t), {isMasterPlaylist: !1}));
        const {
            targetDuration: e,
            mediaSequenceBase: s = 0,
            discontinuitySequenceBase: i = 0,
            endlist: n = !1,
            playlistType: a,
            isIFrame: r,
            segments: o = [],
            prefetchSegments: E = [],
            lowLatencyCompatibility: T,
            partTargetDuration: u,
            renditionReports: c = [],
            skip: l = 0,
            hash: h
        } = t;
        this.targetDuration = e, this.mediaSequenceBase = s, this.discontinuitySequenceBase = i, this.endlist = n, this.playlistType = a, this.isIFrame = r, this.segments = o, this.prefetchSegments = E, this.lowLatencyCompatibility = T, this.partTargetDuration = u, this.renditionReports = c, this.skip = l, this.hash = h
    }
}

class P extends m {
    constructor({
                    uri: t,
                    mimeType: e,
                    data: s,
                    duration: i,
                    title: n,
                    byterange: a,
                    discontinuity: r,
                    mediaSequenceNumber: o = 0,
                    discontinuitySequence: E = 0,
                    key: T,
                    map: u,
                    programDateTime: c,
                    dateRange: l,
                    markers: h = [],
                    parts: X = []
                }) {
        super("segment"), this.uri = t, this.mimeType = e, this.data = s, this.duration = i, this.title = n, this.byterange = a, this.discontinuity = r, this.mediaSequenceNumber = o, this.discontinuitySequence = E, this.key = T, this.map = u, this.programDateTime = c, this.dateRange = l, this.markers = h, this.parts = X
    }
}

class y extends m {
    constructor({hint: t = !1, uri: e, duration: s, independent: i, byterange: a, gap: r}) {
        super("part"), n(e), this.hint = t, this.uri = e, this.duration = s, this.independent = i, this.duration = s, this.byterange = a, this.gap = r
    }
}

class C extends m {
    constructor({uri: t, discontinuity: e, mediaSequenceNumber: s = 0, discontinuitySequence: i = 0, key: a}) {
        super("prefetch"), n(t), this.uri = t, this.discontinuity = e, this.mediaSequenceNumber = s, this.discontinuitySequence = i, this.key = a
    }
}

class U {
    constructor({uri: t, lastMSN: e, lastPart: s}) {
        n(t), this.uri = t, this.lastMSN = e, this.lastPart = s
    }
}

var M = Object.freeze({
    __proto__: null,
    Rendition: I,
    Variant: N,
    SessionData: d,
    Key: A,
    MediaInitializationSection: f,
    DateRange: S,
    SpliceInfo: R,
    Playlist: g,
    MasterPlaylist: O,
    MediaPlaylist: D,
    Segment: P,
    PartialSegment: y,
    PrefetchSegment: C,
    RenditionReport: U
});

function b(t) {
    return function (t, e = " ") {
        return t ? (t = t.trim(), " " === e || (t.startsWith(e) && (t = t.slice(1)), t.endsWith(e) && (t = t.slice(0, -1))), t) : t
    }(t, '"')
}

function L(t) {
    const e = u(t, ",");
    return {duration: o(e[0]), title: decodeURIComponent(escape(e[1]))}
}

function v(t) {
    const e = u(t, "@");
    return {length: o(e[0]), offset: e[1] ? o(e[1]) : -1}
}

function $(t) {
    const e = u(t, "x");
    return {width: o(e[0]), height: o(e[1])}
}

function Y(t) {
    const e = "ALLOWED-CPC: Each entry must consit of KEYFORMAT and Content Protection Configuration", s = t.split(",");
    0 === s.length && r(e);
    const i = [];
    for (const t of s) {
        const [s, n] = u(t, ":");
        s && n ? i.push({format: s, cpcList: n.split("/")}) : r(e)
    }
    return i
}

function F(t) {
    const e = E(t);
    return 16 !== e.length && r("IV must be a 128-bit unsigned integer"), e
}

function G(t, e) {
    e.IV && t.compatibleVersion < 2 && (t.compatibleVersion = 2), (e.KEYFORMAT || e.KEYFORMATVERSIONS) && t.compatibleVersion < 5 && (t.compatibleVersion = 5)
}

function V(t) {
    const e = {};
    for (const i of function (t) {
        const e = [];
        let s = !0, i = 0;
        const n = [];
        for (let a = 0; a < t.length; a++) {
            const r = t[a];
            s && "," === r ? (e.push(t.slice(i, a).trim()), i = a + 1) : '"' !== r && "'" !== r || (s ? (n.push(r), s = !1) : r === p(n, -1) ? (n.pop(), s = !0) : n.push(r))
        }
        return e.push(t.slice(i).trim()), e
    }(t)) {
        const [t, n] = u(i, "="), a = b(n);
        switch (t) {
            case"URI":
                e[t] = a;
                break;
            case"START-DATE":
            case"END-DATE":
                e[t] = new Date(a);
                break;
            case"IV":
                e[t] = F(a);
                break;
            case"BYTERANGE":
                e[t] = v(a);
                break;
            case"RESOLUTION":
                e[t] = $(a);
                break;
            case"ALLOWED-CPC":
                e[t] = Y(a);
                break;
            case"END-ON-NEXT":
            case"DEFAULT":
            case"AUTOSELECT":
            case"FORCED":
            case"PRECISE":
            case"CAN-BLOCK-RELOAD":
            case"INDEPENDENT":
            case"GAP":
                e[t] = "YES" === a;
                break;
            case"DURATION":
            case"PLANNED-DURATION":
            case"BANDWIDTH":
            case"AVERAGE-BANDWIDTH":
            case"FRAME-RATE":
            case"TIME-OFFSET":
            case"CAN-SKIP-UNTIL":
            case"HOLD-BACK":
            case"PART-HOLD-BACK":
            case"PART-TARGET":
            case"BYTERANGE-START":
            case"BYTERANGE-LENGTH":
            case"LAST-MSN":
            case"LAST-PART":
            case"SKIPPED-SEGMENTS":
            case"SCORE":
            case"PROGRAM-ID":
                e[t] = o(a);
                break;
            default:
                t.startsWith("SCTE35-") ? e[t] = E(a) : t.startsWith("X-") ? e[t] = (s = n).startsWith('"') ? b(s) : s.startsWith("0x") || s.startsWith("0X") ? E(s) : o(s) : ("VIDEO-RANGE" === t && "SDR" !== a && "HLG" !== a && "PQ" !== a && r(`VIDEO-RANGE: unknown value "${a}"`), e[t] = a)
        }
    }
    var s;
    return e
}

function w() {
    r("The file contains both media and master playlist tags.")
}

function B(t, e, s) {
    const i = function ({attributes: t}) {
        return new I({
            type: t.TYPE,
            uri: t.URI,
            groupId: t["GROUP-ID"],
            language: t.LANGUAGE,
            assocLanguage: t["ASSOC-LANGUAGE"],
            name: t.NAME,
            isDefault: t.DEFAULT,
            autoselect: t.AUTOSELECT,
            forced: t.FORCED,
            instreamId: t["INSTREAM-ID"],
            characteristics: t.CHARACTERISTICS,
            channels: t.CHANNELS
        })
    }(e), n = t[c(s)], a = function (t, e) {
        let s = !1;
        for (const i of t) {
            if (i.name === e.name) return "All EXT-X-MEDIA tags in the same Group MUST have different NAME attributes.";
            i.isDefault && (s = !0)
        }
        return s && e.isDefault ? "EXT-X-MEDIA A Group MUST NOT have more than one member with a DEFAULT attribute of YES." : ""
    }(n, i);
    a && r(a), n.push(i), i.isDefault && (t.currentRenditions[c(s)] = n.length - 1)
}

function H(t, e, s, i, n) {
    const a = new N({
        uri: s,
        bandwidth: e.BANDWIDTH,
        averageBandwidth: e["AVERAGE-BANDWIDTH"],
        score: e.SCORE,
        codecs: e.CODECS,
        resolution: e.RESOLUTION,
        frameRate: e["FRAME-RATE"],
        hdcpLevel: e["HDCP-LEVEL"],
        allowedCpc: e["ALLOWED-CPC"],
        videoRange: e["VIDEO-RANGE"],
        stableVariantId: e["STABLE-VARIANT-ID"],
        programId: e["PROGRAM-ID"]
    });
    for (const s of t) if ("EXT-X-MEDIA" === s.name) {
        const t = s.attributes, i = t.TYPE;
        if (i && t["GROUP-ID"] || r("EXT-X-MEDIA TYPE attribute is REQUIRED."), e[i] === t["GROUP-ID"] && (B(a, s, i), "CLOSED-CAPTIONS" === i)) for (const {instreamId: t} of a.closedCaptions) if (t && t.startsWith("SERVICE") && n.compatibleVersion < 7) {
            n.compatibleVersion = 7;
            break
        }
    }
    return function (t, e, s) {
        for (const i of ["AUDIO", "VIDEO", "SUBTITLES", "CLOSED-CAPTIONS"]) "CLOSED-CAPTIONS" === i && "NONE" === t[i] ? (s.isClosedCaptionsNone = !0, e.closedCaptions = []) : t[i] && !e[c(i)].some((e => e.groupId === t[i])) && r(`${i} attribute MUST match the value of the GROUP-ID attribute of an EXT-X-MEDIA tag whose TYPE attribute is ${i}.`)
    }(e, a, n), a.isIFrameOnly = i, a
}

function K(t, e) {
    if (t.method !== e.method) return !1;
    if (t.uri !== e.uri) return !1;
    if (t.iv) {
        if (!e.iv) return !1;
        if (t.iv.length !== e.iv.length) return !1;
        for (let s = 0; s < t.iv.length; s++) if (t.iv[s] !== e.iv[s]) return !1
    } else if (e.iv) return !1;
    return t.format === e.format && t.formatVersion === e.formatVersion
}

function k(t, e, s, i, n, a, o) {
    const E = new P({uri: e, mediaSequenceNumber: n, discontinuitySequence: a});
    let T = !1, u = !1;
    for (let e = s; e <= i; e++) {
        const {name: s, value: i, attributes: n} = t[e];
        if ("EXTINF" === s) !Number.isInteger(i.duration) && o.compatibleVersion < 3 && (o.compatibleVersion = 3), Math.round(i.duration) > o.targetDuration && r("EXTINF duration, when rounded to the nearest integer, MUST be less than or equal to the target duration"), E.duration = i.duration, E.title = i.title; else if ("EXT-X-BYTERANGE" === s) o.compatibleVersion < 4 && (o.compatibleVersion = 4), E.byterange = i; else if ("EXT-X-DISCONTINUITY" === s) E.parts.length > 0 && r("EXT-X-DISCONTINUITY must appear before the first EXT-X-PART tag of the Parent Segment."), E.discontinuity = !0; else if ("EXT-X-KEY" === s) E.parts.length > 0 && r("EXT-X-KEY must appear before the first EXT-X-PART tag of the Parent Segment."), G(o, n), E.key = new A({
            method: n.METHOD,
            uri: n.URI,
            iv: n.IV,
            format: n.KEYFORMAT,
            formatVersion: n.KEYFORMATVERSIONS
        }); else if ("EXT-X-MAP" === s) E.parts.length > 0 && r("EXT-X-MAP must appear before the first EXT-X-PART tag of the Parent Segment."), o.compatibleVersion < 5 && (o.compatibleVersion = 5), o.hasMap = !0, E.map = new f({
            uri: n.URI,
            byterange: n.BYTERANGE
        }); else if ("EXT-X-PROGRAM-DATE-TIME" === s) E.programDateTime = i; else if ("EXT-X-DATERANGE" === s) {
            const t = {};
            for (const e of Object.keys(n)) (e.startsWith("SCTE35-") || e.startsWith("X-")) && (t[e] = n[e]);
            E.dateRange = new S({
                id: n.ID,
                classId: n.CLASS,
                start: n["START-DATE"],
                end: n["END-DATE"],
                duration: n.DURATION,
                plannedDuration: n["PLANNED-DURATION"],
                endOnNext: n["END-ON-NEXT"],
                attributes: t
            })
        } else if ("EXT-X-CUE-OUT" === s) E.markers.push(new R({
            type: "OUT",
            duration: n && n.DURATION || i
        })); else if ("EXT-X-CUE-IN" === s) E.markers.push(new R({type: "IN"})); else if ("EXT-X-CUE-OUT-CONT" === s || "EXT-X-CUE" === s || "EXT-OATCLS-SCTE35" === s || "EXT-X-ASSET" === s || "EXT-X-SCTE35" === s) E.markers.push(new R({
            type: "RAW",
            tagName: s,
            value: i
        })); else if ("EXT-X-PRELOAD-HINT" !== s || n.TYPE) if ("EXT-X-PRELOAD-HINT" === s && "PART" === n.TYPE && u) r("Servers should not add more than one EXT-X-PRELOAD-HINT tag with the same TYPE attribute to a Playlist."); else if ("EXT-X-PART" !== s && "EXT-X-PRELOAD-HINT" !== s || n.URI) {
            if ("EXT-X-PRELOAD-HINT" === s && "MAP" === n.TYPE) T && r("Servers should not add more than one EXT-X-PRELOAD-HINT tag with the same TYPE attribute to a Playlist."), T = !0, o.hasMap = !0, E.map = new f({
                hint: !0,
                uri: n.URI,
                byterange: {length: n["BYTERANGE-LENGTH"], offset: n["BYTERANGE-START"] || 0}
            }); else if ("EXT-X-PART" === s || "EXT-X-PRELOAD-HINT" === s && "PART" === n.TYPE) {
                "EXT-X-PART" !== s || n.DURATION || r("EXT-X-PART: DURATION attribute is mandatory"), "EXT-X-PRELOAD-HINT" === s && (u = !0);
                const t = new y({
                    hint: "EXT-X-PRELOAD-HINT" === s,
                    uri: n.URI,
                    byterange: "EXT-X-PART" === s ? n.BYTERANGE : {
                        length: n["BYTERANGE-LENGTH"],
                        offset: n["BYTERANGE-START"] || 0
                    },
                    duration: n.DURATION,
                    independent: n.INDEPENDENT,
                    gap: n.GAP
                });
                E.parts.push(t)
            }
        } else r("EXT-X-PART / EXT-X-PRELOAD-HINT: URI attribute is mandatory"); else r("EXT-X-PRELOAD-HINT: TYPE attribute is mandatory")
    }
    return E
}

function W(t, e, s, i, n, a, o) {
    const E = new C({uri: e, mediaSequenceNumber: n, discontinuitySequence: a});
    for (let e = s; e <= i; e++) {
        const {name: s, attributes: i} = t[e];
        "EXTINF" === s ? r("A prefetch segment must not be advertised with an EXTINF tag.") : "EXT-X-DISCONTINUITY" === s ? r("A prefetch segment must not be advertised with an EXT-X-DISCONTINUITY tag.") : "EXT-X-PREFETCH-DISCONTINUITY" === s ? E.discontinuity = !0 : "EXT-X-KEY" === s ? (G(o, i), E.key = new A({
            method: i.METHOD,
            uri: i.URI,
            iv: i.IV,
            format: i.KEYFORMAT,
            formatVersion: i.KEYFORMATVERSIONS
        })) : "EXT-X-MAP" === s && r("Prefetch segments must not be advertised with an EXT-X-MAP tag.")
    }
    return E
}

function q(t, e) {
    var s;
    const i = new D;
    let n = -1, a = 0, o = !1, E = !1, T = 0, u = null, c = null, l = !1;
    for (const [s, h] of t.entries()) {
        const {name: X, value: p, attributes: I, category: N} = h;
        if ("Segment" !== N) {
            if ("EXT-X-VERSION" === X) void 0 === i.version ? i.version = p : r("A Playlist file MUST NOT contain more than one EXT-X-VERSION tag."); else if ("EXT-X-TARGETDURATION" === X) i.targetDuration = e.targetDuration = p; else if ("EXT-X-MEDIA-SEQUENCE" === X) i.segments.length > 0 && r("The EXT-X-MEDIA-SEQUENCE tag MUST appear before the first Media Segment in the Playlist."), i.mediaSequenceBase = a = p; else if ("EXT-X-DISCONTINUITY-SEQUENCE" === X) i.segments.length > 0 && r("The EXT-X-DISCONTINUITY-SEQUENCE tag MUST appear before the first Media Segment in the Playlist."), o && r("The EXT-X-DISCONTINUITY-SEQUENCE tag MUST appear before any EXT-X-DISCONTINUITY tag."), i.discontinuitySequenceBase = T = p; else if ("EXT-X-ENDLIST" === X) i.endlist = !0; else if ("EXT-X-PLAYLIST-TYPE" === X) i.playlistType = p; else if ("EXT-X-I-FRAMES-ONLY" === X) e.compatibleVersion < 4 && (e.compatibleVersion = 4), i.isIFrame = !0; else if ("EXT-X-INDEPENDENT-SEGMENTS" === X) i.independentSegments && r("EXT-X-INDEPENDENT-SEGMENTS tag MUST NOT appear more than once in a Playlist"), i.independentSegments = !0; else if ("EXT-X-START" === X) i.start && r("EXT-X-START tag MUST NOT appear more than once in a Playlist"), "number" != typeof I["TIME-OFFSET"] && r("EXT-X-START: TIME-OFFSET attribute is REQUIRED"), i.start = {
                offset: I["TIME-OFFSET"],
                precise: I.PRECISE || !1
            }; else if ("EXT-X-SERVER-CONTROL" === X) I["CAN-BLOCK-RELOAD"] || r("EXT-X-SERVER-CONTROL: CAN-BLOCK-RELOAD=YES is mandatory for Low-Latency HLS"), i.lowLatencyCompatibility = {
                canBlockReload: I["CAN-BLOCK-RELOAD"],
                canSkipUntil: I["CAN-SKIP-UNTIL"],
                holdBack: I["HOLD-BACK"],
                partHoldBack: I["PART-HOLD-BACK"]
            }; else if ("EXT-X-PART-INF" === X) I["PART-TARGET"] || r("EXT-X-PART-INF: PART-TARGET attribute is mandatory"), i.partTargetDuration = I["PART-TARGET"]; else if ("EXT-X-RENDITION-REPORT" === X) I.URI || r("EXT-X-RENDITION-REPORT: URI attribute is mandatory"), 0 === I.URI.search(/^[a-z]+:/) && r("EXT-X-RENDITION-REPORT: URI must be relative to the playlist uri"), i.renditionReports.push(new U({
                uri: I.URI,
                lastMSN: I["LAST-MSN"],
                lastPart: I["LAST-PART"]
            })); else if ("EXT-X-SKIP" === X) I["SKIPPED-SEGMENTS"] || r("EXT-X-SKIP: SKIPPED-SEGMENTS attribute is mandatory"), e.compatibleVersion < 9 && (e.compatibleVersion = 9), i.skip = I["SKIPPED-SEGMENTS"], a += i.skip; else if ("EXT-X-PREFETCH" === X) {
                const r = W(t, p, -1 === n ? s : n, s - 1, a++, T, e);
                r && (r.discontinuity && (r.discontinuitySequence++, T = r.discontinuitySequence), r.key ? u = r.key : r.key = u, i.prefetchSegments.push(r)), E = !0, n = -1
            } else if ("string" == typeof h) {
                -1 === n && r("A URI line is not preceded by any segment tags"), i.targetDuration || r("The EXT-X-TARGETDURATION tag is REQUIRED"), E && r("These segments must appear after all complete segments.");
                const o = k(t, h, n, s - 1, a++, T, e);
                o && ([T, u, c] = x(i, o, T, u, c), !l && o.parts.length > 0 && (l = !0)), n = -1
            }
        } else -1 === n && (n = s), "EXT-X-DISCONTINUITY" === X && (o = !0)
    }
    if (-1 !== n) {
        const o = k(t, "", n, t.length - 1, a++, T, e);
        if (o) {
            const {parts: t} = o;
            t.length > 0 && !i.endlist && !(null === (s = p(t, -1)) || void 0 === s ? void 0 : s.hint) && r("If the Playlist contains EXT-X-PART tags and does not contain an EXT-X-ENDLIST tag, the Playlist must contain an EXT-X-PRELOAD-HINT tag with a TYPE=PART attribute"), x(i, o, u, c), !l && o.parts.length > 0 && (l = !0)
        }
    }
    return function (t) {
        const e = new Map, s = new Map;
        let i = !1, n = !1;
        for (let a = t.length - 1; a >= 0; a--) {
            const {programDateTime: o, dateRange: E} = t[a];
            if (o && (n = !0), E && E.start) {
                i = !0, E.endOnNext && (E.end || E.duration) && r("An EXT-X-DATERANGE tag with an END-ON-NEXT=YES attribute MUST NOT contain DURATION or END-DATE attributes.");
                const t = E.start.getTime(), n = E.duration || 0;
                E.end && E.duration && t + 1e3 * n !== E.end.getTime() && r("END-DATE MUST be equal to the value of the START-DATE attribute plus the value of the DURATION"), E.endOnNext && (E.end = e.get(E.classId)), e.set(E.classId, E.start);
                const a = E.end ? E.end.getTime() : E.start.getTime() + 1e3 * (E.duration || 0), o = s.get(E.classId);
                if (o) {
                    for (const e of o) (e.start <= t && e.end > t || e.start >= t && e.start < a) && r("DATERANGE tags with the same CLASS should not overlap");
                    o.push({start: t, end: a})
                } else E.classId && s.set(E.classId, [{start: t, end: a}])
            }
        }
        i && !n && r("If a Playlist contains an EXT-X-DATERANGE tag, it MUST also contain at least one EXT-X-PROGRAM-DATE-TIME tag.")
    }(i.segments), i.lowLatencyCompatibility && function ({
                                                              lowLatencyCompatibility: t,
                                                              targetDuration: e,
                                                              partTargetDuration: s,
                                                              segments: i,
                                                              renditionReports: n
                                                          }, a) {
        const {canSkipUntil: o, holdBack: E, partHoldBack: T} = t;
        o < 6 * e && r("The Skip Boundary must be at least six times the EXT-X-TARGETDURATION.");
        E < 3 * e && r("HOLD-BACK must be at least three times the EXT-X-TARGETDURATION.");
        if (a) {
            void 0 === s && r("EXT-X-PART-INF is required if a Playlist contains one or more EXT-X-PART tags"), void 0 === T && r("EXT-X-PART: PART-HOLD-BACK attribute is mandatory"), T < s && r("PART-HOLD-BACK must be at least PART-TARGET");
            for (const [t, {parts: e}] of i.entries()) {
                e.length > 0 && t < i.length - 3 && r("Remove EXT-X-PART tags from the Playlist after they are greater than three target durations from the end of the Playlist.");
                for (const [t, {duration: i}] of e.entries()) void 0 !== i && (i > s && r("PART-TARGET is the maximum duration of any Partial Segment"), t < e.length - 1 && i < .85 * s && r("All Partial Segments except the last part of a segment must have a duration of at least 85% of PART-TARGET"))
            }
        }
        for (const t of n) {
            const e = i.at(-1);
            null !== t.lastMSN && void 0 !== t.lastMSN || (t.lastMSN = e.mediaSequenceNumber), (null === t.lastPart || void 0 === t.lastPart) && e.parts.length > 0 && (t.lastPart = e.parts.length - 1)
        }
    }(i, l), i
}

function x(t, e, s, i, n) {
    const {discontinuity: a, key: o, map: E, byterange: T, uri: u} = e;
    if (a && (e.discontinuitySequence = s + 1), o || (e.key = i), E || (e.map = n), T && -1 === T.offset) {
        const {segments: e} = t;
        if (e.length > 0) {
            const t = p(e, -1);
            t.byterange && t.uri === u ? T.offset = t.byterange.offset + t.byterange.length : r("If offset of EXT-X-BYTERANGE is not present, a previous Media Segment MUST be a sub-range of the same media resource")
        } else r("If offset of EXT-X-BYTERANGE is not present, a previous Media Segment MUST appear in the Playlist file")
    }
    return t.segments.push(e), [e.discontinuitySequence, e.key, e.map]
}

function j(t, e) {
    const [s, i] = function (t) {
        const e = t.indexOf(":");
        return -1 === e ? [t.slice(1).trim(), null] : [t.slice(1, e).trim(), t.slice(e + 1).trim()]
    }(t), n = function (t) {
        switch (t) {
            case"EXTM3U":
            case"EXT-X-VERSION":
                return "Basic";
            case"EXTINF":
            case"EXT-X-BYTERANGE":
            case"EXT-X-DISCONTINUITY":
            case"EXT-X-PREFETCH-DISCONTINUITY":
            case"EXT-X-KEY":
            case"EXT-X-MAP":
            case"EXT-X-PROGRAM-DATE-TIME":
            case"EXT-X-DATERANGE":
            case"EXT-X-CUE-OUT":
            case"EXT-X-CUE-IN":
            case"EXT-X-CUE-OUT-CONT":
            case"EXT-X-CUE":
            case"EXT-OATCLS-SCTE35":
            case"EXT-X-ASSET":
            case"EXT-X-SCTE35":
            case"EXT-X-PART":
            case"EXT-X-PRELOAD-HINT":
                return "Segment";
            case"EXT-X-TARGETDURATION":
            case"EXT-X-MEDIA-SEQUENCE":
            case"EXT-X-DISCONTINUITY-SEQUENCE":
            case"EXT-X-ENDLIST":
            case"EXT-X-PLAYLIST-TYPE":
            case"EXT-X-I-FRAMES-ONLY":
            case"EXT-X-SERVER-CONTROL":
            case"EXT-X-PART-INF":
            case"EXT-X-PREFETCH":
            case"EXT-X-RENDITION-REPORT":
            case"EXT-X-SKIP":
                return "MediaPlaylist";
            case"EXT-X-MEDIA":
            case"EXT-X-STREAM-INF":
            case"EXT-X-I-FRAME-STREAM-INF":
            case"EXT-X-SESSION-DATA":
            case"EXT-X-SESSION-KEY":
                return "MasterPlaylist";
            case"EXT-X-INDEPENDENT-SEGMENTS":
            case"EXT-X-START":
                return "MediaorMasterPlaylist";
            default:
                return "Unknown"
        }
    }(s);
    if (function (t, e) {
        if ("Segment" === t || "MediaPlaylist" === t) return void 0 === e.isMasterPlaylist ? void (e.isMasterPlaylist = !1) : void (e.isMasterPlaylist && w());
        if ("MasterPlaylist" === t) {
            if (void 0 === e.isMasterPlaylist) return void (e.isMasterPlaylist = !0);
            !1 === e.isMasterPlaylist && w()
        }
    }(n, e), "Unknown" === n) return null;
    "MediaPlaylist" === n && "EXT-X-RENDITION-REPORT" !== s && "EXT-X-PREFETCH" !== s && (e.hash[s] && r("There MUST NOT be more than one Media Playlist tag of each type in any Media Playlist"), e.hash[s] = !0);
    const [a, E] = function (t, e) {
        switch (t) {
            case"EXTM3U":
            case"EXT-X-DISCONTINUITY":
            case"EXT-X-ENDLIST":
            case"EXT-X-I-FRAMES-ONLY":
            case"EXT-X-INDEPENDENT-SEGMENTS":
            case"EXT-X-CUE-IN":
                return [null, null];
            case"EXT-X-VERSION":
            case"EXT-X-TARGETDURATION":
            case"EXT-X-MEDIA-SEQUENCE":
            case"EXT-X-DISCONTINUITY-SEQUENCE":
                return [o(e), null];
            case"EXT-X-CUE-OUT":
                return Number.isNaN(Number(e)) ? [null, V(e)] : [o(e), null];
            case"EXT-X-KEY":
            case"EXT-X-MAP":
            case"EXT-X-DATERANGE":
            case"EXT-X-MEDIA":
            case"EXT-X-STREAM-INF":
            case"EXT-X-I-FRAME-STREAM-INF":
            case"EXT-X-SESSION-DATA":
            case"EXT-X-SESSION-KEY":
            case"EXT-X-START":
            case"EXT-X-SERVER-CONTROL":
            case"EXT-X-PART-INF":
            case"EXT-X-PART":
            case"EXT-X-PRELOAD-HINT":
            case"EXT-X-RENDITION-REPORT":
            case"EXT-X-SKIP":
                return [null, V(e)];
            case"EXTINF":
                return [L(e), null];
            case"EXT-X-BYTERANGE":
                return [v(e), null];
            case"EXT-X-PROGRAM-DATE-TIME":
                return [new Date(e), null];
            default:
                return [e, null]
        }
    }(s, i);
    return {name: s, category: n, value: a, attributes: E}
}

function Q(t, e) {
    let s;
    return e.isMasterPlaylist ? s = function (t, e) {
        const s = new O;
        let i = !1;
        for (const [n, {
            name: a,
            value: o,
            attributes: E
        }] of t.entries()) if ("EXT-X-VERSION" === a) s.version = o; else if ("EXT-X-STREAM-INF" === a) {
            const a = t[n + 1];
            ("string" != typeof a || a.startsWith("#EXT")) && r("EXT-X-STREAM-INF must be followed by a URI line");
            const o = H(t, E, a, !1, e);
            o && ("number" == typeof o.score && (i = !0, o.score < 0 && r("SCORE attribute on EXT-X-STREAM-INF must be positive decimal-floating-point number.")), s.variants.push(o))
        } else if ("EXT-X-I-FRAME-STREAM-INF" === a) {
            const i = H(t, E, E.URI, !0, e);
            i && s.variants.push(i)
        } else if ("EXT-X-SESSION-DATA" === a) {
            const t = new d({id: E["DATA-ID"], value: E.VALUE, uri: E.URI, language: E.LANGUAGE});
            s.sessionDataList.some((e => e.id === t.id && e.language === t.language)) && r("A Playlist MUST NOT contain more than one EXT-X-SESSION-DATA tag with the same DATA-ID attribute and the same LANGUAGE attribute."), s.sessionDataList.push(t)
        } else if ("EXT-X-SESSION-KEY" === a) {
            "NONE" === E.METHOD && r("EXT-X-SESSION-KEY: The value of the METHOD attribute MUST NOT be NONE");
            const t = new A({
                method: E.METHOD,
                uri: E.URI,
                iv: E.IV,
                format: E.KEYFORMAT,
                formatVersion: E.KEYFORMATVERSIONS
            });
            s.sessionKeyList.some((e => K(e, t))) && r("A Master Playlist MUST NOT contain more than one EXT-X-SESSION-KEY tag with the same METHOD, URI, IV, KEYFORMAT, and KEYFORMATVERSIONS attribute values."), G(e, E), s.sessionKeyList.push(t)
        } else "EXT-X-INDEPENDENT-SEGMENTS" === a ? (s.independentSegments && r("EXT-X-INDEPENDENT-SEGMENTS tag MUST NOT appear more than once in a Playlist"), s.independentSegments = !0) : "EXT-X-START" === a && (s.start && r("EXT-X-START tag MUST NOT appear more than once in a Playlist"), "number" != typeof E["TIME-OFFSET"] && r("EXT-X-START: TIME-OFFSET attribute is REQUIRED"), s.start = {
            offset: E["TIME-OFFSET"],
            precise: E.PRECISE || !1
        });
        if (i) for (const t of s.variants) "number" != typeof t.score && r("If any Variant Stream contains the SCORE attribute, then all Variant Streams in the Master Playlist SHOULD have a SCORE attribute");
        if (e.isClosedCaptionsNone) for (const t of s.variants) t.closedCaptions.length > 0 && r("If there is a variant with CLOSED-CAPTIONS attribute of NONE, all EXT-X-STREAM-INF tags MUST have this attribute with a value of NONE");
        return s
    }(t, e) : (s = q(t, e), !s.isIFrame && e.hasMap && e.compatibleVersion < 6 && (e.compatibleVersion = 6)), e.compatibleVersion > 1 && (!s.version || s.version < e.compatibleVersion) && r(`EXT-X-VERSION needs to be ${e.compatibleVersion} or higher.`), s
}

function _(t) {
    const e = {
        version: void 0,
        isMasterPlaylist: void 0,
        hasMap: !1,
        targetDuration: 0,
        compatibleVersion: 1,
        isClosedCaptionsNone: !1,
        hash: {}
    }, s = function (t, e) {
        const s = [];
        for (const i of t.split("\n")) {
            const t = i.trim();
            if (t) if (t.startsWith("#")) {
                if (t.startsWith("#EXT")) {
                    const i = j(t, e);
                    i && s.push(i)
                }
            } else s.push(t)
        }
        return 0 !== s.length && "EXTM3U" === s[0].name || r("The EXTM3U tag MUST be the first line."), s
    }(t, e), i = Q(s, e);
    return i.source = t, i
}

const z = ["#EXTINF", "#EXT-X-BYTERANGE", "#EXT-X-DISCONTINUITY", "#EXT-X-STREAM-INF", "#EXT-X-CUE-OUT", "#EXT-X-CUE-IN", "#EXT-X-KEY", "#EXT-X-MAP"],
    Z = ["#EXT-X-MEDIA"];

class J extends Array {
    constructor(t) {
        super(), this.baseUri = t
    }

    push(...t) {
        for (const e of t) if (e.startsWith("#")) if (z.some((t => e.startsWith(t)))) super.push(e); else {
            if (this.includes(e)) {
                if (Z.some((t => e.startsWith(t)))) continue;
                r(`Redundant item (${e})`)
            }
            super.push(e)
        } else super.push(e);
        return this.length
    }
}

function tt(t, e) {
    let s = 1e3;
    e && (s = Math.pow(10, e));
    const i = Math.round(t * s) / s;
    return e ? i.toFixed(e) : i
}

function et(t) {
    const e = [`DATA-ID="${t.id}"`];
    return t.language && e.push(`LANGUAGE="${t.language}"`), t.value ? e.push(`VALUE="${t.value}"`) : t.uri && e.push(`URI="${t.uri}"`), `#EXT-X-SESSION-DATA:${e.join(",")}`
}

function st(t, e) {
    const s = e ? "#EXT-X-SESSION-KEY" : "#EXT-X-KEY", i = [`METHOD=${t.method}`];
    return t.uri && i.push(`URI="${t.uri}"`), t.iv && (16 !== t.iv.length && r("IV must be a 128-bit unsigned integer"), i.push(`IV=${T(t.iv)}`)), t.format && i.push(`KEYFORMAT="${t.format}"`), t.formatVersion && i.push(`KEYFORMATVERSIONS="${t.formatVersion}"`), `${s}:${i.join(",")}`
}

function it(t, e) {
    const s = e.isIFrameOnly ? "#EXT-X-I-FRAME-STREAM-INF" : "#EXT-X-STREAM-INF", i = [`BANDWIDTH=${e.bandwidth}`];
    if (e.averageBandwidth && i.push(`AVERAGE-BANDWIDTH=${e.averageBandwidth}`), e.isIFrameOnly && i.push(`URI="${e.uri}"`), e.codecs && i.push(`CODECS="${e.codecs}"`), e.resolution && i.push(`RESOLUTION=${e.resolution.width}x${e.resolution.height}`), e.frameRate && i.push(`FRAME-RATE=${tt(e.frameRate, 3)}`), e.hdcpLevel && i.push(`HDCP-LEVEL=${e.hdcpLevel}`), e.audio.length > 0) {
        i.push(`AUDIO="${e.audio[0].groupId}"`);
        for (const s of e.audio) t.push(nt(s))
    }
    if (e.video.length > 0) {
        i.push(`VIDEO="${e.video[0].groupId}"`);
        for (const s of e.video) t.push(nt(s))
    }
    if (e.subtitles.length > 0) {
        i.push(`SUBTITLES="${e.subtitles[0].groupId}"`);
        for (const s of e.subtitles) t.push(nt(s))
    }
    if (X().allowClosedCaptionsNone && 0 === e.closedCaptions.length) i.push("CLOSED-CAPTIONS=NONE"); else if (e.closedCaptions.length > 0) {
        i.push(`CLOSED-CAPTIONS="${e.closedCaptions[0].groupId}"`);
        for (const s of e.closedCaptions) t.push(nt(s))
    }
    if (e.score && i.push(`SCORE=${e.score}`), e.allowedCpc) {
        const t = [];
        for (const {format: s, cpcList: i} of e.allowedCpc) t.push(`${s}:${i.join("/")}`);
        i.push(`ALLOWED-CPC="${t.join(",")}"`)
    }
    e.videoRange && i.push(`VIDEO-RANGE=${e.videoRange}`), e.stableVariantId && i.push(`STABLE-VARIANT-ID="${e.stableVariantId}"`), e.programId && i.push(`PROGRAM-ID=${e.programId}`), t.push(`${s}:${i.join(",")}`), e.isIFrameOnly || t.push(`${e.uri}`)
}

function nt(t) {
    const e = [`TYPE=${t.type}`, `GROUP-ID="${t.groupId}"`, `NAME="${t.name}"`];
    return void 0 !== t.isDefault && e.push("DEFAULT=" + (t.isDefault ? "YES" : "NO")), void 0 !== t.autoselect && e.push("AUTOSELECT=" + (t.autoselect ? "YES" : "NO")), void 0 !== t.forced && e.push("FORCED=" + (t.forced ? "YES" : "NO")), t.language && e.push(`LANGUAGE="${t.language}"`), t.assocLanguage && e.push(`ASSOC-LANGUAGE="${t.assocLanguage}"`), t.instreamId && e.push(`INSTREAM-ID="${t.instreamId}"`), t.characteristics && e.push(`CHARACTERISTICS="${t.characteristics}"`), t.channels && e.push(`CHANNELS="${t.channels}"`), t.uri && e.push(`URI="${t.uri}"`), `#EXT-X-MEDIA:${e.join(",")}`
}

function at(t, e, s, i, n = 1, a = null) {
    let r = !1, o = "";
    if (e.discontinuity && t.push("#EXT-X-DISCONTINUITY"), e.key) {
        const i = st(e.key);
        i !== s && (t.push(i), s = i)
    }
    if (e.map) {
        const s = function (t) {
            const e = [`URI="${t.uri}"`];
            t.byterange && e.push(`BYTERANGE="${rt(t.byterange)}"`);
            return `#EXT-X-MAP:${e.join(",")}`
        }(e.map);
        s !== i && (t.push(s), i = s)
    }
    if (e.programDateTime && t.push(`#EXT-X-PROGRAM-DATE-TIME:${l(e.programDateTime)}`), e.dateRange && t.push(function (t) {
        const e = [`ID="${t.id}"`];
        t.start && e.push(`START-DATE="${l(t.start)}"`);
        t.end && e.push(`END-DATE="${l(t.end)}"`);
        t.duration && e.push(`DURATION=${t.duration}`);
        t.plannedDuration && e.push(`PLANNED-DURATION=${t.plannedDuration}`);
        t.classId && e.push(`CLASS="${t.classId}"`);
        t.endOnNext && e.push("END-ON-NEXT=YES");
        for (const s of Object.keys(t.attributes)) s.startsWith("X-") ? "number" == typeof t.attributes[s] ? e.push(`${s}=${t.attributes[s]}`) : e.push(`${s}="${t.attributes[s]}"`) : s.startsWith("SCTE35-") && e.push(`${s}=${T(t.attributes[s])}`);
        return `#EXT-X-DATERANGE:${e.join(",")}`
    }(e.dateRange)), e.markers.length > 0 && (o = function (t, e) {
        let s = "";
        for (const i of e) if ("OUT" === i.type) s = "OUT", t.push(`#EXT-X-CUE-OUT:DURATION=${i.duration}`); else if ("IN" === i.type) s = "IN", t.push("#EXT-X-CUE-IN"); else if ("RAW" === i.type) {
            const e = i.value ? `:${i.value}` : "";
            t.push(`#${i.tagName}${e}`)
        }
        return s
    }(t, e.markers)), e.parts.length > 0 && (r = function (t, e) {
        let s = !1;
        for (const i of e) if (i.hint) {
            const e = [];
            if (e.push("TYPE=PART", `URI="${i.uri}"`), i.byterange) {
                const {offset: t, length: s} = i.byterange;
                e.push(`BYTERANGE-START=${t}`), s && e.push(`BYTERANGE-LENGTH=${s}`)
            }
            t.push(`#EXT-X-PRELOAD-HINT:${e.join(",")}`), s = !0
        } else {
            const e = [];
            e.push(`DURATION=${i.duration}`, `URI="${i.uri}"`), i.byterange && e.push(`BYTERANGE=${rt(i.byterange)}`), i.independent && e.push("INDEPENDENT=YES"), i.gap && e.push("GAP=YES"), t.push(`#EXT-X-PART:${e.join(",")}`)
        }
        return s
    }(t, e.parts)), r) return [s, i];
    const E = n < 3 ? Math.round(e.duration) : tt(e.duration, function (t) {
        const e = t.toString(10), s = e.indexOf(".");
        return -1 === s ? 0 : e.length - s - 1
    }(e.duration));
    return t.push(`#EXTINF:${E},${unescape(encodeURIComponent(e.title || ""))}`), e.byterange && t.push(`#EXT-X-BYTERANGE:${rt(e.byterange)}`), null != a ? Array.prototype.push.call(t, a(e)) : Array.prototype.push.call(t, `${e.uri}`), [s, i, o]
}

function rt({offset: t, length: e}) {
    return `${e}@${t}`
}

function ot(t, e = null) {
    n(t), s("Not a playlist", "playlist" === t.type);
    const i = new J(t.uri);
    return i.push("#EXTM3U"), t.version && i.push(`#EXT-X-VERSION:${t.version}`), t.independentSegments && i.push("#EXT-X-INDEPENDENT-SEGMENTS"), t.start && i.push(`#EXT-X-START:TIME-OFFSET=${tt(t.start.offset)}${t.start.precise ? ",PRECISE=YES" : ""}`), t.isMasterPlaylist ? function (t, e) {
        for (const s of e.sessionDataList) t.push(et(s));
        for (const s of e.sessionKeyList) t.push(st(s, !0));
        for (const s of e.variants) it(t, s)
    }(i, t) : function (t, e, s = null) {
        let i = "", n = "", a = !1;
        if (e.targetDuration && t.push(`#EXT-X-TARGETDURATION:${e.targetDuration}`), e.lowLatencyCompatibility) {
            const {canBlockReload: s, canSkipUntil: i, holdBack: n, partHoldBack: a} = e.lowLatencyCompatibility,
                r = [];
            r.push("CAN-BLOCK-RELOAD=" + (s ? "YES" : "NO")), void 0 !== i && r.push(`CAN-SKIP-UNTIL=${i}`), void 0 !== n && r.push(`HOLD-BACK=${n}`), void 0 !== a && r.push(`PART-HOLD-BACK=${a}`), t.push(`#EXT-X-SERVER-CONTROL:${r.join(",")}`)
        }
        e.partTargetDuration && t.push(`#EXT-X-PART-INF:PART-TARGET=${e.partTargetDuration}`), e.mediaSequenceBase && t.push(`#EXT-X-MEDIA-SEQUENCE:${e.mediaSequenceBase}`), e.discontinuitySequenceBase && t.push(`#EXT-X-DISCONTINUITY-SEQUENCE:${e.discontinuitySequenceBase}`), e.playlistType && t.push(`#EXT-X-PLAYLIST-TYPE:${e.playlistType}`), e.isIFrame && t.push("#EXT-X-I-FRAMES-ONLY"), e.skip > 0 && t.push(`#EXT-X-SKIP:SKIPPED-SEGMENTS=${e.skip}`);
        for (const r of e.segments) {
            let o = "";
            [i, n, o] = at(t, r, i, n, e.version, s), "OUT" === o ? a = !0 : "IN" === o && a && (a = !1)
        }
        "VOD" === e.playlistType && a && t.push("#EXT-X-CUE-IN"), e.prefetchSegments.length > 2 && r("The server must deliver no more than two prefetch segments");
        for (const s of e.prefetchSegments) s.discontinuity && t.push("#EXT-X-PREFETCH-DISCONTINUITY"), t.push(`#EXT-X-PREFETCH:${s.uri}`);
        e.endlist && t.push("#EXT-X-ENDLIST");
        for (const s of e.renditionReports) {
            const e = [];
            e.push(`URI="${s.uri}"`, `LAST-MSN=${s.lastMSN}`), void 0 !== s.lastPart && e.push(`LAST-PART=${s.lastPart}`), t.push(`#EXT-X-RENDITION-REPORT:${e.join(",")}`)
        }
    }(i, t, e), i.join("\n")
}

export {X as getOptions, _ as parse, h as setOptions, ot as stringify, M as types};