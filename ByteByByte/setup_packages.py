# setup_packages.py
import os

# Список всех папок, которые должны быть пакетами
dirs = [
    "app",
    "app/core",
    "app/services",
    "app/repositories",
    "app/utils",
    "app/ui",
    "app/ui/widgets",
    "app/ui/screens",
    "app/ui/screens/auth",
    "app/ui/screens/dashboard",
    "app/ui/screens/training",
    "app/ui/screens/exam",
    "app/ui/screens/quest",
    "app/ui/screens/teacher",
    "app/ui/screens/student",
    "app/ui/screens/profile",
    "app/ui/screens/admin",
    "app/ui/screens/guilds",
    "app/ui/screens/houses",
    "app/ui/themes",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)          # создаём папку, если её нет
    init_path = os.path.join(d, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("# init\n")            # пустой файл с комментарием
        print(f"  [+] {init_path}")
    else:
        print(f"  [=] {init_path} уже существует")

print("\nГотово! Теперь запускай main.py")
