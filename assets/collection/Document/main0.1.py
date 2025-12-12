import urllib.request
from urllib.parse import urlparse
import re
import os
from datetime import datetime, timedelta, timezone
import random
import opencc
import socket
import time

def traditional_to_simplified(text: str) -> str:
    converter = opencc.OpenCC('t2s')
    simplified_text = converter.convert(text)
    return simplified_text

timestart = datetime.now()

def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            return lines
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def read_blacklist_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    BlackList = [line.split(',')[1].strip() for line in lines if ',' in line]
    return BlackList

blacklist_auto = read_blacklist_from_txt('assets/blacklist1/blacklist_auto.txt')
blacklist_manual = read_blacklist_from_txt('assets/blacklist1/blacklist_manual.txt')
combined_blacklist = set(blacklist_auto + blacklist_manual)

sh_lines = []
ys_lines = []
ws_lines = []
ty_lines = []
tyss_lines = []
mgss_lines = []
dy_lines = []
dsj_lines = []
gat_lines = []
gj_lines = []
jlp_lines = []
dhp_lines = []
xq_lines = []
js_lines = []
cw_lines = []
mx_lines = []
ztp_lines = []
zy_lines = []
yy_lines = []
game_lines = []
radio_lines = []
zj_lines = []
jsu_lines = []
gd_lines = []
hn_lines = []
ah_lines = []
hain_lines = []
nm_lines = []
hb_lines = []
ln_lines = []
sx_lines = []
shanxi_lines = []
shandong_lines = []
yunnan_lines = []
bj_lines = []
cq_lines = []
fj_lines = []
gs_lines = []
gx_lines = []
gz_lines = []
heb_lines = []
hen_lines = []
hlj_lines = []
jl_lines = []
jx_lines = []
nx_lines = []
qh_lines = []
sc_lines = []
tj_lines = []
xj_lines = []
auto_4k_lines = []
zb_lines = []
mtv_lines = []
Olympics_2024_Paris_lines = []
other_lines = []
other_lines_url = []

def process_name_string(input_str):
    parts = input_str.split(',')
    processed_parts = []
    for part in parts:
        processed_part = process_part(part)
        processed_parts.append(processed_part)
    result_str = ','.join(processed_parts)
    return result_str

def process_part(part_str):
    if "CCTV" in part_str and "://" not in part_str:
        part_str = part_str.replace("IPV6", "")
        part_str = part_str.replace("PLUS", "+")
        part_str = part_str.replace("1080", "")
        filtered_str = ''.join(char for char in part_str if char.isdigit() or char == 'K' or char == '+')
        if not filtered_str.strip():
            filtered_str = part_str.replace("CCTV", "")
        if len(filtered_str) > 2 and re.search(r'4K|8K', filtered_str):
            filtered_str = re.sub(r'(4K|8K).*', r'\1', filtered_str)
            if len(filtered_str) > 2:
                filtered_str = re.sub(r'(4K|8K)', r'(\1)', filtered_str)
        return "CCTV" + filtered_str
    elif "卫视" in part_str:
        pattern = r'卫视「.*」'
        result_str = re.sub(pattern, '卫视', part_str)
        return result_str
    return part_str

def get_url_file_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1]
    return extension

def convert_m3u_to_txt(m3u_content):
    lines = m3u_content.split('\n')
    txt_lines = []
    channel_name = ""
    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            channel_name = line.split(',')[-1].strip()
        elif line.startswith("http") or line.startswith("rtmp") or line.startswith("p3p"):
            txt_lines.append(f"{channel_name},{line.strip()}")
        if "#genre#" not in line and "," in line and "://" in line:
            pattern = r'^[^,]+,[^\s]+://[^\s]+$'
            if bool(re.match(pattern, line)):
                txt_lines.append(line)
    return '\n'.join(txt_lines)

def check_url_existence(data_list, url):
    urls = [item.split(',')[1] for item in data_list]
    return url not in urls

def clean_url(url):
    last_dollar_index = url.rfind('$')
    if last_dollar_index != -1:
        return url[:last_dollar_index]
    return url

removal_list = ["_电信", "电信", "高清", "频道", "（HD）", "-HD", "英陆", "_ITV", "(北美)", "(HK)", "AKtv", "「IPV4」", "「IPV6」", "频陆", "备陆", "壹陆", "贰陆", "叁陆", "肆陆", "伍陆", "陆陆", "柒陆", "频晴", "频粤", "[超清]", "高清", "超清", "标清", "斯特", "粤陆", "国陆", "肆柒", "频英", "频特", "频国", "频壹", "频贰", "肆贰", "频测", "咪咕", "闽特", "高特", "频高", "频标", "汝阳", "4Gtv", "频效", "国标", "粤标", "频推", "频流", "粤高", "频限", "实时", "美推", "频美"]

def clean_channel_name(channel_name, removal_list):
    for item in removal_list:
        channel_name = channel_name.replace(item, "")
    if channel_name.endswith("HD"):
        channel_name = channel_name[:-2]
    if channel_name.endswith("台") and len(channel_name) > 3:
        channel_name = channel_name[:-1]
    return channel_name

def process_channel_line(line):
    if "#genre#" not in line and "#EXTINF:" not in line and "," in line and "://" in line:
        channel_name = line.split(',')[0].strip()
        channel_name = clean_channel_name(channel_name, removal_list)
        channel_name = traditional_to_simplified(channel_name)
        channel_address = clean_url(line.split(',')[1].strip())
        line = channel_name + "," + channel_address
        if channel_address not in combined_blacklist:
            if "CCTV" in channel_name and check_url_existence(ys_lines, channel_address):
                ys_lines.append(process_name_string(line.strip()))
            elif channel_name in ws_dictionary and check_url_existence(ws_lines, channel_address):
                ws_lines.append(process_name_string(line.strip()))
            elif channel_name in ty_dictionary and check_url_existence(ty_lines, channel_address):
                ty_lines.append(process_name_string(line.strip()))
            elif any(tyss_dictionary in channel_name for tyss_dictionary in tyss_dictionary) and check_url_existence(tyss_lines, channel_address):
                tyss_lines.append(process_name_string(line.strip()))
            elif any(mgss_dictionary in channel_name for mgss_dictionary in mgss_dictionary) and check_url_existence(mgss_lines, channel_address):
                mgss_lines.append(process_name_string(line.strip()))
            elif channel_name in dy_dictionary and check_url_existence(dy_lines, channel_address):
                dy_lines.append(process_name_string(line.strip()))
            elif channel_name in dsj_dictionary and check_url_existence(dsj_lines, channel_address):
                dsj_lines.append(process_name_string(line.strip()))
            elif channel_name in sh_dictionary and check_url_existence(sh_lines, channel_address):
                sh_lines.append(process_name_string(line.strip()))
            elif channel_name in gat_dictionary and check_url_existence(gat_lines, channel_address):
                gat_lines.append(process_name_string(line.strip()))
            elif channel_name in gj_dictionary and check_url_existence(gj_lines, channel_address):
                gj_lines.append(process_name_string(line.strip()))
            elif channel_name in jlp_dictionary and check_url_existence(jlp_lines, channel_address):
                jlp_lines.append(process_name_string(line.strip()))
            elif channel_name in dhp_dictionary and check_url_existence(dhp_lines, channel_address):
                dhp_lines.append(process_name_string(line.strip()))
            elif channel_name in xq_dictionary and check_url_existence(xq_lines, channel_address):
                xq_lines.append(process_name_string(line.strip()))
            elif channel_name in js_dictionary and check_url_existence(js_lines, channel_address):
                js_lines.append(process_name_string(line.strip()))
            elif channel_name in cw_dictionary and check_url_existence(cw_lines, channel_address):
                cw_lines.append(process_name_string(line.strip()))
            elif channel_name in mx_dictionary and check_url_existence(mx_lines, channel_address):
                mx_lines.append(process_name_string(line.strip()))
            elif channel_name in ztp_dictionary and check_url_existence(ztp_lines, channel_address):
                ztp_lines.append(process_name_string(line.strip()))
            elif channel_name in zy_dictionary and check_url_existence(zy_lines, channel_address):
                zy_lines.append(process_name_string(line.strip()))
            elif channel_name in yy_dictionary and check_url_existence(yy_lines, channel_address):
                yy_lines.append(process_name_string(line.strip()))
            elif channel_name in game_dictionary and check_url_existence(game_lines, channel_address):
                game_lines.append(process_name_string(line.strip()))
            elif channel_name in radio_dictionary and check_url_existence(radio_lines, channel_address):
                radio_lines.append(process_name_string(line.strip()))
            elif channel_name in zj_dictionary and check_url_existence(zj_lines, channel_address):
                zj_lines.append(process_name_string(line.strip()))
            elif channel_name in jsu_dictionary and check_url_existence(jsu_lines, channel_address):
                jsu_lines.append(process_name_string(line.strip()))
            elif channel_name in gd_dictionary and check_url_existence(gd_lines, channel_address):
                gd_lines.append(process_name_string(line.strip()))
            elif channel_name in hn_dictionary and check_url_existence(hn_lines, channel_address):
                hn_lines.append(process_name_string(line.strip()))
            elif channel_name in hb_dictionary and check_url_existence(hb_lines, channel_address):
                hb_lines.append(process_name_string(line.strip()))
            elif channel_name in ah_dictionary and check_url_existence(ah_lines, channel_address):
                ah_lines.append(process_name_string(line.strip()))
            elif channel_name in hain_dictionary and check_url_existence(hain_lines, channel_address):
                hain_lines.append(process_name_string(line.strip()))
            elif channel_name in nm_dictionary and check_url_existence(nm_lines, channel_address):
                nm_lines.append(process_name_string(line.strip()))
            elif channel_name in ln_dictionary and check_url_existence(ln_lines, channel_address):
                ln_lines.append(process_name_string(line.strip()))
            elif channel_name in sx_dictionary and check_url_existence(sx_lines, channel_address):
                sx_lines.append(process_name_string(line.strip()))
            elif channel_name in shanxi_dictionary and check_url_existence(shanxi_lines, channel_address):
                shanxi_lines.append(process_name_string(line.strip()))
            elif channel_name in shandong_dictionary and check_url_existence(shandong_lines, channel_address):
                shandong_lines.append(process_name_string(line.strip()))
            elif channel_name in yunnan_dictionary and check_url_existence(yunnan_lines, channel_address):
                yunnan_lines.append(process_name_string(line.strip()))
            elif channel_name in bj_dictionary and check_url_existence(bj_lines, channel_address):
                bj_lines.append(process_name_string(line.strip()))
            elif channel_name in cq_dictionary and check_url_existence(cq_lines, channel_address):
                cq_lines.append(process_name_string(line.strip()))
            elif channel_name in fj_dictionary and check_url_existence(fj_lines, channel_address):
                fj_lines.append(process_name_string(line.strip()))
            elif channel_name in gs_dictionary and check_url_existence(gs_lines, channel_address):
                gs_lines.append(process_name_string(line.strip()))
            elif channel_name in gx_dictionary and check_url_existence(gx_lines, channel_address):
                gx_lines.append(process_name_string(line.strip()))
            elif channel_name in gz_dictionary and check_url_existence(gz_lines, channel_address):
                gz_lines.append(process_name_string(line.strip()))
            elif channel_name in heb_dictionary and check_url_existence(heb_lines, channel_address):
                heb_lines.append(process_name_string(line.strip()))
            elif channel_name in hen_dictionary and check_url_existence(hen_lines, channel_address):
                hen_lines.append(process_name_string(line.strip()))
            elif channel_name in hlj_dictionary and check_url_existence(hlj_lines, channel_address):
                hlj_lines.append(process_name_string(line.strip()))
            elif channel_name in jl_dictionary and check_url_existence(jl_lines, channel_address):
                jl_lines.append(process_name_string(line.strip()))
            elif channel_name in nx_dictionary and check_url_existence(nx_lines, channel_address):
                nx_lines.append(process_name_string(line.strip()))
            elif channel_name in jx_dictionary and check_url_existence(jx_lines, channel_address):
                jx_lines.append(process_name_string(line.strip()))
            elif channel_name in qh_dictionary and check_url_existence(qh_lines, channel_address):
                qh_lines.append(process_name_string(line.strip()))
            elif channel_name in sc_dictionary and check_url_existence(sc_lines, channel_address):
                sc_lines.append(process_name_string(line.strip()))
            elif channel_name in tj_dictionary and check_url_existence(tj_lines, channel_address):
                tj_lines.append(process_name_string(line.strip()))
            elif channel_name in xj_dictionary and check_url_existence(xj_lines, channel_address):
                xj_lines.append(process_name_string(line.strip()))
            elif channel_name in zb_dictionary and check_url_existence(zb_lines, channel_address):
                zb_lines.append(process_name_string(line.strip()))
            elif channel_name in mtv_dictionary and check_url_existence(mtv_lines, channel_address):
                mtv_lines.append(process_name_string(line.strip()))
            elif channel_name in auto_4k_dictionary and check_url_existence(auto_4k_lines, channel_address):
                auto_4k_lines.append(process_name_string(line.strip()))
            else:
                if channel_address not in other_lines_url:
                    other_lines_url.append(channel_address)
                    other_lines.append(line.strip())

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    ]
    return random.choice(USER_AGENTS)

def process_url(url):
    try:
        other_lines.append("◆◆◆　" + url)
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        with urllib.request.urlopen(req) as response:
            data = response.read()
            text = data.decode('utf-8')
            text = text.strip()
            is_m3u = text.startswith("#EXTM3U") or text.startswith("#EXTINF")
            if get_url_file_extension(url) == ".m3u" or get_url_file_extension(url) == ".m3u8" or is_m3u:
                text = convert_m3u_to_txt(text)
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            for line in lines:
                if "#genre#" not in line and "," in line and "://" in line and "tvbus://" not in line and "/udp/" not in line:
                    channel_name, channel_address = line.split(',', 1)
                    if "#" not in channel_address:
                        process_channel_line(line)
                    else:
                        url_list = channel_address.split('#')
                        for channel_url in url_list:
                            newline = f'{channel_name},{channel_url}'
                            process_channel_line(newline)
            other_lines.append('\n')
    except Exception as e:
        print(f"处理URL时发生错误：{e}")

current_directory = os.getcwd()

ys_dictionary = read_txt_to_array('主频道/CCTV.txt')
sh_dictionary = read_txt_to_array('主频道/shanghai.txt')
ws_dictionary = read_txt_to_array('主频道/卫视频道.txt')
ty_dictionary = read_txt_to_array('主频道/体育频道.txt')
tyss_dictionary = read_txt_to_array('主频道/体育赛事.txt')
mgss_dictionary = read_txt_to_array('主频道/咪咕赛事.txt')
dy_dictionary = read_txt_to_array('主频道/电影.txt')
dsj_dictionary = read_txt_to_array('主频道/电视剧.txt')
gat_dictionary = read_txt_to_array('主频道/港澳台.txt')
gj_dictionary = read_txt_to_array('主频道/国际台.txt')
jlp_dictionary = read_txt_to_array('主频道/纪录片.txt')
dhp_dictionary = read_txt_to_array('主频道/动画片.txt')
xq_dictionary = read_txt_to_array('主频道/戏曲频道.txt')
js_dictionary = read_txt_to_array('主频道/解说频道.txt')
cw_dictionary = read_txt_to_array('主频道/春晚.txt')
mx_dictionary = read_txt_to_array('主频道/明星.txt')
ztp_dictionary = read_txt_to_array('主频道/主题片.txt')
zy_dictionary = read_txt_to_array('主频道/综艺频道.txt')
yy_dictionary = read_txt_to_array('主频道/音乐频道.txt')
game_dictionary = read_txt_to_array('主频道/游戏频道.txt')
radio_dictionary = read_txt_to_array('主频道/收音机频道.txt')
auto_4k_dictionary = read_txt_to_array('主频道/auto_4k.txt')
zb_dictionary = read_txt_to_array('主频道/直播中国.txt')
mtv_dictionary = read_txt_to_array('主频道/MTV.txt')
zj_dictionary = read_txt_to_array('地方台/浙江频道.txt')
jsu_dictionary = read_txt_to_array('地方台/江苏频道.txt')
gd_dictionary = read_txt_to_array('地方台/广东频道.txt')
hn_dictionary = read_txt_to_array('地方台/湖南频道.txt')
ah_dictionary = read_txt_to_array('地方台/安徽频道.txt')
hain_dictionary = read_txt_to_array('地方台/海南频道.txt')
nm_dictionary = read_txt_to_array('地方台/内蒙频道.txt')
hb_dictionary = read_txt_to_array('地方台/湖北频道.txt')
ln_dictionary = read_txt_to_array('地方台/辽宁频道.txt')
sx_dictionary = read_txt_to_array('地方台/陕西频道.txt')
shanxi_dictionary = read_txt_to_array('地方台/山西频道.txt')
shandong_dictionary = read_txt_to_array('地方台/山东频道.txt')
yunnan_dictionary = read_txt_to_array('地方台/云南频道.txt')
bj_dictionary = read_txt_to_array('地方台/北京频道.txt')
cq_dictionary = read_txt_to_array('地方台/重庆频道.txt')
fj_dictionary = read_txt_to_array('地方台/福建频道.txt')
gs_dictionary = read_txt_to_array('地方台/甘肃频道.txt')
gx_dictionary = read_txt_to_array('地方台/广西频道.txt')
gz_dictionary = read_txt_to_array('地方台/贵州频道.txt')
heb_dictionary = read_txt_to_array('地方台/河北频道.txt')
hen_dictionary = read_txt_to_array('地方台/河南频道.txt')
hlj_dictionary = read_txt_to_array('地方台/黑龙江频道.txt')
jl_dictionary = read_txt_to_array('地方台/吉林频道.txt')
jx_dictionary = read_txt_to_array('地方台/江西频道.txt')
nx_dictionary = read_txt_to_array('地方台/宁夏频道.txt')
qh_dictionary = read_txt_to_array('地方台/青海频道.txt')
sc_dictionary = read_txt_to_array('地方台/四川频道.txt')
tj_dictionary = read_txt_to_array('地方台/天津频道.txt')
xj_dictionary = read_txt_to_array('地方台/新疆频道.txt')

def load_corrections_name(filename):
    corrections = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split(',')
            correct_name = parts[0]
            for name in parts[1:]:
                corrections[name] = correct_name
    return corrections

corrections_name = load_corrections_name('assets/corrections_name.txt')

def correct_name_data(corrections, data):
    corrected_data = []
    for line in data:
        line = line.strip()
        if ',' not in line:
            continue
        name, url = line.split(',', 1)
        if name in corrections and name != corrections[name]:
            name = corrections[name]
        corrected_data.append(f"{name},{url}")
    return corrected_data

def sort_data(order, data):
    order_dict = {name: i for i, name in enumerate(order)}
    def sort_key(line):
        name = line.split(',')[0]
        return order_dict.get(name, len(order))
    sorted_data = sorted(data, key=sort_key)
    return sorted_data

urls = read_txt_to_array('assets/urls-daily.txt')
for url in urls:
    if url.startswith("http"):
        if "{MMdd}" in url:
            current_date_str = datetime.now().strftime("%m%d")
            url = url.replace("{MMdd}", current_date_str)
        if "{MMdd-1}" in url:
            yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%m%d")
            url = url.replace("{MMdd-1}", yesterday_date_str)
        print(f"处理URL: {url}")
        process_url(url)

def extract_number(s):
    num_str = s.split(',')[0].split('-')[1]
    numbers = re.findall(r'\d+', num_str)
    return int(numbers[-1]) if numbers else 999

def custom_sort(s):
    if "CCTV-4K" in s:
        return 2
    elif "CCTV-8K" in s:
        return 3
    elif "(4K)" in s:
        return 1
    else:
        return 0

print(f"ADD whitelist_auto.txt")
whitelist_auto_lines = read_txt_to_array('assets/blacklist1/whitelist_auto.txt')
for whitelist_line in whitelist_auto_lines:
    if "#genre#" not in whitelist_line and "," in whitelist_line and "://" in whitelist_line:
        whitelist_parts = whitelist_line.split(",")
        try:
            response_time = float(whitelist_parts[0].replace("ms", ""))
        except ValueError:
            print(f"response_time转换失败: {whitelist_line}")
            response_time = 60000
        if response_time < 2000:
            process_channel_line(",".join(whitelist_parts[1:]))

def get_http_response(url, timeout=8, retries=2, backoff_factor=1.0):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                return data.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"[HTTPError] Code: {e.code}, URL: {url}")
            break
        except urllib.error.URLError as e:
            print(f"[URLError] Reason: {e.reason}, Attempt: {attempt + 1}")
        except socket.timeout:
            print(f"[Timeout] URL: {url}, Attempt: {attempt + 1}")
        except Exception as e:
            print(f"[Exception] {type(e).__name__}: {e}, Attempt: {attempt + 1}")
        if attempt < retries - 1:
            time.sleep(backoff_factor * (2 ** attempt))
    return None

def normalize_date_to_md(text):
    text = text.strip()
    def format_md(m):
        month = int(m.group(1))
        day = int(m.group(2))
        after = m.group(3) or ''
        if not after.startswith(' '):
            after = ' ' + after
        return f"{month:02d}-{day:02d}{after}"
    text = re.sub(r'^0?(\d{1,2})/0?(\d{1,2})(.*)', format_md, text)
    text = re.sub(r'^\d{4}-0?(\d{1,2})-0?(\d{1,2})(.*)', format_md, text)
    text = re.sub(r'^0?(\d{1,2})月0?(\d{1,2})日(.*)', format_md, text)
    return text

normalized_tyss_lines = [normalize_date_to_md(s) for s in tyss_lines]

aktv_lines = []
aktv_url = "https://aktv.space/live.m3u"
aktv_text = get_http_response(aktv_url)
if aktv_text:
    print("AKTV成功获取内容")
    aktv_text = convert_m3u_to_txt(aktv_text)
    aktv_lines = aktv_text.strip().split('\n')
else:
    print("AKTV请求失败，从本地获取！")
    aktv_lines = read_txt_to_array('专区/AKTV.txt')

def filter_lines(lines, exclude_keywords):
    return [line for line in lines if not any(keyword in line for keyword in exclude_keywords)]

def generate_playlist_html(data_list, output_file='playlist.html'):
    html_head = '''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">        
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6061710286208572"
     crossorigin="anonymous"></script>
        <!-- Setup Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-BS1Z4F5BDN"></script>
        <script> 
        window.dataLayer = window.dataLayer || []; 
        function gtag(){dataLayer.push(arguments);} 
        gtag('js', new Date()); 
        gtag('config', 'G-BS1Z4F5BDN'); 
        </script>
        <title>最新体育赛事</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f9f9f9; }
            .item { margin-bottom: 20px; padding: 12px; background: #fff; border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
            .title { font-weight: bold; font-size: 1.1em; color: #333; margin-bottom: 5px; }
            .url-wrapper { display: flex; align-items: center; gap: 10px; }
            .url {
                max-width: 80%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.9em;
                color: #555;
                background: #f0f0f0;
                padding: 6px;
                border-radius: 4px;
                flex-grow: 1;
            }
            .copy-btn {
                background-color: #007BFF;
                border: none;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8em;
            }
            .copy-btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
    <h2>📋 最新体育赛事列表</h2>
    '''
    html_body = ''
    for idx, entry in enumerate(data_list):
        if ',' not in entry:
            continue
        info, url = entry.split(',', 1)
        url_id = f"url_{idx}"
        html_body += f'''
        <div class="item">
            <div class="title">🕒 {info}</div>
            <div class="url-wrapper">
                <div class="url" id="{url_id}">{url}</div>
                <button class="copy-btn" onclick="copyToClipboard('{url_id}')">复制</button>
            </div>
        </div>
        '''
    html_tail = '''
    <script>
        function copyToClipboard(id) {
            const el = document.getElementById(id);
            const text = el.textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("已复制链接！");
            }).catch(err => {
                alert("复制失败: " + err);
            });
        }
    </script>
    </body>
    </html>
    '''
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_head + html_body + html_tail)
    print(f"✅ 网页已生成：{output_file}")

def custom_tyss_sort(lines):
    digit_prefix = []
    others = []
    for line in lines:
        name_part = line.split(',')[0].strip()
        if name_part and name_part[0].isdigit():
            digit_prefix.append(line)
        else:
            others.append(line)
    digit_prefix_sorted = sorted(digit_prefix, reverse=True)
    others_sorted = sorted(others)
    return digit_prefix_sorted + others_sorted

keywords_to_exclude_tiyu_txt = ["玉玉软件", "榴芒电视", "公众号", "麻豆", "「回看」"]
normalized_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu_txt)
normalized_tyss_lines = custom_tyss_sort(set(normalized_tyss_lines))
keywords_to_exclude_tiyu = ["玉玉软件", "榴芒电视", "公众号", "咪视通", "麻豆", "「回看」"]
filtered_tyss_lines = filter_lines(normalized_tyss_lines, keywords_to_exclude_tiyu)
generate_playlist_html(filtered_tyss_lines, 'tiyu.html')

def get_random_url(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            url = line.strip().split(',')[-1]
            urls.append(url)
    return random.choice(urls) if urls else None

daily_mtv = "(百)每日一首," + get_random_url('assets/今日推荐.txt')
utc_time = datetime.now(timezone.utc)
beijing_time = utc_time + timedelta(hours=8)
formatted_time = beijing_time.strftime("%Y%m%d %H:%M:%S")
about_video1 = "https://gitee.com/kabigo/tv/raw/master/assets/about1080p.mp4"
about_video2 = "https://gitlab.com/p2v5/wangtv/-/raw/main/about1080p.mp4"
version = formatted_time + "," + about_video1
about = "关于本源(iptv365.org)," + about_video2

print(f"处理手工区...")
zj_lines = zj_lines + read_txt_to_array('手工区/浙江频道.txt')
gd_lines = gd_lines + read_txt_to_array('手工区/广东频道.txt')
hb_lines = hb_lines + read_txt_to_array('手工区/湖北频道.txt')
sh_lines = sh_lines + read_txt_to_array('手工区/上海频道.txt')
jsu_lines = jsu_lines + read_txt_to_array('手工区/江苏频道.txt')

all_lines_simple = ["更新时间,#genre#"] + [version] + [about] + [daily_mtv] + read_txt_to_array('专区/about.txt') + ['\n'] + \
    ["💓专享源🅰️,#genre#"] + read_txt_to_array('专区/♪专享源①.txt') + ['\n'] + \
    ["💓专享源🅱️,#genre#"] + read_txt_to_array('专区/♪专享源②.txt') + ['\n'] + \
    ["💓专享央视,#genre#"] + read_txt_to_array('专区/♪优质央视.txt') + ['\n'] + \
    ["💓专享卫视,#genre#"] + read_txt_to_array('专区/♪优质卫视.txt') + ['\n'] + \
    ["💓港澳台📶,#genre#"] + read_txt_to_array('专区/♪港澳台.txt') + ['\n'] + \
    ["💓台湾台📶,#genre#"] + read_txt_to_array('专区/♪台湾台.txt') + ['\n'] + \
    ["🏈体育赛事🏆️,#genre#"] + normalized_tyss_lines + ['\n'] + \
    ["🏈咪咕赛事🏆️,#genre#"] + mgss_lines + ['\n'] + \
    ["💓咪咕直播,#genre#"] + read_txt_to_array('专区/♪咪咕直播.txt') + ['\n'] + \
    ["⚽️SPORTS,#genre#"] + read_txt_to_array('专区/♪sports.txt') + ['\n'] + \
    ["🎞️电影点播,#genre#"] + read_txt_to_array('专区/♪电影点播.txt') + ['\n'] + \
    ["💓电视剧🔁,#genre#"] + read_txt_to_array('专区/♪电视剧.txt') + ['\n'] + \
    ["💓优质个源,#genre#"] + read_txt_to_array('专区/♪优质源.txt') + ['\n'] + \
    ["💓儿童专享,#genre#"] + read_txt_to_array('专区/♪儿童专享.txt') + ['\n'] + \
    ["🍹定制台☕️,#genre#"] + read_txt_to_array('专区/♪定制源.txt') + ['\n'] + \
    ["🍹定制P3P☕️,#genre#"] + read_txt_to_array('专区/p3p.txt') + ['\n'] + \
    ["💓英语频道,#genre#"] + read_txt_to_array('专区/♪英语频道.txt') + ['\n'] + \
    ["💓4K(Test),#genre#"] + read_txt_to_array('专区/4K.txt') + ['\n'] + \
    ["💓4K(Auto),#genre#"] + sort_data(auto_4k_dictionary, correct_name_data(corrections_name, auto_4k_lines)) + ['\n'] + \
    ["☘️湖南频道,#genre#"] + sort_data(hn_dictionary, set(correct_name_data(corrections_name, hn_lines))) + ['\n'] + \
    ["☘️湖北频道,#genre#"] + sort_data(hb_dictionary, set(correct_name_data(corrections_name, hb_lines))) + ['\n'] + \
    ["☘️广东频道,#genre#"] + sort_data(gd_dictionary, set(correct_name_data(corrections_name, gd_lines))) + ['\n'] + \
    ["☘️浙江频道,#genre#"] + sort_data(zj_dictionary, set(correct_name_data(corrections_name, zj_lines))) + ['\n'] + \
    ["☘️山东频道,#genre#"] + sort_data(shandong_dictionary, set(correct_name_data(corrections_name, shandong_lines))) + ['\n'] + \
    ["上海频道,#genre#"] + sort_data(sh_dictionary, set(correct_name_data(corrections_name, sh_lines))) + ['\n'] + \
    ["体育频道,#genre#"] + sort_data(ty_dictionary, set(correct_name_data(corrections_name, ty_lines))) + ['\n']

all_lines = ["更新时间,#genre#"] + [version] + [about] + [daily_mtv] + read_txt_to_array('专区/about.txt') + ['\n'] + \
    ["💓专享源🅰️,#genre#"] + read_txt_to_array('专区/♪专享源①.txt') + ['\n'] + \
    ["💓专享源🅱️,#genre#"] + read_txt_to_array('专区/♪专享源②.txt') + ['\n'] + \
    ["💓专享央视,#genre#"] + read_txt_to_array('专区/♪优质央视.txt') + ['\n'] + \
    ["💓专享卫视,#genre#"] + read_txt_to_array('专区/♪优质卫视.txt') + ['\n'] + \
    ["💓港澳台📶,#genre#"] + read_txt_to_array('专区/♪港澳台.txt') + ['\n'] + \
    ["💓台湾台📶,#genre#"] + read_txt_to_array('专区/♪台湾台.txt') + ['\n'] + \
    ["🏈体育赛事🏆️,#genre#"] + normalized_tyss_lines + ['\n'] + \
    ["🏈咪咕赛事🏆️,#genre#"] + mgss_lines + ['\n'] + \
    ["💓咪咕直播,#genre#"] + read_txt_to_array('专区/♪咪咕直播.txt') + ['\n'] + \
    ["⚽️SPORTS,#genre#"] + read_txt_to_array('专区/♪sports.txt') + ['\n'] + \
    ["🎞️电影点播,#genre#"] + read_txt_to_array('专区/♪电影点播.txt') + ['\n'] + \
    ["💓电视剧🔁,#genre#"] + read_txt_to_array('专区/♪电视剧.txt') + ['\n'] + \
    ["💓优质个源,#genre#"] + read_txt_to_array('专区/♪优质源.txt') + ['\n'] + \
    ["💓儿童专享,#genre#"] + read_txt_to_array('专区/♪儿童专享.txt') + ['\n'] + \
    ["🍹定制台☕️,#genre#"] + read_txt_to_array('专区/♪定制源.txt') + ['\n'] + \
    ["🍹定制P3P☕️,#genre#"] + read_txt_to_array('专区/p3p.txt') + ['\n'] + \
    ["💓英语频道,#genre#"] + read_txt_to_array('专区/♪英语频道.txt') + ['\n'] + \
    ["💓4K(Test),#genre#"] + read_txt_to_array('专区/4K.txt') + ['\n'] + \
    ["💓4K(Auto),#genre#"] + sort_data(auto_4k_dictionary, correct_name_data(corrections_name, auto_4k_lines)) + ['\n'] + \
    ["🌐央视频道,#genre#"] + sort_data(ys_dictionary, correct_name_data(corrections_name, ys_lines)) + ['\n'] + \
    ["📡卫视频道,#genre#"] + sort_data(ws_dictionary, correct_name_data(corrections_name, ws_lines)) + ['\n'] + \
    ["上海频道,#genre#"] + sort_data(sh_dictionary, correct_name_data(corrections_name, sh_lines)) + ['\n'] + \
    ["体育频道,#genre#"] + sort_data(ty_dictionary, correct_name_data(corrections_name, ty_lines)) + ['\n'] + \
    ["电影频道,#genre#"] + sort_data(dy_dictionary, correct_name_data(corrections_name, dy_lines)) + ['\n'] + \
    ["电视剧频道,#genre#"] + sort_data(dsj_dictionary, correct_name_data(corrections_name, dsj_lines)) + ['\n'] + \
    ["明星,#genre#"] + sort_data(mx_dictionary, correct_name_data(corrections_name, mx_lines)) + ['\n'] + \
    ["主题片,#genre#"] + sort_data(ztp_dictionary, correct_name_data(corrections_name, ztp_lines)) + ['\n'] + \
    ["港澳台,#genre#"] + sort_data(gat_dictionary, correct_name_data(corrections_name, gat_lines)) + ['\n'] + \
    ["国际台,#genre#"] + sort_data(gj_dictionary, set(correct_name_data(corrections_name, gj_lines))) + ['\n'] + \
    ["纪录片,#genre#"] + sort_data(jlp_dictionary, set(correct_name_data(corrections_name, jlp_lines))) + ['\n'] + \
    ["动画片,#genre#"] + sort_data(dhp_dictionary, set(correct_name_data(corrections_name, dhp_lines))) + ['\n'] + \
    ["戏曲频道,#genre#"] + sort_data(xq_dictionary, set(correct_name_data(corrections_name, xq_lines))) + ['\n'] + \
    ["综艺频道,#genre#"] + sorted(set(correct_name_data(corrections_name, zy_lines))) + ['\n'] + \
    ["音乐频道,#genre#"] + sorted(set(yy_lines)) + ['\n'] + \
    ["游戏频道,#genre#"] + sorted(set(game_lines)) + ['\n'] + \
    ["☘️湖南频道,#genre#"] + sort_data(hn_dictionary, set(correct_name_data(corrections_name, hn_lines))) + ['\n'] + \
    ["☘️湖北频道,#genre#"] + sort_data(hb_dictionary, set(correct_name_data(corrections_name, hb_lines))) + ['\n'] + \
    ["☘️广东频道,#genre#"] + sort_data(gd_dictionary, set(correct_name_data(corrections_name, gd_lines))) + ['\n'] + \
    ["☘️浙江频道,#genre#"] + sort_data(zj_dictionary, set(correct_name_data(corrections_name, zj_lines))) + ['\n'] + \
    ["☘️山东频道,#genre#"] + sort_data(shandong_dictionary, set(correct_name_data(corrections_name, shandong_lines))) + ['\n'] + \
    ["☘️江苏频道,#genre#"] + sorted(set(correct_name_data(corrections_name, jsu_lines))) + ['\n'] + \
    ["☘️安徽频道,#genre#"] + sorted(set(correct_name_data(corrections_name, ah_lines))) + ['\n'] + \
    ["☘️海南频道,#genre#"] + sorted(set(correct_name_data(corrections_name, hain_lines))) + ['\n'] + \
    ["☘️内蒙频道,#genre#"] + sorted(set(correct_name_data(corrections_name, nm_lines))) + ['\n'] + \
    ["☘️辽宁频道,#genre#"] + sorted(set(correct_name_data(corrections_name, ln_lines))) + ['\n'] + \
    ["☘️陕西频道,#genre#"] + sorted(set(correct_name_data(corrections_name, sx_lines))) + ['\n'] + \
    ["☘️山西频道,#genre#"] + sorted(set(correct_name_data(corrections_name, shanxi_lines))) + ['\n'] + \
    ["☘️云南频道,#genre#"] + sorted(set(correct_name_data(corrections_name, yunnan_lines))) + ['\n'] + \
    ["☘️北京频道,#genre#"] + sorted(set(correct_name_data(corrections_name, bj_lines))) + ['\n'] + \
    ["☘️重庆频道,#genre#"] + sorted(set(correct_name_data(corrections_name, cq_lines))) + ['\n'] + \
    ["☘️福建频道,#genre#"] + sorted(set(correct_name_data(corrections_name, fj_lines))) + ['\n'] + \
    ["☘️甘肃频道,#genre#"] + sorted(set(correct_name_data(corrections_name, gs_lines))) + ['\n'] + \
    ["☘️广西频道,#genre#"] + sorted(set(correct_name_data(corrections_name, gx_lines))) + ['\n'] + \
    ["☘️贵州频道,#genre#"] + sorted(set(correct_name_data(corrections_name, gz_lines))) + ['\n'] + \
    ["☘️河北频道,#genre#"] + sorted(set(correct_name_data(corrections_name, heb_lines))) + ['\n'] + \
    ["☘️河南频道,#genre#"] + sorted(set(correct_name_data(corrections_name, hen_lines))) + ['\n'] + \
    ["☘️黑龙江频道,#genre#"] + sorted(set(correct_name_data(corrections_name, hlj_lines))) + ['\n'] + \
    ["☘️吉林频道,#genre#"] + sorted(set(correct_name_data(corrections_name, jl_lines))) + ['\n'] + \
    ["☘️江西频道,#genre#"] + sorted(set(correct_name_data(corrections_name, jx_lines))) + ['\n'] + \
    ["☘️宁夏频道,#genre#"] + sorted(set(correct_name_data(corrections_name, nx_lines))) + ['\n'] + \
    ["☘️青海频道,#genre#"] + sorted(set(correct_name_data(corrections_name, qh_lines))) + ['\n'] + \
    ["☘️四川频道,#genre#"] + sorted(set(correct_name_data(corrections_name, sc_lines))) + ['\n'] + \
    ["☘️天津频道,#genre#"] + sorted(set(correct_name_data(corrections_name, tj_lines))) + ['\n'] + \
    ["☘️新疆频道,#genre#"] + sorted(set(correct_name_data(corrections_name, xj_lines))) + ['\n'] + \
    ["解说频道,#genre#"] + sorted(set(js_lines)) + ['\n'] + \
    ["春晚,#genre#"] + sort_data(cw_dictionary, set(cw_lines)) + ['\n'] + \
    ["直播中国,#genre#"] + sorted(set(correct_name_data(corrections_name, zb_lines))) + ['\n'] + \
    ["MTV,#genre#"] + sorted(set(correct_name_data(corrections_name, mtv_lines))) + ['\n'] + \
    ["收音机频道,#genre#"] + sort_data(radio_dictionary, set(radio_lines)) + ['\n'] + \
    ["❤️雪中悍刀行,#genre#"] + read_txt_to_array('专区/特供频道/♪雪中悍刀行.txt') + ['\n'] + \
    ["❤️以家人之名,#genre#"] + read_txt_to_array('专区/特供频道/♪以家人之名.txt')

output_file = "merged_output.txt"
output_file_simple = "merged_output_simple.txt"
others_file = "others_output.txt"
new_output_file = "bbxx.txt"
new_output_file_simple = "bbxx_lite.txt"

try:
    with open(new_output_file_simple, 'w', encoding='utf-8') as f:
        for line in all_lines_simple:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {new_output_file_simple}")
    with open(new_output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {new_output_file}")
    with open(others_file, 'w', encoding='utf-8') as f:
        for line in other_lines:
            f.write(line + '\n')
    print(f"Others已保存到文件: {others_file}")
except Exception as e:
    print(f"保存文件时发生错误：{e}")

channels_logos = read_txt_to_array('assets/logo.txt')

def get_logo_by_channel_name(channel_name):
    for line in channels_logos:
        if not line.strip():
            continue
        name, url = line.split(',')
        if name == channel_name:
            return url
    return None

def make_m3u(txt_file, m3u_file):
    try:
        output_text = '#EXTM3U x-tvg-url="https://live.fanmingming.cn/e.xml"\n'
        with open(txt_file, "r", encoding='utf-8') as file:
            input_text = file.read()
        lines = input_text.strip().split("\n")
        group_name = ""
        for line in lines:
            parts = line.split(",")
            if len(parts) == 2 and "#genre#" in line:
                group_name = parts[0]
            elif len(parts) == 2:
                channel_name = parts[0]
                channel_url = parts[1]
                logo_url = get_logo_by_channel_name(channel_name)
                if logo_url is None:
                    output_text += f"#EXTINF:-1 group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
                else:
                    output_text += f"#EXTINF:-1  tvg-name=\"{channel_name}\" tvg-logo=\"{logo_url}\"  group-title=\"{group_name}\",{channel_name}\n"
                    output_text += f"{channel_url}\n"
        with open(f"{m3u_file}", "w", encoding='utf-8') as file:
            file.write(output_text)
        print(f"M3U文件 '{m3u_file}' 生成成功。")
    except Exception as e:
        print(f"发生错误: {e}")

make_m3u(new_output_file, new_output_file.replace(".txt", ".m3u"))
make_m3u(new_output_file_simple, new_output_file_simple.replace(".txt", ".m3u"))

timeend = datetime.now()
elapsed_time = timeend - timestart
total_seconds = elapsed_time.total_seconds()
minutes = int(total_seconds // 60)
seconds = int(total_seconds % 60)
timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")
print(f"开始时间: {timestart_str}")
print(f"结束时间: {timeend_str}")
print(f"执行时间: {minutes} 分 {seconds} 秒")
combined_blacklist_hj = len(combined_blacklist)
all_lines_hj = len(all_lines)
other_lines_hj = len(other_lines)
print(f"黑名单行数: {combined_blacklist_hj} ")
print(f"txt行数: {all_lines_hj} ")
print(f"other行数: {other_lines_hj} ")