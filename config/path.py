from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TMP_DIR = BASE_DIR / 'tmp' # 临时数据目录
LOGS_DIR = TMP_DIR / 'logs' # 日志目录
