# theory_repository.py
import json
import os
from app.core.config import THEORY_DIR
from app.core.logger import get_logger

logger = get_logger(__name__)


class TheoryLoader:
    _cache_general = None
    _cache_tasks = {}

    @classmethod
    def load_general(cls):
        if cls._cache_general is not None:
            return cls._cache_general
        filepath = os.path.join(THEORY_DIR, "general.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                cls._cache_general = json.load(f)
            logger.info("Общая теория загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки общей теории: {e}")
            cls._cache_general = {"sections": []}
        return cls._cache_general

    @classmethod
    def load_task_theory(cls, task_number):
        # Для заданий 19, 20, 21 используется общий файл task_19_21.json
        if task_number in (19, 20, 21):
            cache_key = "19_21"
            if cache_key in cls._cache_tasks:
                return cls._cache_tasks[cache_key]
            filepath = os.path.join(THEORY_DIR, "task_19_21.json")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    theory = json.load(f)
                cls._cache_tasks[cache_key] = theory
                logger.info("Теория для заданий 19-21 загружена")
                return theory
            except Exception as e:
                logger.warning(f"Теория для заданий 19-21 не найдена: {e}")
                cls._cache_tasks[cache_key] = {
                    "content": "Теория для этих заданий пока не добавлена."
                }
                return cls._cache_tasks[cache_key]

        # Для остальных заданий загружаем отдельные файлы
        if task_number in cls._cache_tasks:
            return cls._cache_tasks[task_number]
        filepath = os.path.join(THEORY_DIR, f"task_{task_number:02d}.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                theory = json.load(f)
            cls._cache_tasks[task_number] = theory
            logger.info(f"Теория для задания {task_number} загружена")
            return theory
        except Exception as e:
            logger.warning(f"Теория для задания {task_number} не найдена: {e}")
            cls._cache_tasks[task_number] = {
                "content": "Теория для этого задания пока не добавлена."
            }
            return cls._cache_tasks[task_number]
