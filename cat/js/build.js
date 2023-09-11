import fs from 'node:fs';
import path from 'path';
import uglifyjs from 'uglify-js';

const copySpider = ['app', 'kunyu77_open', 'alist_open'];

const root = process.cwd();

const src = path.join(root);
const out = path.join(root, 'dist');

function minify(s, d) {
    var jsContent = fs.readFileSync(s).toString();
    jsContent = jsContent.replace('./lib/cat.js', 'assets://js/lib/cat.js');
    jsContent = jsContent.replace('./cat.js', 'assets://js/lib/cat.js');
    jsContent = uglifyjs.minify(jsContent, {
        mangle: false,
    });
    fs.writeFileSync(d, jsContent.code);
}

function listAllFiles(dirPath, arrayOfFiles) {
    var files = fs.readdirSync(dirPath);

    arrayOfFiles = arrayOfFiles || [];

    files.forEach(function (file) {
        if (fs.statSync(dirPath + '/' + file).isDirectory()) {
            arrayOfFiles = listAllFiles(dirPath + '/' + file, arrayOfFiles);
        } else {
            arrayOfFiles.push(path.join(dirPath, '/', file));
        }
    });

    return arrayOfFiles;
}

function src2Out() {
    if (fs.existsSync(out)) fs.rmSync(out, { recursive: true, force: true });

    fs.mkdirSync(out, { recursive: true });
    const libSrc = path.join(src, 'lib');
    const libOut = path.join(out, 'lib');
    fs.mkdirSync(libOut, { recursive: true });
    const libs = listAllFiles(libSrc);
    for (let index = 0; index < libs.length; index++) {
        const element = libs[index];
        const relative = path.relative(libSrc, element);
        minify(element, path.join(libOut, relative));
    }

    for (const sp of copySpider) {
        minify(path.join(src, sp + '.js'), path.join(out, sp + '.js'));
    }
}

src2Out();

fs.copyFileSync(path.join(src, 'config_open.json'), path.join(out, 'config_open.json'));

console.log('done');
