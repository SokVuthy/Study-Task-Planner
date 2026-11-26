import storage
from model import STATUS_COMPLETED, STATUS_PENDING, parse_date



# =============MENU===========

def print_menu():
    print("\n--- STUDY TASK PLANNER ---")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Search")
    print("4. Update Task Status")
    print("5. Delete Task")
    print("6. Show Summary")
    print("7. Exit")


# ======================INPUT / OUTPUT HELPERS================

def get_valid_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Error: Please fill out this field!!")
            continue
        return user_input

def get_valid_date(prompt):
    while True:
        date = parse_date(get_valid_input(prompt))
        if date:
            return date
        print("Error: Date must be in YYYY-MM-DD format (e.g. 2026-11-30)!!")


def print_task(task):
    print(
        f"[{task.task_id}] {task.title} | Subject: {task.subject} "
        f"| Due: {task.due_date} | Status: {task.status}"
    )


def print_tasks(tasks, empty_message):
    if not tasks:
        print(empty_message)
        return

    for task in tasks:
        print_task(task)


# ==============1. ADD TASK=================

def menu_add_task(manager):
    print("\n ADD TASK")
    title = get_valid_input("Enter Task Title: ")
    subject = get_valid_input("Enter Subject: ")
    due_date = get_valid_date("Enter Due Date (YYYY-MM-DD): ")

    task = manager.create_task(title, subject, due_date)

    if storage.save_data(manager):
        print(f"Success! Task {task.task_id} added and saved.")
    else:
        print(f"Task {task.task_id} was added but could not be saved.")


# =========================2. VIEW ALL TASKS=============

def menu_view_tasks(manager):
    print("\n Task List ")
    print_tasks(manager.get_sorted_tasks(), "Empty List")



# ==================3. SEARCH / FILTER==================

def menu_search(manager):
    while True:
        print("\n-- Search / Filter --")
        print("1. Search by Subject")
        print("2. Filter by Status")
        print("3. Back to Main Menu")

        sub_choice = input("Choice: ").strip()

        if sub_choice == "1":
            subject = input("Enter the subject to search: ").strip()
            print_tasks(manager.search_by_subject(subject), f"No task found for {subject}")
            
        elif sub_choice == "2":
            status = input("Enter the status to filter (completed/pending): ").strip().lower()
            if status not in (STATUS_PENDING, STATUS_COMPLETED):
                print("Error: Status must be 'completed' or 'pending'!!")
            else:
                print_tasks(manager.filter_tasks(status=status), f"No task with status: {status}")
                
        elif sub_choice == "3":
            break 
        else:
            print("Error: Incorrect Input (Input Must be 1, 2, or 3)!!")


# ===============4. UPDATE TASK STATUS===============

def menu_update_status(manager):
    print("\n Update Task ")
    task_id = input("Enter task ID to update: ").strip().upper()
    task = manager.get_task(task_id)

    if not task:
        print("Error: Task ID not found!!!")
        return

    print(f"Current Status: {task.status}")
    new_status = input("Enter new status (completed/pending): ").strip().lower()

    if new_status not in (STATUS_PENDING, STATUS_COMPLETED):
        print("Incorrect Input, please try again. (input must be 'completed' or 'pending') !!")
        return

    task.status = new_status
    storage.save_data(manager)
    print("Task status changed successfully.")


# ====================5. DELETE TASK===============

def menu_delete_task(manager):
    print("\n Delete Task by ID ")
    task_id = input("Enter task ID to delete: ").strip().upper()
    task = manager.get_task(task_id)

    if not task:
        print("Task not found!!")
        return

    confirm = input(f"Are you sure you want to delete {task.title}? (y/n): ").strip().lower()

    if confirm == "y":
        manager.delete_task(task_id)
        storage.save_data(manager)
        print(f"Task {task.title} has been deleted. Remaining task IDs were renumbered.")
    elif confirm == "n":
        print("Deletion Cancelled.")
    else:
        print("Error: wrong input please try again. (input must be y=Y & n=N)")


# ===================6. SHOW SUMMARY=================

def menu_summary(manager):
    summary = manager.get_summary()

    print("\n Show Summary")
    print(f"Total Tasks: {summary['total']}")
    print(f"Completed/Done: {summary['completed']}")
    print(f"Pending: {summary['pending']}")
    print(f"Overdue: {summary['overdue']}")


# =========================MAIN LOOP================

def main():
    manager = storage.load_data()

    while True:
        print_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            menu_add_task(manager)
            input("\nPress Enter to return to the main menu...")
        elif choice == "2":
            menu_view_tasks(manager)
            input("\nPress Enter to return to the main menu...")
        elif choice == "3":
            # Option 3 handles its own loop internally, so no pause needed here.
            menu_search(manager) 
        elif choice == "4":
            menu_update_status(manager)
            input("\nPress Enter to return to the main menu...")
        elif choice == "5":
            menu_delete_task(manager)
            input("\nPress Enter to return to the main menu...")
        elif choice == "6":
            menu_summary(manager)
            input("\nPress Enter to return to the main menu...")
        elif choice == "7":
            print("Exiting program!!!")
            break
        else:
            print("Invalid Input!! Input must be from 1-7")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting program!!!")