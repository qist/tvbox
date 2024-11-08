// drT.js
// 2022/09/30 write by hjdhnx
// Licensed under the MIT license.

(function () {
    "use strict";

    var drT = {
        name: "drT",
        version: "1.0.0",
        templateSettings: {
            evaluate:    /\{\{([\s\S]+?(\}?)+)\}\}/g,
            interpolate: /\{\{([\s\S]+?)\}\}/g, // 变量渲染
            encode:      /\{\{@([\s\S]+?)\}\}/g, // 变量自动url编码
            use:         /\{\{#([\s\S]+?)\}\}/g,
            useParams:   /(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})/g,
            define:      /\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}/g,
            defineParams:/^\s*([\w$]+):([\s\S]+)/,
            conditional: /\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}/g, // ? if ?? else if ?? else
            iterate:     /\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})/g,
            varname:	"fl",
            strip:		true,
            append:		true,
            selfcontained: false,
            doNotSkipEncoded: false
        },
        template: undefined, //fn, compile template
        compile:  undefined, //fn, for express
        log: true
    }, _globals;

    drT.encodeHTMLSource = function(doNotSkipEncoded) {
        var encodeHTMLRules = { "&": "&#38;", "<": "&#60;", ">": "&#62;", '"': "&#34;", "'": "&#39;", "/": "&#47;" },
            matchHTML = doNotSkipEncoded ? /[&<>"'\/]/g : /&(?!#?\w+;)|<|>|"|'|\//g;
        return function(code) {
            return code ? code.toString().replace(matchHTML, function(m) {return encodeHTMLRules[m] || m;}) : "";
        };
    };

    _globals = (function(){ return this || (0,eval)("this"); }());

    /* istanbul ignore else */
    if (typeof module !== "undefined" && module.exports) {
        module.exports = drT;
    } else if (typeof define === "function" && define.amd) {
        define(function(){return drT;});
    } else {
        _globals.drT = drT;
    }

    var startend = {
        append: { start: "'+(",      end: ")+'",      startencode: "'+encodeHTML(" },
        split:  { start: "';out+=(", end: ");out+='", startencode: "';out+=encodeHTML(" }
    }, skip = /$^/;

    function resolveDefs(c, block, def) {
        return ((typeof block === "string") ? block : block.toString())
            .replace(c.define || skip, function(m, code, assign, value) {
                if (code.indexOf("def.") === 0) {
                    code = code.substring(4);
                }
                if (!(code in def)) {
                    if (assign === ":") {
                        if (c.defineParams) value.replace(c.defineParams, function(m, param, v) {
                            def[code] = {arg: param, text: v};
                        });
                        if (!(code in def)) def[code]= value;
                    } else {
                        new Function("def", "def['"+code+"']=" + value)(def);
                    }
                }
                return "";
            })
            .replace(c.use || skip, function(m, code) {
                if (c.useParams) code = code.replace(c.useParams, function(m, s, d, param) {
                    if (def[d] && def[d].arg && param) {
                        var rw = (d+":"+param).replace(/'|\\/g, "_");
                        def.__exp = def.__exp || {};
                        def.__exp[rw] = def[d].text.replace(new RegExp("(^|[^\\w$])" + def[d].arg + "([^\\w$])", "g"), "$1" + param + "$2");
                        return s + "def.__exp['"+rw+"']";
                    }
                });
                var v = new Function("def", "return " + code)(def);
                return v ? resolveDefs(c, v, def) : v;
            });
    }

    function unescape(code) {
        return code.replace(/\\('|\\)/g, "$1").replace(/[\r\t\n]/g, " ");
    }

    drT.template = function(tmpl, c, def) {
        c = c || drT.templateSettings;
        var cse = c.append ? startend.append : startend.split, needhtmlencode, sid = 0, indv,
            str  = (c.use || c.define) ? resolveDefs(c, tmpl, def || {}) : tmpl;

        // console.log(str);
        let beforeCode = '';
        if(str.match(c.interpolate || skip)){
            let inter_codes = str.match(c.interpolate || skip);
            let inter_dict = {};
            inter_codes.forEach(item=>{
                item.replace(c.interpolate || skip,function (m,code) {
                    let varname = code.split('.')[0];
                    if(!inter_dict.hasOwnProperty(varname)){
                        let beginCode = `if(typeof(${varname})==='undefined'){${varname}={}}`;
                        inter_dict[varname] = beginCode;
                    }if(!inter_dict.hasOwnProperty(code)){
                        let beginCode = `if(typeof(${code})==='undefined'){${code}=''};`;
                        inter_dict[code] = beginCode;
                    }
                });
            });
            let beginCode = Object.values(inter_dict).join('\n');
            // console.log(beginCode);
            beforeCode += beginCode;
        }
        str = beforeCode+("var out='" + (c.strip ? str.replace(/(^|\r|\n)\t* +| +\t*(\r|\n|$)/g," ")
                .replace(/\r|\n|\t|\/\*[\s\S]*?\*\//g,""): str)
                .replace(/'|\\/g, "\\$&")
                .replace(c.encode || skip, function(m, code) {
                    needhtmlencode = true;
                    return cse.startencode + unescape(code) + cse.end;
                })
                .replace(c.interpolate || skip, function(m, code) {
                    let varname = code.split('.')[0];
                    // console.log(varname === code);
                    // console.log(`varname:${varname},code:${code}`);
                    if(varname === code){
                        let res = cse.start + `JSON.stringify(${unescape(code)})` + cse.end;
                        // console.log(res);
                        return res
                    }
                    return cse.start + unescape(code) + cse.end;
                })
                .replace(c.conditional || skip, function(m, elsecase, code) {
                    return elsecase ?
                        (code ? "';}else if(" + unescape(code) + "){out+='" : "';}else{out+='") :
                        (code ? "';if(" + unescape(code) + "){out+='" : "';}out+='");
                })
                .replace(c.iterate || skip, function(m, iterate, vname, iname) {
                    if (!iterate) return "';} } out+='";
                    sid+=1; indv=iname || "i"+sid; iterate=unescape(iterate);
                    return "';var arr"+sid+"="+iterate+";if(arr"+sid+"){var "+vname+","+indv+"=-1,l"+sid+"=arr"+sid+".length-1;while("+indv+"<l"+sid+"){"
                        +vname+"=arr"+sid+"["+indv+"+=1];out+='";
                })
                .replace(c.evaluate || skip, function(m, code) {
                    return "';" + unescape(code) + "out+='";
                })
            + "';return out;")
            .replace(/\n/g, "\\n").replace(/\t/g, '\\t').replace(/\r/g, "\\r")
            .replace(/(\s|;|\}|^|\{)out\+='';/g, '$1').replace(/\+''/g, "");
        //.replace(/(\s|;|\}|^|\{)out\+=''\+/g,'$1out+=');

        if (needhtmlencode) {
            // console.log('需要编码');
            // console.log(c.doNotSkipEncoded);
            if (!c.selfcontained && _globals && !_globals._encodeHTML) _globals._encodeHTML = drT.encodeHTMLSource(c.doNotSkipEncoded);
            str = "var encodeHTML = typeof _encodeHTML !== 'undefined' ? _encodeHTML : ("
                + drT.encodeHTMLSource.toString() + "(" + (c.doNotSkipEncoded || '') + "));"
                + str;
            // console.log(str);
        }else{
            // console.log('不需要编码');
        }
        // console.log(c.varname);
        // console.log(str);
        try {
            return new Function(c.varname, str);
        } catch (e) {
            /* istanbul ignore else */
            // console.log(e.message);
            if (typeof console !== "undefined") console.log("Could not create a template function: " + str);
            throw e;
        }
    };

    drT.compile = function(tmpl, def) {
        return drT.template(tmpl, null, def);
    };
    drT.renderText = function (tmpl,dict,varname){
        varname = varname||'';
        if(varname){
            drT.templateSettings.varname = varname;
        }
        dict = dict||{};
        return drT.compile(tmpl)(dict);
    };
}());