#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telebot, requests as req, time, uuid, warnings
from telebot import types
from datetime import datetime
warnings.filterwarnings('ignore')

BOT_TOKEN = "8859712974:AAEtM8x8Ac0xNVrjM55dKyAfQugz_wgNmVE"
ADMIN_ID = 8931155476
ADMIN_USER = "@SUMIT_X_OFFICIAL"
FIREBASE_URL = "https://hihehdhd-15a54-default-rtdb.asia-southeast1.firebasedatabase.app"
BOT_OWNER = "SUMIT"

bot = telebot.TeleBot(BOT_TOKEN)

class DB:
    def __init__(self,u): self.u=u.rstrip('/')
    def r(self,m,p,d=None):
        try: r=req.request(m,f"{self.u}/{p}.json",json=d,timeout=10); return r.json() if r.text else {}
        except: return None
    def get(self,uid): return self.r("GET",f"users/{uid}")
    def all(self): return self.r("GET","users") or {}
    def logs(self,uid): return self.r("GET",f"logs/{uid}") or {}
    def up_att(self,uid,c): self.r("PUT",f"users/{uid}/att",c)
    def ban(self,uid,r=""): self.r("PATCH",f"users/{uid}",{"ban":True,"reason":r})
    def unban(self,uid): self.r("PATCH",f"users/{uid}",{"ban":False,"reason":""})
    def set_plan(self,uid,p): self.r("PATCH",f"users/{uid}",{"plan":p})

db = DB(FIREBASE_URL)

def admin_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("👥 ALL USERS",callback_data="users"),types.InlineKeyboardButton("🚫 BANNED",callback_data="banned"))
    markup.add(types.InlineKeyboardButton("📊 GLOBAL STATS",callback_data="gstats"),types.InlineKeyboardButton("🏆 TOP 15",callback_data="top"))
    markup.add(types.InlineKeyboardButton("🔍 USER INFO",callback_data="suser"),types.InlineKeyboardButton("📋 USER LOGS",callback_data="ulogs"))
    markup.add(types.InlineKeyboardButton("📢 BROADCAST",callback_data="bcast"),types.InlineKeyboardButton("🔄 RESET USER",callback_data="ruser"))
    markup.add(types.InlineKeyboardButton("🔒 LOGOUT",callback_data="logout"))
    return markup

def check_admin(m):
    if m.from_user.id != ADMIN_ID:
        bot.send_message(m.chat.id,"❌ *Unauthorized!*",parse_mode="Markdown")
        return False
    return True

@bot.message_handler(commands=['start','admin','panel'])
def start(m):
    if not check_admin(m): return
    bot.send_message(m.chat.id,f"👑 *ADMIN PANEL - {BOT_OWNER}*\n━━━━━━━━━━━━━━━━━━━\nWelcome Admin!\nUse buttons or commands.",parse_mode="Markdown",reply_markup=admin_kb())

# ===== COMMANDS =====
@bot.message_handler(commands=['users'])
def cmd_users(m):
    if not check_admin(m): return
    allu=db.all()
    if not allu: return bot.send_message(m.chat.id,"❌ *No users*",parse_mode="Markdown")
    txt=f"👥 *ALL USERS ({len(allu)})*\n━━━━━━━━━━━━━━━━━━━\n"
    cnt=0
    for uid,d in sorted(allu.items(),key=lambda x: x[1].get('att',0) if isinstance(x[1],dict) else 0,reverse=True):
        if cnt>=50: txt+=f"\n... +{len(allu)-50} more"; break
        if isinstance(d,dict):
            b="🚫" if d.get("ban") else "✅"
            txt+=f"{b} `{uid}` @{d.get('username','?')} | `{d.get('att',0)}` | `{d.get('plan','free')}`\n"; cnt+=1
    txt+="━━━━━━━━━━━━━━━━━━━"
    bot.send_message(m.chat.id,txt,parse_mode="Markdown")

@bot.message_handler(commands=['ban'])
def cmd_ban(m):
    if not check_admin(m): return
    p=m.text.split(maxsplit=2)
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/ban <id> [reason]`",parse_mode="Markdown")
    try:
        tid=int(p[1]); r=p[2] if len(p)>2 else "Violation"
        db.ban(tid,r)
        bot.send_message(m.chat.id,f"✅ *Banned*\n👤 `{tid}`\n📝 `{r}`",parse_mode="Markdown")
        try: bot.send_message(tid,f"❌ *Banned!*\nReason: `{r}`\nContact: {ADMIN_USER}",parse_mode="Markdown")
        except: pass
    except: bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")

@bot.message_handler(commands=['unban'])
def cmd_unban(m):
    if not check_admin(m): return
    p=m.text.split()
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/unban <id>`",parse_mode="Markdown")
    try: tid=int(p[1]); db.unban(tid); bot.send_message(m.chat.id,f"✅ *Unbanned* `{tid}`",parse_mode="Markdown")
    except: bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")

@bot.message_handler(commands=['userinfo'])
def cmd_uinfo(m):
    if not check_admin(m): return
    p=m.text.split()
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/userinfo <id>`",parse_mode="Markdown")
    try: uid=int(p[1])
    except: return bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")
    d=db.get(uid)
    if not d: return bot.send_message(m.chat.id,f"❌ `{uid}` not found",parse_mode="Markdown")
    l=db.logs(uid)
    bot.send_message(m.chat.id,f"""👤 *USER INFO*
━━━━━━━━━━━━━━━━━━━
🆔 `{uid}`
📛 @{d.get('username','?')}
💥 Attacks: `{d.get('att',0)}`
🚫 Banned: `{'Yes' if d.get('ban') else 'No'}`
📝 Reason: `{d.get('reason','N/A')}`
📅 First: `{d.get('first','?')}`
📜 Logs: `{len(l)}`
💎 Plan: `{d.get('plan','free')}`
━━━━━━━━━━━━━━━━━━━""",parse_mode="Markdown")

@bot.message_handler(commands=['banned'])
def cmd_banned(m):
    if not check_admin(m): return
    allu=db.all()
    bd=[(uid,d) for uid,d in allu.items() if isinstance(d,dict) and d.get("ban")]
    if not bd: return bot.send_message(m.chat.id,"✅ *No banned users*",parse_mode="Markdown")
    txt=f"🚫 *BANNED ({len(bd)})*\n━━━━━━━━━━━━━━━━━━━\n"
    for uid,d in bd: txt+=f"👤 `{uid}` @{d.get('username','?')}\n📝 `{d.get('reason','N/A')}`\n━━━━━━\n"
    bot.send_message(m.chat.id,txt,parse_mode="Markdown")

@bot.message_handler(commands=['logs'])
def cmd_logs(m):
    if not check_admin(m): return
    p=m.text.split()
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/logs <id>`",parse_mode="Markdown")
    try: uid=int(p[1])
    except: return bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")
    l=db.logs(uid)
    if not l: return bot.send_message(m.chat.id,f"📜 No logs for `{uid}`",parse_mode="Markdown")
    txt=f"📜 *LOGS: `{uid}` ({len(l)})*\n━━━━━━━━━━━━━━━━━━━\n"
    for lid,log in list(l.items())[:20]:
        txt+=f"🎯 `{log.get('target','?')}` ⚔️ `{log.get('method','?')}` 📊 `{log.get('status','?')}` ⏱️ `{str(log.get('time','?'))[:19]}`\n"
    if len(l)>20: txt+=f"\n... +{len(l)-20} more"
    txt+="━━━━━━━━━━━━━━━━━━━"
    bot.send_message(m.chat.id,txt,parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def cmd_bcast(m):
    if not check_admin(m): return
    p=m.text.split(maxsplit=1)
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/broadcast <msg>`",parse_mode="Markdown")
    msg=p[1]; allu=db.all(); s=f=0
    for uid in allu:
        try: bot.send_message(int(uid),f"📢 *BROADCAST*\n\n{msg}\n\n— {ADMIN_USER}",parse_mode="Markdown"); s+=1
        except: f+=1
        time.sleep(0.04)
    bot.send_message(m.chat.id,f"✅ *Done*\n📨 Sent: `{s}`\n❌ Failed: `{f}`",parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def cmd_reset(m):
    if not check_admin(m): return
    p=m.text.split()
    if len(p)<2: return bot.send_message(m.chat.id,"❌ `/reset <id>`",parse_mode="Markdown")
    try: uid=int(p[1]); db.up_att(uid,0); bot.send_message(m.chat.id,f"✅ *Reset* `{uid}` → 0",parse_mode="Markdown")
    except: bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")

@bot.message_handler(commands=['setplan'])
def cmd_setplan(m):
    if not check_admin(m): return
    p=m.text.split()
    if len(p)<3: return bot.send_message(m.chat.id,"❌ `/setplan <id> <plan>`",parse_mode="Markdown")
    try: uid=int(p[1]); plan=p[2]; db.set_plan(uid,plan); bot.send_message(m.chat.id,f"✅ `{uid}` → `{plan}`",parse_mode="Markdown")
    except: bot.send_message(m.chat.id,"❌ *Invalid*",parse_mode="Markdown")

# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    if c.from_user.id!=ADMIN_ID: return bot.answer_callback_query(c.id,"❌ Unauthorized!",show_alert=True)
    d=c.data; cid=c.message.chat.id; mid=c.message.message_id

    if d=="logout":
        bot.edit_message_text("🔒 *Panel Closed*\nSend /admin to reopen.",cid,mid,parse_mode="Markdown")
        bot.answer_callback_query(c.id); return

    if d=="users":
        allu=db.all()
        if not allu: return bot.edit_message_text("❌ *No users*",cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        txt=f"👥 *ALL USERS ({len(allu)})*\n━━━━━━━━━━━━━━━━━━━\n"; cnt=0
        for uid,d2 in sorted(allu.items(),key=lambda x: x[1].get('att',0) if isinstance(x[1],dict) else 0,reverse=True):
            if cnt>=30: break
            if isinstance(d2,dict):
                b="🚫" if d2.get("ban") else "✅"
                txt+=f"{b} `{uid}` @{d2.get('username','?')} | `{d2.get('att',0)}`\n"; cnt+=1
        if len(allu)>30: txt+=f"\n... +{len(allu)-30} more"
        txt+="\n━━━━━━━━━━━━━━━━━━━"
        bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        bot.answer_callback_query(c.id); return

    if d=="banned":
        allu=db.all(); bd=[(uid,d2) for uid,d2 in allu.items() if isinstance(d2,dict) and d2.get("ban")]
        if not bd: return bot.edit_message_text("✅ *No banned*",cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        txt=f"🚫 *BANNED ({len(bd)})*\n━━━━━━━━━━━━━━━━━━━\n"
        for uid,d2 in bd: txt+=f"👤 `{uid}` @{d2.get('username','?')}\n📝 `{d2.get('reason','N/A')}`\n━━━━━━\n"
        bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        bot.answer_callback_query(c.id); return

    if d=="gstats":
        allu=db.all(); tu=len(allu) if allu else 0; ta=0
        if allu:
            for uid,d2 in allu.items():
                if isinstance(d2,dict): ta+=d2.get("att",0)
        top=sorted([(uid,d2) for uid,d2 in allu.items() if isinstance(d2,dict)],key=lambda x: x[1].get("att",0),reverse=True)[:5]
        txt=f"📊 *GLOBAL STATS*\n━━━━━━━━━━━━━━━━━━━\n👥 Users: `{tu}`\n💣 Total Attacks: `{ta:,}`\n━━━━━━━━━━━━━━━━━━━\n\n🏆 *TOP 5:*\n"
        for i,(uid,d2) in enumerate(top,1): txt+=f"#{i} `{uid}` @{d2.get('username','?')} — `{d2.get('att',0)}`\n"
        bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        bot.answer_callback_query(c.id); return

    if d=="top":
        allu=db.all()
        top=sorted([(uid,d2) for uid,d2 in allu.items() if isinstance(d2,dict)],key=lambda x: x[1].get("att",0),reverse=True)[:15]
        txt="🏆 *TOP 15 USERS*\n━━━━━━━━━━━━━━━━━━━\n"; medals=["🥇","🥈","🥉"]
        for i,(uid,d2) in enumerate(top,1):
            m=medals[i-1] if i<=3 else f"#{i}"
            txt+=f"{m} `{uid}` @{d2.get('username','?')} — `{d2.get('att',0)}`\n"
        txt+="━━━━━━━━━━━━━━━━━━━"
        bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        bot.answer_callback_query(c.id); return

    if d in ("suser","ulogs","ruser","bcast"):
        msgs={"suser":"🔍 *Send user ID to lookup:*","ulogs":"📋 *Send user ID for logs:*","ruser":"🔄 *Send user ID to reset attacks:*","bcast":"📢 *Send broadcast message:*"}
        bot.edit_message_text(msgs[d],cid,mid,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 BACK",callback_data="back")))
        handlers={"suser":handle_userinfo,"ulogs":handle_logs,"ruser":handle_reset,"bcast":handle_bcast}
        bot.register_next_step_handler_by_chat_id(cid,handlers[d])
        bot.answer_callback_query(c.id); return

    if d=="back":
        bot.edit_message_text(f"👑 *ADMIN PANEL - {BOT_OWNER}*",cid,mid,parse_mode="Markdown",reply_markup=admin_kb())
        bot.answer_callback_query(c.id); return

def handle_bcast(m):
    if m.from_user.id!=ADMIN_ID: return
    msg=m.text; allu=db.all(); s=f=0
    for uid in allu:
        try: bot.send_message(int(uid),f"📢 *BROADCAST*\n\n{msg}\n\n— {ADMIN_USER}",parse_mode="Markdown"); s+=1
        except: f+=1
        time.sleep(0.04)
    bot.reply_to(m,f"✅ Sent: `{s}` | Failed: `{f}`",parse_mode="Markdown",reply_markup=admin_kb())

def handle_userinfo(m):
    if m.from_user.id!=ADMIN_ID: return
    try: uid=int(m.text.strip())
    except: return bot.reply_to(m,"❌ *Invalid ID*",parse_mode="Markdown",reply_markup=admin_kb())
    d=db.get(uid)
    if not d: return bot.reply_to(m,f"❌ `{uid}` not found",parse_mode="Markdown",reply_markup=admin_kb())
    l=db.logs(uid)
    bot.reply_to(m,f"""👤 *USER INFO*
━━━━━━━━━━━━━━━━━━━
🆔 `{uid}`
📛 @{d.get('username','?')}
💥 Attacks: `{d.get('att',0)}`
🚫 Banned: `{'Yes' if d.get('ban') else 'No'}`
📝 Reason: `{d.get('reason','N/A')}`
📅 First: `{d.get('first','?')}`
📜 Logs: `{len(l)}`
💎 Plan: `{d.get('plan','free')}`
━━━━━━━━━━━━━━━━━━━""",parse_mode="Markdown",reply_markup=admin_kb())

def handle_reset(m):
    if m.from_user.id!=ADMIN_ID: return
    try: uid=int(m.text.strip()); db.up_att(uid,0); bot.reply_to(m,f"✅ *Reset* `{uid}` → 0",parse_mode="Markdown",reply_markup=admin_kb())
    except: bot.reply_to(m,"❌ *Invalid*",parse_mode="Markdown",reply_markup=admin_kb())

def handle_logs(m):
    if m.from_user.id!=ADMIN_ID: return
    try: uid=int(m.text.strip())
    except: return bot.reply_to(m,"❌ *Invalid*",parse_mode="Markdown",reply_markup=admin_kb())
    l=db.logs(uid)
    if not l: return bot.reply_to(m,f"📜 No logs for `{uid}`",parse_mode="Markdown",reply_markup=admin_kb())
    txt=f"📜 *LOGS: `{uid}` ({len(l)})*\n━━━━━━━━━━━━━━━━━━━\n"
    for lid,log in list(l.items())[:20]:
        txt+=f"🎯 `{log.get('target','?')}` ⚔️ `{log.get('method','?')}` 📊 `{log.get('status','?')}` ⏱️ `{str(log.get('time','?'))[:19]}`\n"
    if len(l)>20: txt+=f"\n... +{len(l)-20} more"
    txt+="━━━━━━━━━━━━━━━━━━━"
    bot.reply_to(m,txt,parse_mode="Markdown",reply_markup=admin_kb())

# ===== RUN =====
print(f"""
╔══════════════════════════════════╗
║    SUMIT ADMIN PANEL LOADED     ║
╠══════════════════════════════════╣
║  Admin: {ADMIN_USER}              ║
║  Owner: {BOT_OWNER}                        ║
║  Commands: /admin /panel        ║
╚══════════════════════════════════╝
""")
try: bot.infinity_polling(timeout=60)
except KeyboardInterrupt: print("\n[!] Stopped")
except Exception as e: print(f"[!] Error: {e}")
