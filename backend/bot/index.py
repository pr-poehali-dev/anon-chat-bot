"""
AvaMatch Bot — анонимные знакомства для игроков Avakin Life.
Обрабатывает все входящие обновления от Telegram через webhook.
"""

import os
import json
import requests
import psycopg2
import re

SCHEMA = "t_p59360323_anon_chat_bot"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

MAT_WORDS = [
    "хуй", "хуи", "пизд", "ебл", "ебат", "ёбан", "блять", "блядь", "сука", "пидор",
    "мудак", "залупа", "ёбан", "ёб", "уёб", "пиздец", "пиздёж", "манда", "шлюх",
    "проститут", "дрочи", "дрочит", "выёб", "наебал", "наебат", "заебал", "заебат",
    "ёбаный", "ёбаная", "ёбаное", "долбоёб", "хуйня", "пиздёт", "заеб"
]

def contains_mat(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    for word in MAT_WORDS:
        if word in t:
            return True
    return False

def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def send(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{API}/sendMessage", json=payload, timeout=10)

def send_photo(chat_id, file_id, caption=None, reply_markup=None):
    payload = {"chat_id": chat_id, "photo": file_id}
    if caption:
        payload["caption"] = caption
        payload["parse_mode"] = "HTML"
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{API}/sendPhoto", json=payload, timeout=10)

def forward_message(from_msg, to_chat_id):
    """Пересылает любой тип сообщения анонимно (скрывая отправителя)."""
    msg_type = None
    if from_msg.get("text"):
        msg_type = "text"
    elif from_msg.get("photo"):
        msg_type = "photo"
    elif from_msg.get("sticker"):
        msg_type = "sticker"
    elif from_msg.get("voice"):
        msg_type = "voice"
    elif from_msg.get("video"):
        msg_type = "video"
    elif from_msg.get("document"):
        msg_type = "document"

    if msg_type == "text":
        text = from_msg["text"]
        if contains_mat(text):
            return False
        send(to_chat_id, f"💬 <b>Анонимное сообщение:</b>\n{text}")
    elif msg_type == "photo":
        file_id = from_msg["photo"][-1]["file_id"]
        caption = from_msg.get("caption", "")
        send_photo(to_chat_id, file_id, caption=f"📸 <b>Анонимное фото</b>\n{caption}" if caption else "📸 <b>Анонимное фото</b>")
    elif msg_type == "sticker":
        requests.post(f"{API}/sendSticker", json={"chat_id": to_chat_id, "sticker": from_msg["sticker"]["file_id"]}, timeout=10)
    elif msg_type == "voice":
        requests.post(f"{API}/sendVoice", json={"chat_id": to_chat_id, "voice": from_msg["voice"]["file_id"]}, timeout=10)
    elif msg_type == "video":
        requests.post(f"{API}/sendVideo", json={"chat_id": to_chat_id, "video": from_msg["video"]["file_id"]}, timeout=10)
    elif msg_type == "document":
        requests.post(f"{API}/sendDocument", json={"chat_id": to_chat_id, "document": from_msg["document"]["file_id"]}, timeout=10)
    return True

def get_user(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, is_banned, state, complaint_count FROM {SCHEMA}.users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row

def ensure_user(conn, user_id, username):
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {SCHEMA}.users (id, username)
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
    """, (user_id, username or ""))
    conn.commit()
    cur.close()

def set_state(conn, user_id, state):
    cur = conn.cursor()
    cur.execute(f"UPDATE {SCHEMA}.users SET state = %s WHERE id = %s", (state, user_id))
    conn.commit()
    cur.close()

def get_profile(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"SELECT avakin_nick, gender, orientation, age, photo_file_id, likes, dislikes FROM {SCHEMA}.profiles WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row

def get_next_profile(conn, viewer_id):
    """Возвращает следующую анкету которую пользователь ещё не смотрел."""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT p.user_id, p.avakin_nick, p.gender, p.orientation, p.age, p.photo_file_id, p.likes
        FROM {SCHEMA}.profiles p
        WHERE p.is_active = TRUE
          AND p.user_id != %s
          AND p.user_id NOT IN (
              SELECT vp.viewed_user_id FROM {SCHEMA}.viewed_profiles vp WHERE vp.user_id = %s
          )
          AND p.user_id NOT IN (
              SELECT u.id FROM {SCHEMA}.users u WHERE u.is_banned = TRUE
          )
        ORDER BY RANDOM()
        LIMIT 1
    """, (viewer_id, viewer_id))
    row = cur.fetchone()
    cur.close()
    return row

def mark_viewed(conn, viewer_id, viewed_id):
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {SCHEMA}.viewed_profiles (user_id, viewed_user_id)
        VALUES (%s, %s) ON CONFLICT DO NOTHING
    """, (viewer_id, viewed_id))
    conn.commit()
    cur.close()

def get_active_chat(conn, user_id):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, user_a, user_b FROM {SCHEMA}.chats
        WHERE is_active = TRUE AND (user_a = %s OR user_b = %s)
        LIMIT 1
    """, (user_id, user_id))
    row = cur.fetchone()
    cur.close()
    return row

def end_chat(conn, chat_id):
    cur = conn.cursor()
    cur.execute(f"UPDATE {SCHEMA}.chats SET is_active = FALSE, ended_at = NOW() WHERE id = %s", (chat_id,))
    conn.commit()
    cur.close()

def check_match(conn, user_a, user_b):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id FROM {SCHEMA}.likes
        WHERE from_user_id = %s AND to_user_id = %s AND is_like = TRUE
    """, (user_b, user_a))
    row = cur.fetchone()
    cur.close()
    return row is not None

def start_chat(conn, user_a, user_b):
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {SCHEMA}.chats (user_a, user_b)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_a, user_b))
    conn.commit()
    cur.close()

def add_complaint(conn, from_id, to_id, reason):
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {SCHEMA}.complaints (from_user_id, to_user_id, reason) VALUES (%s, %s, %s)", (from_id, to_id, reason))
    cur.execute(f"UPDATE {SCHEMA}.users SET complaint_count = complaint_count + 1 WHERE id = %s", (to_id,))
    cur.execute(f"SELECT complaint_count FROM {SCHEMA}.users WHERE id = %s", (to_id,))
    count = cur.fetchone()[0]
    if count >= 3:
        cur.execute(f"UPDATE {SCHEMA}.users SET is_banned = TRUE, ban_reason = 'Автоблокировка: 3+ жалобы' WHERE id = %s", (to_id,))
    conn.commit()
    cur.close()
    return count

def profile_text(nick, gender, orientation, age, likes):
    gender_map = {"male": "👦 Парень", "female": "👧 Девушка", "other": "🌈 Другой"}
    orient_map = {"hetero": "Гетеро", "homo": "Гомо", "bi": "Би", "other": "Другая"}
    g = gender_map.get(gender, gender)
    o = orient_map.get(orientation, orientation)
    return (
        f"✨ <b>{nick}</b>\n"
        f"{g} · {o} · {age} лет\n"
        f"❤️ Лайков: {likes}"
    )

def main_menu():
    return {"keyboard": [
        [{"text": "📋 Моя анкета"}, {"text": "🔍 Смотреть анкеты"}],
        [{"text": "💬 Мой чат"}, {"text": "⭐ Отзывы"}],
        [{"text": "ℹ️ Помощь"}]
    ], "resize_keyboard": True}

def browse_keyboard(target_user_id):
    return {"inline_keyboard": [
        [
            {"text": "❤️ Лайк", "callback_data": f"like_{target_user_id}"},
            {"text": "👎 Дизлайк", "callback_data": f"dislike_{target_user_id}"}
        ],
        [{"text": "💬 Написать", "callback_data": f"write_{target_user_id}"}],
        [{"text": "🚩 Пожаловаться", "callback_data": f"report_{target_user_id}"}]
    ]}

def gender_keyboard():
    return {"inline_keyboard": [
        [{"text": "👦 Парень", "callback_data": "g_male"}, {"text": "👧 Девушка", "callback_data": "g_female"}],
        [{"text": "🌈 Другой", "callback_data": "g_other"}]
    ]}

def orientation_keyboard():
    return {"inline_keyboard": [
        [{"text": "Гетеро", "callback_data": "o_hetero"}, {"text": "Гомо", "callback_data": "o_homo"}],
        [{"text": "Би", "callback_data": "o_bi"}, {"text": "Другая", "callback_data": "o_other"}]
    ]}

def handle_message(conn, msg):
    user_id = msg["from"]["id"]
    username = msg["from"].get("username", "")
    text = msg.get("text", "")
    photo = msg.get("photo")

    ensure_user(conn, user_id, username)
    user = get_user(conn, user_id)
    is_banned, state = user[2], user[3]

    if is_banned:
        send(user_id, "🚫 Ваш аккаунт заблокирован за нарушение правил.")
        return

    # Активный чат — пересылаем сообщения
    active_chat = get_active_chat(conn, user_id)
    if active_chat and state == "in_chat" and text not in ["/stop", "🛑 Завершить чат"]:
        chat_id_db, user_a, user_b = active_chat
        partner_id = user_b if user_a == user_id else user_a
        ok = forward_message(msg, partner_id)
        if not ok:
            send(user_id, "⚠️ Сообщение содержит недопустимые слова и не было отправлено.")
        return

    # Команды
    if text == "/start":
        profile = get_profile(conn, user_id)
        if profile:
            send(user_id, f"👋 С возвращением в <b>AvaMatch</b>!\n\nТвоя анкета активна. Приятных знакомств! 🎮", reply_markup=main_menu())
        else:
            send(user_id, (
                "🎮 Добро пожаловать в <b>AvaMatch</b> — анонимные знакомства для игроков <b>Avakin Life</b>!\n\n"
                "Здесь ты можешь:\n"
                "• Создать анкету с ником из игры\n"
                "• Просматривать анкеты других игроков\n"
                "• Анонимно общаться в чате\n\n"
                "Давай создадим твою анкету! Как тебя зовут в Avakin Life?\n"
                "<i>(Введи свой игровой ник)</i>"
            ), reply_markup={"remove_keyboard": True})
            set_state(conn, user_id, "fill_name")

    elif text in ["📋 Моя анкета", "/profile"]:
        profile = get_profile(conn, user_id)
        if not profile:
            send(user_id, "У тебя пока нет анкеты. Используй /start чтобы создать её.")
            return
        nick, gender, orientation, age, photo_file_id, likes, dislikes = profile
        caption = profile_text(nick, gender, orientation, age, likes) + f"\n👎 Дизлайков: {dislikes}"
        edit_kb = {"inline_keyboard": [
            [{"text": "✏️ Изменить анкету", "callback_data": "edit_profile"}],
            [{"text": "❌ Удалить анкету", "callback_data": "delete_profile"}]
        ]}
        if photo_file_id:
            send_photo(user_id, photo_file_id, caption=caption, reply_markup=edit_kb)
        else:
            send(user_id, caption, reply_markup=edit_kb)

    elif text in ["🔍 Смотреть анкеты", "/browse"]:
        profile = get_profile(conn, user_id)
        if not profile:
            send(user_id, "Сначала создай анкету! Используй /start")
            return
        show_next_profile(conn, user_id)

    elif text in ["💬 Мой чат", "/chat"]:
        active_chat = get_active_chat(conn, user_id)
        if active_chat:
            partner_id = active_chat[2] if active_chat[1] == user_id else active_chat[1]
            p_profile = get_profile(conn, partner_id)
            nick = p_profile[0] if p_profile else "Аноним"
            send(user_id, f"💬 У тебя активный чат с <b>{nick}</b>.\nПиши сообщения — я передам их анонимно!\n\nЧтобы завершить чат — /stop", reply_markup={"keyboard": [[{"text": "🛑 Завершить чат"}]], "resize_keyboard": True})
            set_state(conn, user_id, "in_chat")
        else:
            send(user_id, "У тебя нет активного чата. Найди кого-то в разделе «Смотреть анкеты» и поставь лайк! 🔍", reply_markup=main_menu())

    elif text in ["/stop", "🛑 Завершить чат"]:
        active_chat = get_active_chat(conn, user_id)
        if active_chat:
            chat_id_db, user_a, user_b = active_chat
            partner_id = user_b if user_a == user_id else user_a
            end_chat(conn, chat_id_db)
            set_state(conn, user_id, "idle")
            set_state(conn, partner_id, "idle")
            send(user_id, "✅ Чат завершён. До новых знакомств! 🎮", reply_markup=main_menu())
            send(partner_id, "💔 Собеседник завершил чат. Ищи новых знакомых! 🔍", reply_markup=main_menu())
        else:
            send(user_id, "У тебя нет активного чата.", reply_markup=main_menu())
            set_state(conn, user_id, "idle")

    elif text in ["⭐ Отзывы", "/reviews"]:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT u.username, r.rating, r.comment, r.created_at
            FROM {SCHEMA}.reviews r
            JOIN {SCHEMA}.users u ON r.from_user_id = u.id
            JOIN {SCHEMA}.profiles p ON r.to_user_id = p.user_id
            WHERE r.to_user_id = %s
            ORDER BY r.created_at DESC LIMIT 5
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        if not rows:
            send(user_id, "⭐ У тебя пока нет отзывов. Общайся с людьми и они оставят отзывы!")
        else:
            text_out = "⭐ <b>Отзывы о тебе:</b>\n\n"
            for row in rows:
                stars = "⭐" * row[1]
                comment = row[2] or ""
                text_out += f"{stars}\n{comment}\n\n"
            send(user_id, text_out)

    elif text in ["ℹ️ Помощь", "/help"]:
        send(user_id, (
            "ℹ️ <b>AvaMatch — помощь</b>\n\n"
            "📋 <b>Моя анкета</b> — просмотр и редактирование\n"
            "🔍 <b>Смотреть анкеты</b> — листай и ставь лайки\n"
            "💬 <b>Мой чат</b> — анонимный чат при взаимном лайке\n"
            "⭐ <b>Отзывы</b> — отзывы о тебе\n\n"
            "🛡 Все сообщения проходят фильтрацию. При 3 жалобах — автоблокировка.\n"
            "📩 Поддержка: @AvaMatchSupport"
        ), reply_markup=main_menu())

    # FSM — создание анкеты
    elif state == "fill_name":
        if contains_mat(text):
            send(user_id, "⚠️ Ник содержит недопустимые слова. Введи другой:")
            return
        if not text or len(text) < 2 or len(text) > 30:
            send(user_id, "Ник должен быть от 2 до 30 символов. Попробуй ещё раз:")
            return
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {SCHEMA}.profiles (user_id, avakin_nick, gender, orientation, age)
            VALUES (%s, %s, 'male', 'hetero', 18)
            ON CONFLICT (user_id) DO UPDATE SET avakin_nick = EXCLUDED.avakin_nick, updated_at = NOW()
        """, (user_id, text))
        conn.commit()
        cur.close()
        set_state(conn, user_id, "fill_gender")
        send(user_id, f"✅ Ник <b>{text}</b> сохранён!\n\nТеперь выбери свой пол:", reply_markup=gender_keyboard())

    elif state == "fill_age":
        try:
            age = int(text.strip())
            if age < 13 or age > 99:
                raise ValueError
        except ValueError:
            send(user_id, "Введи возраст числом от 13 до 99:")
            return
        cur = conn.cursor()
        cur.execute(f"UPDATE {SCHEMA}.profiles SET age = %s, updated_at = NOW() WHERE user_id = %s", (age, user_id))
        conn.commit()
        cur.close()
        set_state(conn, user_id, "fill_photo")
        send(user_id, f"✅ Возраст {age} лет сохранён!\n\n📸 Отправь фото своего персонажа из Avakin Life (или нажми /skip чтобы пропустить):")

    elif state == "fill_photo":
        if text == "/skip":
            set_state(conn, user_id, "idle")
            send(user_id, "✅ <b>Анкета создана!</b> Удачи в знакомствах! 🎮", reply_markup=main_menu())
        elif photo:
            file_id = photo[-1]["file_id"]
            cur = conn.cursor()
            cur.execute(f"UPDATE {SCHEMA}.profiles SET photo_file_id = %s, updated_at = NOW() WHERE user_id = %s", (file_id, user_id))
            conn.commit()
            cur.close()
            set_state(conn, user_id, "idle")
            send(user_id, "✅ <b>Анкета полностью создана!</b> Теперь тебя видят другие игроки! 🎮", reply_markup=main_menu())
        else:
            send(user_id, "Отправь фото или нажми /skip:")

    elif state == "fill_review_rating":
        try:
            rating = int(text.strip())
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            send(user_id, "Введи оценку от 1 до 5:")
            return
        cur = conn.cursor()
        cur.execute(f"SELECT state FROM {SCHEMA}.users WHERE id = %s", (user_id,))
        # Сохраняем рейтинг в state как fill_review_comment_<rating>_<target_id>
        # target_id уже хранится в state как fill_review_rating_<target_id>
        cur.close()
        # Получаем target_id из метаданных — используем кастомную технику через state
        cur2 = conn.cursor()
        cur2.execute(f"SELECT state FROM {SCHEMA}.users WHERE id = %s", (user_id,))
        full_state = cur2.fetchone()[0]
        cur2.close()
        parts = full_state.split("_")
        target_id = int(parts[-1]) if parts[-1].isdigit() else None
        if not target_id:
            send(user_id, "Ошибка. Попробуй снова.", reply_markup=main_menu())
            set_state(conn, user_id, "idle")
            return
        set_state(conn, user_id, f"fill_review_comment_{rating}_{target_id}")
        send(user_id, f"Оценка {rating}⭐ принята!\nНапиши комментарий (или /skip):")

    elif "fill_review_comment_" in state:
        parts = state.split("_")
        rating = int(parts[3])
        target_id = int(parts[4])
        comment = text if text != "/skip" else None
        if comment and contains_mat(comment):
            send(user_id, "⚠️ Комментарий содержит недопустимые слова. Попробуй снова или /skip:")
            return
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {SCHEMA}.reviews (from_user_id, to_user_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (from_user_id, to_user_id) DO UPDATE SET rating = EXCLUDED.rating, comment = EXCLUDED.comment
        """, (user_id, target_id, rating, comment))
        conn.commit()
        cur.close()
        set_state(conn, user_id, "idle")
        send(user_id, "✅ Отзыв сохранён! Спасибо! ⭐", reply_markup=main_menu())

def show_next_profile(conn, user_id):
    profile = get_next_profile(conn, user_id)
    if not profile:
        send(user_id, "😔 Анкеты закончились! Загляни позже — появятся новые игроки. 🎮", reply_markup=main_menu())
        return
    target_id, nick, gender, orientation, age, photo_file_id, likes = profile
    mark_viewed(conn, user_id, target_id)
    caption = profile_text(nick, gender, orientation, age, likes)
    kb = browse_keyboard(target_id)
    if photo_file_id:
        send_photo(user_id, photo_file_id, caption=caption, reply_markup=kb)
    else:
        send(user_id, caption, reply_markup=kb)

def handle_callback(conn, cb):
    user_id = cb["from"]["id"]
    username = cb["from"].get("username", "")
    data = cb["data"]
    msg_id = cb["message"]["message_id"]
    chat_id = cb["message"]["chat"]["id"]

    ensure_user(conn, user_id, username)
    user = get_user(conn, user_id)
    if user[2]:
        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"], "text": "🚫 Вы заблокированы."}, timeout=5)
        return

    requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": cb["id"]}, timeout=5)

    # Выбор пола
    if data.startswith("g_"):
        gender = data[2:]
        cur = conn.cursor()
        cur.execute(f"UPDATE {SCHEMA}.profiles SET gender = %s, updated_at = NOW() WHERE user_id = %s", (gender, user_id))
        conn.commit()
        cur.close()
        set_state(conn, user_id, "fill_orientation")
        requests.post(f"{API}/editMessageReplyMarkup", json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": json.dumps({})}, timeout=5)
        send(user_id, "✅ Пол сохранён!\n\nВыбери ориентацию:", reply_markup=orientation_keyboard())

    # Выбор ориентации
    elif data.startswith("o_"):
        orientation = data[2:]
        cur = conn.cursor()
        cur.execute(f"UPDATE {SCHEMA}.profiles SET orientation = %s, updated_at = NOW() WHERE user_id = %s", (orientation, user_id))
        conn.commit()
        cur.close()
        set_state(conn, user_id, "fill_age")
        requests.post(f"{API}/editMessageReplyMarkup", json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": json.dumps({})}, timeout=5)
        send(user_id, "✅ Ориентация сохранена!\n\nСколько тебе лет? (введи число):")

    # Лайк
    elif data.startswith("like_"):
        target_id = int(data[5:])
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {SCHEMA}.likes (from_user_id, to_user_id, is_like)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (from_user_id, to_user_id) DO UPDATE SET is_like = TRUE
        """, (user_id, target_id))
        cur.execute(f"UPDATE {SCHEMA}.profiles SET likes = likes + 1 WHERE user_id = %s", (target_id,))
        conn.commit()
        cur.close()

        is_match = check_match(conn, user_id, target_id)
        if is_match:
            p_profile = get_profile(conn, target_id)
            my_profile = get_profile(conn, user_id)
            p_nick = p_profile[0] if p_profile else "Аноним"
            my_nick = my_profile[0] if my_profile else "Аноним"
            start_chat(conn, user_id, target_id)
            set_state(conn, user_id, "in_chat")
            set_state(conn, target_id, "in_chat")
            send(user_id, f"🎉 <b>Взаимный лайк!</b>\nТы совпал с <b>{p_nick}</b>!\n\nЧат открыт — пиши сюда, я передам анонимно! 💬\n/stop — завершить чат", reply_markup={"keyboard": [[{"text": "🛑 Завершить чат"}]], "resize_keyboard": True})
            send(target_id, f"🎉 <b>Взаимный лайк!</b>\n<b>{my_nick}</b> тоже лайкнул тебя!\n\nЧат открыт — пиши сюда, я передам анонимно! 💬\n/stop — завершить чат", reply_markup={"keyboard": [[{"text": "🛑 Завершить чат"}]], "resize_keyboard": True})
        else:
            requests.post(f"{API}/editMessageReplyMarkup", json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": json.dumps({})}, timeout=5)
            send(user_id, "❤️ Лайк отправлен! Если будет взаимно — появится чат. Листай дальше! 👇")
            show_next_profile(conn, user_id)

    # Дизлайк
    elif data.startswith("dislike_"):
        target_id = int(data[8:])
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {SCHEMA}.likes (from_user_id, to_user_id, is_like)
            VALUES (%s, %s, FALSE)
            ON CONFLICT (from_user_id, to_user_id) DO UPDATE SET is_like = FALSE
        """, (user_id, target_id))
        cur.execute(f"UPDATE {SCHEMA}.profiles SET dislikes = dislikes + 1 WHERE user_id = %s", (target_id,))
        conn.commit()
        cur.close()
        requests.post(f"{API}/editMessageReplyMarkup", json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": json.dumps({})}, timeout=5)
        show_next_profile(conn, user_id)

    # Написать (открыть чат)
    elif data.startswith("write_"):
        target_id = int(data[6:])
        active_chat = get_active_chat(conn, user_id)
        if active_chat:
            send(user_id, "У тебя уже есть активный чат! Сначала заверши его: /stop")
            return
        # Ставим лайк автоматически
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {SCHEMA}.likes (from_user_id, to_user_id, is_like)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (from_user_id, to_user_id) DO UPDATE SET is_like = TRUE
        """, (user_id, target_id))
        conn.commit()
        cur.close()
        is_match = check_match(conn, user_id, target_id)
        if is_match:
            p_profile = get_profile(conn, target_id)
            p_nick = p_profile[0] if p_profile else "Аноним"
            start_chat(conn, user_id, target_id)
            set_state(conn, user_id, "in_chat")
            set_state(conn, target_id, "in_chat")
            send(user_id, f"💬 Чат с <b>{p_nick}</b> открыт! Пиши сообщения — передам анонимно.\n/stop — завершить", reply_markup={"keyboard": [[{"text": "🛑 Завершить чат"}]], "resize_keyboard": True})
            send(target_id, f"💬 Кто-то хочет с тобой пообщаться! Чат открыт!\n/stop — завершить", reply_markup={"keyboard": [[{"text": "🛑 Завершить чат"}]], "resize_keyboard": True})
        else:
            send(user_id, "❤️ Лайк поставлен! Когда человек лайкнет тебя в ответ — чат откроется автоматически.")

    # Жалоба — шаг 1
    elif data.startswith("report_"):
        target_id = int(data[7:])
        kb = {"inline_keyboard": [
            [{"text": "🔞 Неприемлемый контент", "callback_data": f"report_reason_{target_id}_18"}],
            [{"text": "💢 Оскорбления/хамство", "callback_data": f"report_reason_{target_id}_abuse"}],
            [{"text": "🤖 Спам/реклама", "callback_data": f"report_reason_{target_id}_spam"}],
            [{"text": "❌ Другое", "callback_data": f"report_reason_{target_id}_other"}],
        ]}
        send(user_id, "🚩 Выбери причину жалобы:", reply_markup=kb)

    # Жалоба — шаг 2 (причина выбрана)
    elif data.startswith("report_reason_"):
        parts = data.split("_")
        target_id = int(parts[2])
        reason_code = parts[3]
        reason_map = {"18": "Неприемлемый контент", "abuse": "Оскорбления/хамство", "spam": "Спам/реклама", "other": "Другое"}
        reason = reason_map.get(reason_code, "Другое")
        count = add_complaint(conn, user_id, target_id, reason)
        msg_text = f"✅ Жалоба принята! Причина: {reason}."
        if count >= 3:
            msg_text += "\n🚫 Пользователь заблокирован автоматически."
        send(user_id, msg_text, reply_markup=main_menu())

    # Редактировать анкету
    elif data == "edit_profile":
        set_state(conn, user_id, "fill_name")
        send(user_id, "✏️ Введи новый ник из Avakin Life:")

    # Удалить анкету
    elif data == "delete_profile":
        cur = conn.cursor()
        cur.execute(f"UPDATE {SCHEMA}.profiles SET is_active = FALSE WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        send(user_id, "❌ Анкета скрыта. Ты можешь создать новую через /start", reply_markup=main_menu())

    # Оставить отзыв
    elif data.startswith("review_"):
        target_id = int(data[7:])
        set_state(conn, user_id, f"fill_review_rating_{target_id}")
        send(user_id, "⭐ Оцени пользователя от 1 до 5:")


def handler(event: dict, context) -> dict:
    """Главный webhook-обработчик Telegram-бота AvaMatch."""
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": ""
        }

    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return {"statusCode": 200, "headers": {"Access-Control-Allow-Origin": "*"}, "body": "ok"}

    conn = get_conn()
    try:
        if "message" in body:
            handle_message(conn, body["message"])
        elif "callback_query" in body:
            handle_callback(conn, body["callback_query"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "ok"
    }
