import json
import os
import shutil
from model import Task, TaskManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(BASE_DIR, "task_data.json")
BACKUP_FILENAME = FILENAME + ".backup"


# =====================BACKUP================

def backup_data_file():
    try:
        shutil.copy(FILENAME, BACKUP_FILENAME)
        print(f"A backup has been saved as {BACKUP_FILENAME}.")
    except OSError as e:
        print(f"Could not create a backup: {e}")

# ==========================LOAD=========================

def load_data():
    manager = TaskManager()

    if not os.path.exists(FILENAME):
        print("File not found. Starting fresh.")
        return manager

    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        for task_dict in data:
            task = Task(
                task_id=task_dict["task_id"],
                title=task_dict["title"],
                subject=task_dict["subject"],
                due_date=task_dict["due_date"],
                status=task_dict.get("status", "pending"),
            )
            manager.add_task(task)

    except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError, AttributeError):
        print("\nError: The data file is damaged or corrupted.")
        backup_data_file()
        print("Starting with an empty task list to prevent further issues.\n")
        return TaskManager()

    manager.renumber_tasks()
    return manager

# =======================SAVE=========================

def save_data(manager):
    data_to_save = [task.to_dict() for task in manager.get_sorted_tasks()]
    temp_filename = FILENAME + ".tmp"

    try:
        with open(temp_filename, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4)
        os.replace(temp_filename, FILENAME)
        return True

    except (OSError, TypeError) as e:
        print(f"Error saving data: {e}")
        return False