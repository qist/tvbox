/*
* @File     : book.js
* @Author   : jade
* @Date     : 2024/1/30 17:01
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
export class BookShort {

    constructor() {
        this.book_id = ""        //id
        this.book_name = ""      //名称
        this.book_pic = ""   //图片
        this.book_remarks = ""  //备注
    }

    to_dict() {
        return JSON.stringify(this);
    }

    load_dic(json_str) {
        let obj = JSON.parse(json_str)
        for (let propName in obj) {
            this[propName] = obj[propName];
        }

    }
}

export class BookDetail extends BookShort {
    /**
     *         let book = {
     *             book_name: $('[property$=book_name]')[0].attribs.content,
     *             book_year: $('[property$=update_time]')[0].attribs.content,
     *             book_director: $('[property$=author]')[0].attribs.content,
     *             book_content: $('[property$=description]')[0].attribs.content,
     *         };
     *         $ = await this.getHtml(this.siteUrl + id + `list.html`);
     *         let urls = [];
     *         const links = $('dl>dd>a[href*="/html/"]');
     *         for (const l of links) {
     *             const name = $(l).text().trim();
     *             const link = l.attribs.href;
     *             urls.push(name + '$' + link);
     *         }
     *         book.volumes = '全卷';
     *         book.urls = urls.join('#');
     *         return book
     * */
    constructor() {
        super();
        this.book_year = ""
        this.book_director = ""
        this.book_content = ""
        this.volumes = ""
        this.urls = ""
    }

    to_short() {
        let bookShort = new BookShort()
        bookShort.load_dic(this.to_dict())
        return bookShort.to_dict()
    }

    load_dic(json_str) {
        let obj = JSON.parse(json_str)
        for (let propName in obj) {
            this[propName] = obj[propName];
            console.log(propName);//打印👉属性名-->name  age  gender  address
        }
    }
}



