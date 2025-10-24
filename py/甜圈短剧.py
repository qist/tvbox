# -*- coding: utf-8 -*-
# by @嗷呜
import sys
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    ahost='https://api.cenguigui.cn'

    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
            'DNT': '1',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Storage-Access': 'active',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def homeContent(self, filter):
        result = {'class': [{'type_id': '推荐榜', 'type_name': '🔥 推荐榜'},
                            {'type_id': '新剧', 'type_name': '🎬 新剧'},
                            {'type_id': '逆袭', 'type_name': '🎬 逆袭'},
                            {'type_id': '霸总', 'type_name': '🎬 霸总'},
                            {'type_id': '现代言情', 'type_name': '🎬 现代言情'},
                            {'type_id': '打脸虐渣', 'type_name': '🎬 打脸虐渣'},
                            {'type_id': '豪门恩怨', 'type_name': '🎬 豪门恩怨'},
                            {'type_id': '神豪', 'type_name': '🎬 神豪'},
                            {'type_id': '马甲', 'type_name': '🎬 马甲'},
                            {'type_id': '都市日常', 'type_name': '🎬 都市日常'},
                            {'type_id': '战神归来', 'type_name': '🎬 战神归来'},
                            {'type_id': '小人物', 'type_name': '🎬 小人物'},
                            {'type_id': '女性成长', 'type_name': '🎬 女性成长'},
                            {'type_id': '大女主', 'type_name': '🎬 大女主'},
                            {'type_id': '穿越', 'type_name': '🎬 穿越'},
                            {'type_id': '都市修仙', 'type_name': '🎬 都市修仙'},
                            {'type_id': '强者回归', 'type_name': '🎬 强者回归'},
                            {'type_id': '亲情', 'type_name': '🎬 亲情'},
                            {'type_id': '古装', 'type_name': '🎬 古装'},
                            {'type_id': '重生', 'type_name': '🎬 重生'},
                            {'type_id': '闪婚', 'type_name': '🎬 闪婚'},
                            {'type_id': '赘婿逆袭', 'type_name': '🎬 赘婿逆袭'},
                            {'type_id': '虐恋', 'type_name': '🎬 虐恋'},
                            {'type_id': '追妻', 'type_name': '🎬 追妻'},
                            {'type_id': '天下无敌', 'type_name': '🎬 天下无敌'},
                            {'type_id': '家庭伦理', 'type_name': '🎬 家庭伦理'},
                            {'type_id': '萌宝', 'type_name': '🎬 萌宝'},
                            {'type_id': '古风权谋', 'type_name': '🎬 古风权谋'},
                            {'type_id': '职场', 'type_name': '🎬 职场'},
                            {'type_id': '奇幻脑洞', 'type_name': '🎬 奇幻脑洞'},
                            {'type_id': '异能', 'type_name': '🎬 异能'},
                            {'type_id': '无敌神医', 'type_name': '🎬 无敌神医'},
                            {'type_id': '古风言情', 'type_name': '🎬 古风言情'},
                            {'type_id': '传承觉醒', 'type_name': '🎬 传承觉醒'},
                            {'type_id': '现言甜宠', 'type_name': '🎬 现言甜宠'},
                            {'type_id': '奇幻爱情', 'type_name': '🎬 奇幻爱情'},
                            {'type_id': '乡村', 'type_name': '🎬 乡村'},
                            {'type_id': '历史古代', 'type_name': '🎬 历史古代'},
                            {'type_id': '王妃', 'type_name': '🎬 王妃'},
                            {'type_id': '高手下山', 'type_name': '🎬 高手下山'},
                            {'type_id': '娱乐圈', 'type_name': '🎬 娱乐圈'},
                            {'type_id': '强强联合', 'type_name': '🎬 强强联合'},
                            {'type_id': '破镜重圆', 'type_name': '🎬 破镜重圆'},
                            {'type_id': '暗恋成真', 'type_name': '🎬 暗恋成真'},
                            {'type_id': '民国', 'type_name': '🎬 民国'},
                            {'type_id': '欢喜冤家', 'type_name': '🎬 欢喜冤家'},
                            {'type_id': '系统', 'type_name': '🎬 系统'},
                            {'type_id': '真假千金', 'type_name': '🎬 真假千金'},
                            {'type_id': '龙王', 'type_name': '🎬 龙王'},
                            {'type_id': '校园', 'type_name': '🎬 校园'},
                            {'type_id': '穿书', 'type_name': '🎬 穿书'},
                            {'type_id': '女帝', 'type_name': '🎬 女帝'},
                            {'type_id': '团宠', 'type_name': '🎬 团宠'},
                            {'type_id': '年代爱情', 'type_name': '🎬 年代爱情'},
                            {'type_id': '玄幻仙侠', 'type_name': '🎬 玄幻仙侠'},
                            {'type_id': '青梅竹马', 'type_name': '🎬 青梅竹马'},
                            {'type_id': '悬疑推理', 'type_name': '🎬 悬疑推理'},
                            {'type_id': '皇后', 'type_name': '🎬 皇后'},
                            {'type_id': '替身', 'type_name': '🎬 替身'},
                            {'type_id': '大叔', 'type_name': '🎬 大叔'},
                            {'type_id': '喜剧', 'type_name': '🎬 喜剧'},
                            {'type_id': '剧情', 'type_name': '🎬 剧情'}]}
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        params = {
            'classname': tid,
            'offset': str((int(pg) - 1)),
        }
        data = self.fetch(f'{self.ahost}/api/duanju/api.php', params=params, headers=self.headers).json()
        videos = []
        for k in data['data']:
            videos.append({
                'vod_id': k.get('book_id'),
                'vod_name': k.get('title'),
                'vod_pic': k.get('cover'),
                'vod_year': k.get('score'),
                'vod_remarks': f"{k.get('sub_title')}|{k.get('episode_cnt')}"
            })
        result = {}
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        v=self.fetch(f'{self.ahost}/api/duanju/api.php', params={'book_id': ids[0]}, headers=self.headers).json()
        vod = {
            'type_name': v.get('category'),
            'vod_year': v.get('time'),
            'vod_remarks': v.get('duration'),
            'vod_content': v.get('desc'),
            'vod_play_from': '嗷呜爱看短剧',
            'vod_play_url': '#'.join([f"{i['title']}${i['video_id']}" for i in v['data']])
        }
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        return self.categoryContent(key, pg, True, {})

    def playerContent(self, flag, id, vipFlags):
        data=self.fetch(f'{self.ahost}/api/duanju/api.php', params={'video_id': id}, headers=self.headers).json()
        return  {'parse': 0, 'url': data['data']['url'], 'header': self.headers}

    def localProxy(self, param):
        pass
