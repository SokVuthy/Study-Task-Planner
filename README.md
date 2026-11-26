# Study Task Planner

A small task planner for keeping track of study work. It has two interfaces that share the same code and the same data file: a command-line menu and a Streamlit web app.

## Features

- Add tasks with a title, subject and due date
- View, search and filter tasks (by subject, status or free text)
- Mark tasks as pending or completed
- Delete tasks with a confirmation step
- Task IDs stay in order (T001, T002, ...) and are renumbered after a delete, so there are no gaps
- Summary of total, completed, pending and overdue tasks
- Web app extras: progress bar, "Up Next" list, overdue highlighting, and swipe-left-to-delete on task cards

## Project structure

```
.
├── app.py            Streamlit web app (pages only)
├── main.py           Command-line interface (menus only)
├── model.py          Task and TaskManager: IDs, sorting, filtering, summary
├── storage.py        Loading and saving task_data.json
├── style.css         Web app styling
├── animations.js     Web app animations (count-up, progress bar, swipe to delete)
├── task_data.json    Saved tasks (created on first save)
├── icon.png          Optional page icon for the web app
└── .streamlit/
    └── config.toml   Optional light theme settings
```

All task logic lives in `model.py`, so the CLI and the web app behave the same way. `storage.py` only reads and writes the JSON file.

## Requirements

- Python 3.8 or newer
- Streamlit 1.39 or newer (web app only; the CLI needs nothing beyond the standard library)

```
pip install streamlit
```

## Running

Command line:

```
python main.py
```

Web app:

```
streamlit run app.py
```

Run both commands from the folder that contains the files. Data is stored in `task_data.json` next to the scripts, whichever folder you launch from.

## Using the CLI

| Option | Action |
|---|---|
| 1 | Add a task (due date must be `YYYY-MM-DD`) |
| 2 | View all tasks, sorted by ID |
| 3 | Search by subject or filter by status |
| 4 | Change a task's status |
| 5 | Delete a task (asks for confirmation) |
| 6 | Show the summary |
| 7 | Exit |

## Data format

Tasks are saved as a JSON list:

```json
[
    {
        "task_id": "T001",
        "title": "Debugging",
        "subject": "Computer Science B",
        "due_date": "2026-11-28",
        "status": "pending"
    }
]
```

Valid statuses are `pending` and `completed`. Any other value is treated as `pending` when the file is loaded.

If the file is damaged, the app copies it to `task_data.json.backup` and starts with an empty list instead of crashing. Saves go through a temporary file first, so a crash while saving won't corrupt existing data.

## Notes

- Deleting a task renumbers the tasks after it. If you refer to task IDs anywhere outside the app, keep that in mind.
- The web app loads the data file once per browser session. If you change tasks in the CLI while the web app is open, refresh the page to see them.
- Both interfaces write the whole file on every change, so avoid editing from two places at the same time. The last save wins.
- The swipe-to-delete animation needs `animations.js` next to `app.py`. Without it the app still works, but the animations are skipped.
- Streamlit versions older than 1.39 don't support the button styling used for the delete buttons. The app still works, but those buttons stay blue.

## Optional: light theme

If text looks washed out because Streamlit is using a dark theme, create `.streamlit/config.toml` with:

```toml
[theme]
base = "light"
primaryColor = "#2563eb"
backgroundColor = "#f0f4f8"
secondaryBackgroundColor = "#ffffff"
textColor = "#1e293b"
```