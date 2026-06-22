"""Constants for BiteRisk."""

DOMAIN = "biterisk"

# --- Update / persistence ---
UPDATE_INTERVAL_MINUTES = 5
STORAGE_KEY_BROOD = "biterisk_brood"
STORAGE_VERSION = 1

# --- Config keys ---
CONF_TEMP_SENSOR = "temp_sensor"
CONF_HUMIDITY_SENSOR = "humidity_sensor"
CONF_WIND_SENSOR = "wind_sensor"
CONF_RAIN_SENSOR = "rain_sensor"
CONF_FLOOR = "floor"
CONF_SUN_ENTITY = "sun_entity"

# --- Floor modifiers ---
FLOOR_GROUND = "ground"
FLOOR_FIRST = "first"
FLOOR_SECOND_PLUS = "second_plus"
FLOOR_MODIFIERS = {
    FLOOR_GROUND: 1.0,
    FLOOR_FIRST: 0.8,
    FLOOR_SECOND_PLUS: 0.6,
}
DEFAULT_FLOOR = FLOOR_GROUND
DEFAULT_SUN_ENTITY = "sun.sun"

# --- Factor weights (sum = 1.0) ---
WEIGHT_BROOD = 0.30
WEIGHT_TEMP = 0.25
WEIGHT_TIME = 0.20
WEIGHT_HUMIDITY = 0.15
WEIGHT_WIND = 0.10

# --- Temperature curve (deg C) ---
TEMP_MIN_ACTIVE = 10.0
TEMP_OPT_LOW = 20.0
TEMP_OPT_HIGH = 25.0
TEMP_MAX_ACTIVE = 35.0

# --- Humidity curve (%) ---
HUMIDITY_MIN = 50.0
HUMIDITY_FULL = 80.0

# --- Wind curve (m/s) ---
WIND_FULL_BELOW = 0.5
WIND_ZERO_AT = 3.0

# --- Time-of-day curve ---
TIME_DAY_BASE = 0.2
TIME_NIGHT_BASE = 0.5
TIME_PEAK = 1.0
DUSK_PRE_MIN = 30  # minutes before sunset peak starts
DUSK_POST_MIN = 180  # minutes after sunset peak ends

# --- Brood model ---
BROOD_SLOTS = 504  # 21 days x 24 h
BROOD_HOURS = 504
LAG_PEAK_START_H = 168  # 7 days
LAG_PEAK_END_H = 336  # 14 days
HEAVY_RAIN_CAP_MM = 8.0  # per-hour cap (wash-out effect)
BROOD_SATURATION_MM = 60.0  # weighted-sum value mapped to score 1.0
BROOD_NEUTRAL_FILL_MM = 0.5  # neutral per-hour value for cold-start gaps

# --- Label thresholds (on 0-100 modified score) ---
LABEL_LOW_MAX = 33
LABEL_MED_MAX = 66
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
