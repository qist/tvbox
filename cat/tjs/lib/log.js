const level_list = ["DEBUG", "INFO", "WARNING", "ERROR"];
const file_path = "log"

class JadeLogging {

    constructor(app_name, level = "DEBUG") {
        this.app_name = app_name
        this.level = level
        this.level_index = level_list.indexOf(level)
    }


    format(level, message) {
        let max_format = 80
        switch (level) {
            case "INFO":
                max_format = max_format + 1
                break
            case "WARNING":
                max_format = max_format - 2
                break
            default :
                break
        }
        if (message.length < max_format) {
            if ((max_format - message.length) % 2 === 0) {
                message = "#".repeat(Math.floor((max_format - message.length) / 2)) + message + "#".repeat(Math.floor((max_format - message.length) / 2))
            } else {
                message = "#".repeat(Math.floor((max_format - message.length) / 2)) + message + "#".repeat(Math.floor((max_format - message.length) / 2) + 1)
            }
        }
        return message
    }

    getTime() {
        const timestamp = new Date();
        // 获取当前时间戳
        return timestamp.toLocaleDateString().replace(/\//g, "-") + " " + timestamp.toTimeString().substr(0, 8) + "," + timestamp.getMilliseconds().toString()
    }

    formatMessage(log_level, message, is_format) {
        // 获取北京时间
        // 格式化消息
        //2023-12-13 15:15:21,409 - 阿里玩偶 -
        //2023-12-14T01:43:31.278Z
        //2023-12-13 15:15:21,409 - 阿里玩偶 - INFO:
        //2023-12-13 15:15:21,409 - 阿里玩偶 - ERROR:
        if (is_format) {
            message = this.format(log_level, message)
        }
        return `${this.getTime()} - ${this.app_name} - ${log_level}: ${message}`

    }

    async log(message) {
        console.debug(message)
        await local.set(file_path,this.getTime(), message);
    }

    async info(message, is_format=false) {
        if (this.level_index <= 1) {
            await this.log(this.formatMessage("INFO", message, is_format))
        }
    }

    async warning(message, is_format=false) {
        if (this.level_index <= 2) {
            await this.log(this.formatMessage("WARNING", message, is_format))
        }
    }

    async error(message, is_format=false) {
        if (this.level_index <= 3) {
            await this.log(this.formatMessage("ERROR", message, is_format))
        }
    }

    async debug(message, is_format=false) {
        if (this.level_index <= 0) {
            await this.log(this.formatMessage("DEBUG", message, is_format))
        }
    }
}

// 测试日志记录函数
export {JadeLogging}