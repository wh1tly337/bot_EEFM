from loguru import logger


def print_log_info(message, start_message):
    """ Функция для составления сообщения логгера """
    start_message += ' |'
    output = [
        start_message,
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    ]
    logger.info(' '.join(str(_) for _ in output))
