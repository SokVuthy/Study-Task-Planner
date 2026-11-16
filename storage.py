import json
import os
import shutil
from model import Task, TaskManager

FILENAME = "task_data.json"

def load_data():
    manager= TaskManager()

    if not os.path.exists(FILENAME):
        print("File not found. Starting Fresh")
        return manager

    try:
        with open(FILENAME,'r') as file:
            data= json.load(file)

            for task_dict in data:
                task= Task(
                    task_id=task_dict["task_id"],
                    title=task_dict["title"],
                    subject=task_dict["subject"],
                    due_date=task_dict["due_date"],
                    status= task_dict.get("status", "pending")
                )

                manager.add_task(task)
    except json.JSONDecodeError:
        print("\n Error: The data file is damaged or currupted.")

        backup_name = FILENAME + ".backup"
        shutil.copy(FILENAME, backup_name)

        print(f"A backup has been save as {backup_name}.")
        print("Starting with an empty task list to prevent further issues.\n")

    return manager

def save_data(manager):
    data_to_save = [task.to_dict() for task in manager.task.values()]

    try:
        with open(FILENAME, 'w') as file:
            json.dump(data_to_save, file, indent= 4)

    except Exception as e:
        print("Error saving data: {e} ")
        