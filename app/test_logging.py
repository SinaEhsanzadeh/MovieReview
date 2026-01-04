import logging

logger = logging.getLogger("movie_rating")

logger.debug("This is a DEBUG message - should not appear (level is INFO)")
logger.info("This is an INFO message - should appear")
logger.warning("This is a WARNING message - should appear")
logger.error("This is an ERROR message - should appear")
logger.critical("This is a CRITICAL message - should appear")

print("Check console for logs. Also check 'movie_rating.log' file in project root.")