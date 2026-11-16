import storage
from model import Task

def print_menu(): 
    print("\n--- STUDY TASK PLANNER ---")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Search")
    print("4. Update Task Status")
    print("5. Delete Task")
    print("6. Show Summary")
    print("7. Exit")    

def get_valid_input(prompt):

    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Error: Please fill out this field!!")
            continue
        return user_input

def main():

    manager = storage.load_data()

    next_id = 1

    if manager.task:

        existing_id = [int(tid.replace("T", "")) for tid in manager.task.keys()]
        next_id = max(existing_id) + 1

    while True:
        print_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":

            print("\n ADD TASK")
            title = get_valid_input("Enter Task Title: ")
            subject = get_valid_input("Enter Subject: ")
            due_date = get_valid_input("Enter Due Date (YYYY-MM-DD): ")
            
            task_id = f"T{next_id:03d}"
            next_id += 1
            
            new_task = Task(task_id, title, subject, due_date)
            manager.add_task(new_task)
            storage.save_data(manager)
            
            print(f"Success! Task {task_id} added and saved.")

        elif choice == "2":

            print("\n Task List ")

            if not manager.task:
                print("Empty List")

            else: 
                for t in manager.task.values(): # Singular
                    print(f"[{t.task_id}] {t.title} | Subject: {t.subject} | Due: {t.due_date} | Status: {t.status}")
        
        elif choice == "3":

            print("\n-- Search / Filter --")
            print("1. Search by Subject")
            print("2. Filter by Status")
            
            sub_choice = input("Choice: ").strip()

            if sub_choice =="1":

                sub_search = input("Enter the subject to search: ").strip().lower()
                found = False

                for t in manager.task.values():

                    if t.subject.lower() == sub_search:

                        print(f"[{t.task_id}] {t.title} | Due: {t.due_date} | Status: {t.status}")
                        found = True

                if not found: 
                    print(f"No task found for {sub_search}")

            elif sub_choice =="2":
 
                search_status = input("Enter the status to filter (completed/pending): ").strip().lower()
                found = False
 
                for t in manager.task.values():
                    
                    if t.status.lower() == search_status:
                        print(f"[{t.task_id}] {t.title} | Subject: {t.subject} | Due: {t.due_date}")
                        found = True
    
                if not found:
                         print(f"No task with status: {search_status}")

        elif choice == "4":
    
            print("\n Update Task ")
            task_id = input("Enter task ID to update: ").strip().upper()
            task = manager.get_task(task_id)
            
            if task:
                print(f"Current Status: {task.status}")
                new_status = input("Enter new status (completed/pending): ").strip().lower()
    
                if new_status in ["pending", "completed"]:
                    task.status = new_status
                    storage.save_data(manager)
                    print("Task status changed successfully.")
    
                else: 
                    print("Incorrect Input, please try again. (input must be 'completed' or 'pending') !!")
    
            else: 
                print("Error: Task ID not found!!!")

        elif choice == "5":
  
            print("\n Delete Task by ID ")
            task_id = input("Enter task ID to delete: ").strip().upper()
            task = manager.get_task(task_id)
            
            if task: 
        
                confirm = input(f"Are you sure you want to delete {task.title}? (y/n): ").strip().lower()
       
                if confirm == "y":
       
                    manager.delete_task(task_id)
                    storage.save_data(manager)
                    print(f"Task {task.title} has been deleted.")
       
                elif confirm == "n":
                    print("Deletion Cancelled.")

                else: 
                    print("Error: wrong input please try again. (input must be y=Y & n=N)")

            else:
                print("Task not found!!")

        elif choice == "6": 

            summary = manager.get_summary()

            print("\n Show Summary")
            print(f"Total Tasks: {summary['total']}")
            print(f"Completed/Done: {summary['completed']}")
            print(f"Pending: {summary['pending']}")
            print(f"Overdue: {summary['overdue']}")

        elif choice == "7": 
            print("Exiting program!!!")
            break

        else: 
            print("Invalid Input!! Input must be from 1-7")

if __name__ == "__main__":
    main()