# task_repository.py
import json
import os
import glob
from app.core.config import TASKS_DIR
from app.core.logger import get_logger

logger = get_logger(__name__)

class TaskLoader:
    _cache = None

    @classmethod
    def load_all(cls):
        if cls._cache is not None:
            return cls._cache

        pattern = os.path.join(TASKS_DIR, "task_*.json")
        all_data = {}
        for filepath in glob.glob(pattern):
            try:
                basename = os.path.basename(filepath)
                task_num_str = basename.replace("task_", "").replace(".json", "")
                with open(filepath, "r", encoding="utf-8") as f:
                    task_data = json.load(f)

                # Обработка единого файла task_19_21.json
                if task_num_str == "19_21":
                    for num in ("19", "20", "21"):
                        flat_subtypes = {}
                        for subtype, subtype_content in task_data["subtypes"].items():
                            if "blocks" in subtype_content:
                                tasks_for_num = []
                                for block in subtype_content["blocks"]:
                                    if num in block:
                                        tasks_for_num.append(block[num])
                                flat_subtypes[subtype] = tasks_for_num
                        all_data[num] = {"subtypes": flat_subtypes}
                else:
                    task_key = str(int(task_num_str))
                    all_data[task_key] = task_data
                logger.info(f"Загружены задачи для задания {task_num_str} из {basename}")
            except Exception as e:
                logger.error(f"Ошибка загрузки {basename}: {e}")

        cls._cache = all_data
        return cls._cache

    @classmethod
    def get_tasks(cls, task_number, subtype_name):
        data = cls.load_all()
        task_key = str(task_number)
        
        if (task_key in data and 
            "subtypes" in data[task_key] and 
            subtype_name in data[task_key]["subtypes"]):
            tasks = data[task_key]["subtypes"][subtype_name]
            return tasks
        # Заглушка, если не найдено
        logger.warning(f"Задачи не найдены для {task_number} / {subtype_name}")
        return [
            {
                "question": f"Задача-заглушка для задания {task_number}, подтипа '{subtype_name}'\n\nЭто демонстрационная задача. Введите ответ 0.",
                "answer": "0",
                "hint": "Подсказка: правильный ответ — 0."
            }
            for _ in range(5)
        ]
