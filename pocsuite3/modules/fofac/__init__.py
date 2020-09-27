import pychrome
import urllib
import random
from base64 import b64encode
from configparser import ConfigParser
from pocsuite3.lib.core.data import logger
from pocsuite3.lib.core.data import paths


class Fofac():
    def __init__(self, conf_path=paths.POCSUITE_RC_PATH, cookie=None):
        self.cookie = cookie
        self.conf_path = conf_path

        if self.conf_path:
            self.parser = ConfigParser()
            # print(self.conf_path)
            self.parser.read(self.conf_path)
            try:
                self.cookie = self.parser.get("Fofa", 'cookie')
            except Exception:
                pass

        if cookie:
            self.cookie = cookie
        self.check_cookie()

    def cookie_is_available(self):
        if self.cookie:
            try:
                browser = pychrome.Browser(url="http://127.0.0.1:9222")
                # create a tab
                tab = browser.new_tab()
                # start the tab
                tab.start()
                tab.Page.enable()
                # call method
                tab.Network.enable()
                tab.Runtime.enable()
                tab.Network.clearBrowserCookies()
                url = "https://fofa.so/"
                tab.Network.setExtraHTTPHeaders(headers={
                                                "Connection": "keep-alive", "Cookie": "_fofapro_ars_session={c}".format(c=self.cookie)})
                tab.Network.setUserAgentOverride(
                    userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
                tab.Network.setCookie(
                    name="_fofapro_ars_session", value=self.cookie, url="https://fofa.so/")
                # call method with timeout
                tab.Page.navigate(url=url, _timeout=5)
                tab.wait(2)
                test = 'document.getElementsByClassName("user-avatar").length'
                tmp = tab.Runtime.evaluate(expression=test)
                # print(tmp['result']['value'])
                if tmp['result']['value'] != 0:
                    return True
            except Exception as ex:
                logger.error(str(ex))
        return False

    def check_cookie(self):
        if self.cookie_is_available():
            return True
        else:
            cookie = input("Fofac cookie:")
            self.user = cookie
            if self.cookie_is_available():
                self.write_conf()
                return True
            else:
                logger.error("The Fofa cookie is incorrect. "
                             "Please enter the correct cookie.")
                self.check_cookie()

    def write_conf(self):
        if not self.parser.has_section("Fofa"):
            self.parser.add_section("Fofa")
        try:
            self.parser.set("Fofa", "Cookie", self.cookie)
            self.parser.write(open(self.conf_path, "w"))
        except Exception as ex:
            logger.error(str(ex))

    def search(self, dork, pages=100):
        search_result = set()
        # create a browser instance
        browser = pychrome.Browser(url="http://127.0.0.1:9222")
        # create a tab
        tab = browser.new_tab()
        # start the tab
        tab.start()
        tab.Page.enable()
        # call method
        tab.Network.enable()
        tab.Runtime.enable()
        tab.Network.clearBrowserCookies()
        url = "https://fofa.so/result?full=true&qbase64={dork}".format(
            dork=b64encode(dork.encode()).decode())
        tab.Network.setExtraHTTPHeaders(headers={
                                        "Connection": "keep-alive", "Cookie": "_fofapro_ars_session={c}".format(c=self.cookie)})
        tab.Network.setUserAgentOverride(
            userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")
        tab.Network.setCookie(name="_fofapro_ars_session",
                              value=self.cookie, url="https://fofa.so/result")
        # call method with timeout
        tab.Page.navigate(url=url, _timeout=5)
        tab.wait(2)

        exp = 'document.querySelector("#rs > span:nth-child(1)").innerText'
        length = tab.Runtime.evaluate(expression=exp)
        # 判断当前搜索结果有多少数据，来确定可以爬取数据的页数
        # print("length:", length['result']['value'])
        logger.info("Total: "+str(length['result']['value']))
        logger.info("The current set of max crawler pages is {}.".format(pages))
        if pages > 1000:
            pages = 1000
        if int(length['result']['value'].replace(",", ""))/10 <= pages:
            endPageNum = int(length['result']['value'].replace(",", ""))/10+1
        else:
            # endPageNum=1000
            # 限制了一下能力，一般也只爬取20页也就是200条数据
            endPageNum = pages
        # print(endPageNum)
        try:
            # 从每一页上抓取url
            for step in range(1, endPageNum+1):
                # 通过前端模拟点击跳转页面
                nextPage = 'document.querySelector("#will_page > a.next_page").click()'
                # test='document.querySelector("#result > div.g-header.box-sizing.clearfix.common.new-header > div.clearfix > div.fr > a.marLef40.login-btn").innerText'
                tab.Runtime.evaluate(expression=nextPage)
                tab.wait(random.randint(2, 4))

                # test='document.querySelector("#result > div.g-header.box-sizing.clearfix.common.new-header > div.clearfix > div.fr > a.marLef40.nav-user > span").innerText'
                # # test='document.querySelector("#result > div.g-header.box-sizing.clearfix.common.new-header > div.clearfix > div.fr > a.marLef40.login-btn").innerText'
                # tmp=tab.Runtime.evaluate(expression=test)
                # print tmp['result']

                exp1 = 'document.getElementsByClassName("re-domain").length'
                endNum = tab.Runtime.evaluate(expression=exp1)
                endNum = int(endNum['result']['value'])
                # print(endNum)

                if endNum == 0:
                    # 通过网络发包来跳转页面
                    url = "https://fofa.so/result?full=true&qbase64={dork}".format(
                        dork=b64encode(dork.encode()).decode())
                    url = url+"&page={}".format(step)
                    # tab.Network.setExtraHTTPHeaders(headers={"Connection":"keep-alive"})
                    tab.Network.setExtraHTTPHeaders(headers={
                                                    "Connection": "keep-alive", "Cookie": "_fofapro_ars_session={c}".format(c=self.cookie)})
                    tab.Network.setCookie(
                        name="_fofapro_ars_session", value=self.cookie, url="https://fofa.so/result")
                    tab.Page.navigate(url=url, _timeout=5)
                    exp1 = 'document.getElementsByClassName("re-domain").length'
                    endNum = tab.Runtime.evaluate(expression=exp1)
                    endNum = int(endNum['result']['value'])
                    # print(endNum)
                    # debug info
                    # test = 'document.body'
                    # tmp = tab.Runtime.evaluate(expression=test)
                    # print(tmp['result'])

                for l in range(0, endNum):
                    exp2 = 'document.getElementsByClassName("re-domain")[{}].innerText'.format(
                        l)
                    res2 = tab.Runtime.evaluate(expression=exp2)
                    result_value = res2['result']['value'].replace(" ", "")
                    if not result_value.startswith("https://") and not result_value.startswith("http://"):
                        result_value = "http://" + result_value
                    else:
                        result_value = result_value
                    logger.info(result_value)
                    search_result.add(result_value)
            tab.stop()
            browser.close_tab(tab)
        except Exception as ex:
            logger.error(str(ex))
        return search_result


if __name__ == "__main__":
    fa = Fofac(cookie='e9b6337117b4e513a9ec4bb8b348ed9d')
    z = fa.search('body="thinkphp"')
    print(z)
