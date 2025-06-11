import configparser

config = configparser.ConfigParser()
config.read('./conf.txt')

RAY_PEN_WIDTH = config.getint('DEFAULT', 'RAY_PEN_WIDTH', fallback=5)
RAY_MAX_LENGTH = config.getint('DEFAULT', 'RAY_MAX_LENGTH', fallback=500)

MAX_REFRACTIONS = config.getint('DEFAULT', 'MAX_REFRACTIONS', fallback=10)
ROUNDING_PRECISION = config.getint('DEFAULT', 'ROUNDING_PRECISION', fallback=2)

LEN_NORMAL_POINTS_DISTANCE = config.getfloat('DEFAULT', 'LEN_NORMAL_POINTS_DISTANCE', fallback=0.5)

REFRESH_LASER_TIMEOUT = config.getint('DEFAULT', 'REFRESH_LASER_TIMEOUT', fallback=2000)
REFRESH_OBJ_TIMEOUT = config.getint('DEFAULT', 'REFRESH_OBJ_TIMEOUT', fallback=2000)

IS_REFLECTION = config.getboolean('DEFAULT', 'IS_REFLECTION', fallback=True)
IS_REFRACTION = config.getboolean('DEFAULT', 'IS_REFRACTION', fallback=True)

LEN_COUNT = config.getint('DEFAULT', 'LEN_COUNT', fallback=0)
MIRROR_COUNT = config.getint('DEFAULT', 'MIRROR_COUNT', fallback=1)
LASER_COUNT = config.getint('DEFAULT', 'LASER_COUNT', fallback=1)
