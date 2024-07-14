import requests
from bs4 import BeautifulSoup

import time
import random


def ip_proxy_pool():
    def validate_proxy(proxy):
        try:
            # 使用代理发送请求
            response = requests.get("https://www.baidu.com", proxies=proxy, timeout=5)
            # 如果响应状态码为200，则返回True
            if response.status_code == 200:
                return True
        except:
            # 如果请求失败，则返回False
            return False

    proxy_pool = []
    with open("raw_corpus/IP.txt", "r") as file:
        for line in file:
            # 假设每行都是一个代理IP的字典字符串
            proxy = eval(line.strip())
            proxy_pool.append(proxy)

    # proxy_pool = [proxy for proxy in proxy_pool if proxy.get("HTTPS") and validate_proxy(proxy)]
    proxy_pool = [proxy for proxy in proxy_pool if proxy.get("HTTPS")]

    return proxy_pool


def query(content, headers):
    # 请求地址
    url = "https://baike.baidu.com/item/" + requests.utils.quote(content)

    try:
        # 发送请求，获得响应
        response = requests.get(url, headers=headers, timeout=1)
        # 读取响应，获得文本
        text = response.text
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(text, "html.parser")
        # print(soup)
        # 使用css选择器匹配数据，得到匹配字符串列表
        sen_list = soup.select(".lemmaSummary, .J-lemma-content")
        # 过滤数据，去掉空白
        sen_list_after_filter = [item.get_text().strip() for item in sen_list]
        # 将字符串列表连成字符串并返回
        return "".join(sen_list_after_filter), 200
    except:
        return "", -1


if __name__ == "__main__":
    # ['分布式系统', '总线冲突', '汇编指令', '冯诺依曼体系结构', '虚拟存储器', '流水线技术', '总线频率', '总线带宽', '寄存器', '地址寄存器', '输出设备', '存储单元', '内存碎片', '网络系统', '大型计算机', '时钟周期', '易失性存储器', '存储器带宽', '内存泄漏', '存储器管理', '缓存一致性', '内存屏障', '程序计数器', '机器指令', '主存', '异步总线', '内存映射文件', '并行处理', '指令集', '集成电路', '光盘存储', '微型计算机', '系统总线', '总线复用', '数据寄存器', '数据总线', '指令寄存器', '操作系统', '应用软件', '高级语言', '二级缓存', '小型计算机', '解释器', '指令预取', '机器周期', '总线接口', '指令解码', 'CPU', '片内总线', '计算机网络', '局域网', '并行计算', '超线程技术', '辅助存储器', '系统软件', '总线周期', '存储器地址寄存器', '算术逻辑部件', '实时系统', '存储字', '运算器', '控制器', 'PC', 'MAR', '定点数', '浮点数', '逻辑运算', 'CISC', 'RISC', '计算机组成', 'I/O设备', '寻址方式', '只读存储器', '直接映射', '固态硬盘(SSD)', '全相联映射', '磁带', 'MDR', '组相联映射', '动态内存管理', '存储器', '扩展总线', '总线请求', 'SRAM', '总线', '存取周期', '内存交换', '总线带宽', '通用寄存器', '字长', 'RAM', '指令周期', '位宽', 'SDRAM', 'DMA', '总线容量', '非易失性内存', '存储单元', '中断', '超标量技术', '算术逻辑单元', '缓存', '并行传输', '存储器容量', '磁盘', '闪存', 'DRAM', '硬件', '总线仲裁', '微操作', '微指令', '微程序', '硬布线控制器', 'I/O接口', 'IO', '直接映射', 'SSD', '磁带', '组相联映射', '存取周期', '缓存', '总线仲裁', '存储容量', '多核处理器', '指令集架构', ]
    spider_params = []
    empty_params = []
    proxy_pool = ip_proxy_pool()
    retry = 3
    for p in spider_params:
        print(f"正在爬取：{p}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "Cookie": 'BAIDUID=890E51CDBD29BD92E2BE03DD34C8F1A6:FG=1; BAIDUID_BFESS=890E51CDBD29BD92E2BE03DD34C8F1A6:FG=1; BAIDU_WISE_UID=wapp_1714198917765_235; BIDUPSID=890E51CDBD29BD92E2BE03DD34C8F1A6; PSTM=1718885629; BDUSS_BFESS=JrSEFjVmxReWdTNDFmU3V4TDlYbHBITFlFNnkyU3dFY0plblZNZ1BudHdrS2RtRVFBQUFBJCQAAAAAAQAAAAEAAAAGjBlJv93I2da5yrQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHADgGZwA4BmSj; ZFY=9PpGk0TuStG83d4e7y:BE9HAOTXmRcsvl9Ui14rofLvo:C; ariaDefaultTheme=undefined; RT="z=1&dm=baidu.com&si=7eae614a-9252-4e76-a87b-3b35507c12a1&ss=ly8357zr&sl=1&tt=5nr&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=6fz&ul=9jbq&hd=9jc4"; BD_UPN=12314753; B64_BOT=1; ab_sr=1.0.1_NWE3ZDc0MjA1OWYxNzk5MjQyYTE0ZWFjMjI4YTFjNmU5M2Y4OTc2MWZkZWI1M2U4NGM5OWI4ZjE4OTA0MzRjNDAwZDM4OTQyYmJiYjgxMzBlMWYwNGE4M2ZiNzJlMmE2ZDc1MjUxMDhiNjhiZjBjZDRmZTE3NTkwNjNkNGI4ZDNhYTdhMDYzMGY2N2E0M2Y1ZDAwZmE1NjFjODRmOWJmODQ4NDAyM2NiMjVjM2IxMmQ0YWUwMjk4YzQ5MDgyNjE3; H_PS_PSSID=60363_60359_60379_60444; BA_HECTOR=ag8hal8l2hak050h2h050ha40tvf2d1j8hd7j1u; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; BD_CK_SAM=1; PSINO=2; H_PS_645EC=809bghXjfdD10mdm4Dt2O%2BNppgvOQ8UCbTV6j4qShkM2F0LUXbPgMq5c2MysJjw10OwL; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSVRTM=591; channel=bing; baikeVisitId=f41f9855-b359-44cd-935a-5ddad8ff563b',
            "https": random.choice(proxy_pool)["HTTPS"]
        }
        result, status = query(p, headers)
        if status != 200:
            while retry == 0 and status != 200:
                headers["https"] =  random.choice(proxy_pool)["HTTPS"]
                result, status = query(p, headers)
        time.sleep(random.randint(1, 2))
        if not result:
            print(f"{p}的爬取结果为空")
            empty_params.append(p)
            continue
        else:
            with open("raw_corpus/spider_raw_data.txt", "a") as f:
                f.write(f"{p}：\n")
                f.write(result)
                f.write("\n\n")
    print("爬取完成")
    print("以下是爬取失败的参数：")
    print(empty_params)
