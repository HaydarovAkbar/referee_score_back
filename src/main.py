import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Списки пользователей
premium_users = set()
standard_users = set()
admins = {758934089}


# Функция для добавления премиум-пользователя
def add_premium_user(update: Update, context: CallbackContext) -> None:
    user_id = int(context.args[0])
    premium_users.add(user_id)
    update.message.reply_text("Пользователь добавлен в премиум группу!", reply_to_message_id=update.message.message_id)


# Функция для добавления стандартного пользователя
def add_standard_user(update: Update, context: CallbackContext) -> None:
    user_id = int(context.args[0])
    standard_users.add(user_id)
    update.message.reply_text("Пользователь добавлен в стандартную группу!",
                              reply_to_message_id=update.message.message_id)


def publish_content_type(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Пожалуйста, укажите тип контента (premium/standard) и сообщение.\n\nПример: /publish premium")
        return

    content_type = context.args[0].lower()

    if content_type == 'premium':
        context.chat_data['content_type'] = 'premium'
    elif content_type == 'standard':
        context.chat_data['content_type'] = 'standard'
    else:
        update.message.reply_text("Неверный тип контента. Используйте 'premium' или 'standard'.")
    update.message.reply_text("Теперь введите сообщение для публикации.")


# Функция для публикации контента
def publish_content(update: Update, context: CallbackContext) -> None:
    content_type = context.chat_data.get('content_type', None)
    if not content_type:
        update.message.reply_text("Сначала укажите тип контента (premium/standard).")
        return publish_content_type(update, context)
    if content_type == 'premium':
        for user_id in premium_users:
            context.bot.send_message(chat_id=user_id, text=f"Премиум контент: {content_message}")
    elif content_type == 'standard':
        for user_id in standard_users:
            context.bot.send_message(chat_id=user_id, text=f"Стандартный контент: {content_message}")
    else:
        update.message.reply_text("Неверный тип контента. Используйте 'premium' или 'standard'.")


# Функция для публикации списка пользователей
def publish_users(update: Update, context: CallbackContext):
    if update.message.from_user.id not in admins:
        return

    all_users = "foydalanuvchilar:\n\n"
    for user_id in premium_users | standard_users:
        user_is_premium = user_id in premium_users
        all_users += f"{user_id}\nПремиум user: {user_is_premium}\n"

    context.bot.send_message(chat_id=update.message.chat_id, text=all_users)


# Функция для уведомления администраторов о новом пользователе
def notify_admins(update: Update, context: CallbackContext):
    new_members = update.message.new_chat_members
    for new_member in new_members:
        for admin_id in admins:
            context.bot.send_message(
                chat_id=admin_id,
                text=f"Новый пользователь: {new_member.id} ({new_member.username}). Введите команду: \n\n/addpremium {new_member.id} \n/addstandard {new_member.id} \n\nдля добавления в соответствующую группу."
            )


# Основная функция
def main() -> None:
    # Создание Updater и передача токена вашего бота
    updater = Updater("7310956380:AAE17v-TyMTz3YRfV2L2SKdYOc1kXly3Fu8")

    # Получение диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация команд
    dispatcher.add_handler(CommandHandler("addpremium", add_premium_user, Filters.user(user_id=admins)))
    dispatcher.add_handler(CommandHandler("addstandard", add_standard_user, Filters.user(user_id=admins)))
    dispatcher.add_handler(CommandHandler("users", publish_users))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, notify_admins))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(r'^/publish'), publish_content_type))
    dispatcher.add_handler(MessageHandler(Filters.text, publish_content))

    # Запуск бота
    updater.start_polling()

    # Ожидание остановки
    updater.idle()


if __name__ == '__main__':
    main()
