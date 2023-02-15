from loguru import logger
# Связть между markup и hendler-ми

def print_log_info(message, start_message):
    start_message += ' |'
    output = [
        start_message,
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
    ]
    logger.info(' '.join(str(_) for _ in output))
