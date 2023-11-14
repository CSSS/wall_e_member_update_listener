from setup_logger import Loggers

log_info = Loggers.get_logger(logger_name="member_update_listener")
member_update_listener_log = log_info[0]

discordpy_logger_name = "discord.py"
discordpy_log_info = Loggers.get_logger(logger_name=discordpy_logger_name)
discordpy_logger = discordpy_log_info[0]