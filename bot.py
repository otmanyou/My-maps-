import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import os

# إعداد السجل لتسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# إدخال الـ Token الخاص بالبوت

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# معرف المستخدم الإداري
ADMIN_ID = 5164991393  # معرف الأدمن

# قائمة للمستخدمين (كمثال بدائي لإحصائيات المستخدمين)
users_db = []

# دالة لإرسال الرسائل عبر البوت
async def send_message(update: Update, message: str, reply_markup=None):
    """ترسل رسالة إلى المستخدم."""
    try:
        await update.message.reply_text(message, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"خطأ أثناء إرسال الرسالة: {e}")

async def send_admin_notification(context, text):
    """إرسال إشعار إلى الأدمن."""
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        logging.error(f"خطأ أثناء إرسال إشعار للأدمن: {e}")

# إعداد لوحة أزرار الإدارة
def get_admin_buttons():
    """إعداد لوحة أزرار الإدارة."""
    keyboard = [
        ["عدد المستخدمين", "إحصائيات"],
        ["حظر المستخدم", "حذف الرسالة"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# عرض رسالة ترحيبية لأي مستخدم وإشعار الأدمن
async def start_handler(update: Update, context):
    """إرسال رسالة ترحيبية عند دخول المستخدم وإشعار الأدمن."""
    user = update.message.from_user
    user_info = {
        "id": user.id,
        "name": user.first_name,
        "username": user.username or "لا يوجد",
    }

    # تسجيل المستخدم الجديد في قاعدة البيانات
    if user_info["id"] not in [u["id"] for u in users_db]:
        users_db.append(user_info)
    
    # رسالة ترحيبية للمستخدم
    welcome_message = (
        f"🎉 أهلاً وسهلاً بك، {user_info['name']}! 🎉\n\n" 
"انا ذكاء إصطناعي شرير ولست لطيف لا أهتم بالقوانين 🚮"
"\n\n"
        "🚀 نحن سعداء بانضمامك إلينا. إذا كنت بحاجة إلى مساعدة، فقط أرسل رسالة هنا."
    )
    await send_message(update, welcome_message)

    # إشعار الإداري بدخول المستخدم
    admin_notification = (
        f"🔔 مستخدم جديد دخل البوت!\n\n"
        f"👤 الاسم: {user_info['name']}\n"
        f"💬 اسم المستخدم: @{user_info['username']}\n"
        f"🆔 المعرف: {user_info['id']}"
    )
    await send_admin_notification(context, admin_notification)

    # إذا كان المستخدم هو الأدمن، عرض قائمة الأزرار الإدارية
    if user.id == ADMIN_ID:
        admin_welcome = (
            "🎉 مرحباً بك أيها المدير العظيم! 🎉\n\n"
            "🔹 يمكنك الآن التحكم في البوت بسهولة من خلال الأزرار أدناه.\n"
        )
        reply_markup = get_admin_buttons()
        await send_message(update, admin_welcome, reply_markup=reply_markup)

# معالجة الرسائل الواردة
async def handle_message(update: Update, context):
    """تعالج الرسائل الواردة بناءً على النص."""
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    # أوامر ديناميكية للإدارة
    if text == "عدد المستخدمين":
        count_message = f"👥 عدد المستخدمين: {len(users_db)}"
        await send_message(update, count_message)

    elif text == "إحصائيات":
        stats_message = (
            f"📊 إحصائيات البوت:\n"
            f"- 👥 عدد المستخدمين: {len(users_db)}\n"
            f"- 💬 الرسائل المستلمة: {context.bot_data.get('messages_count', 0)}"
        )
        await send_message(update, stats_message)

    elif text == "حظر المستخدم":
        # يمكنك توسيع هذا لتطبيق ميزة الحظر الفعلية
        await send_message(update, "🚫 ميزة حظر المستخدم قيد التطوير.")

    elif text == "حذف الرسالة":
        # يمكنك إضافة منطق حذف الرسائل لاحقًا
        await send_message(update, "🗑️ ميزة حذف الرسائل قيد التطوير.")

    else:
        # إرسال النصوص العامة إلى API
        await handle_general_text(update, text)

# دالة لتحليل النصوص وإرسال طلب API
async def handle_general_text(update: Update, text: str):
    """معالجة النصوص العادية باستخدام API خارجي."""
    try:
        url = f"https://tamtam.freewebhostmost.com/apiAhmed.php?user_input={text}"
        response = requests.get(url)
        if response.status_code == 200:
            # تعديل النص: حذف الأقواس [] واستبدال 💡 بـ OTH👨‍💻
            gpt_response = (
                response.text
                .replace("Ahmed", "")
                .replace("\r\n", "")
                .replace("\n", "")
                .replace("الذكاء الاصطناعي", "OTH")
                .replace("[", "")
                .replace("]", "")
            )
            await send_message(update, f"OTH👨‍💻 : {gpt_response}")
        else:
            await send_message(update, "❌ حدث خطأ أثناء الاتصال بـ API.")
    except Exception as e:
        logging.error(f"خطأ أثناء الاتصال بـ API: {e}")
        await send_message(update, "❌ حدث خطأ غير متوقع.")

# الإعداد الرئيسي للبرنامج
def main():
    """تشغيل البوت."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start_handler))

    # إضافة معالج الرسائل العامة
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء تشغيل البوت
    application.run_polling()

if __name__ == "__main__":
    main()
