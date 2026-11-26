import datetime
import html
import json
import os
import streamlit as st
import streamlit.components.v1 as components
import storage
from model import STATUS_COMPLETED, STATUS_PENDING




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "icon.png")

st.set_page_config(
    page_title="Task Planner",
    page_icon=ICON_PATH if os.path.exists(ICON_PATH) else "✅",
    layout="wide",
)

if "manager" not in st.session_state:
    st.session_state.manager = storage.load_data()
if "delete_target" not in st.session_state:
    st.session_state.delete_target = None

manager = st.session_state.manager

# ==================LOAD CSS AND JAVASCRIPT====================

def read_file(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_css():
    css = read_file("style.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def load_script():
    script = read_file("animations.js")
    if not script:
        return

    script_literal = json.dumps(script).replace("</", "<\\/")
    components.html(
        f"""
        <script>
        const doc = window.parent.document;
        if (!doc.getElementById('planner-script')) {{
            const el = doc.createElement('script');
            el.id = 'planner-script';
            el.textContent = {script_literal};
            doc.head.appendChild(el);
        }}
        </script>
        """,
        height=0,
    )


# ======================UI HELPERS======================

def spacer():
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

def relative_due(task):
    if task.is_completed():
        return "Done"

    try:
        days = (datetime.date.fromisoformat(task.due_date) - datetime.date.today()).days
    except ValueError:
        return ""

    if days < 0:
        return f"{-days} day(s) overdue"
    if days == 0:
        return "Due today"
    if days == 1:
        return "Due tomorrow"
    return f"In {days} days"


def task_card_html(task, index, confirming):
    css_class = "task-card"
    badge_class, badge_text = "badge-pending", "Pending"

    if task.is_completed():
        css_class += " completed"
        badge_class, badge_text = "badge-done", "Completed"
    elif task.is_overdue():
        css_class += " overdue"
        badge_class, badge_text = "badge-overdue", "Overdue"

    if confirming:
        css_class += " confirming"
        badge_class, badge_text = "badge-overdue", "Delete?"

    delay = min(index * 0.05, 0.5)

    return (
        f'<div class="{css_class}" style="animation-delay:{delay:.2f}s">'
        f'<div class="task-info">'
        f'<div class="task-title">{html.escape(task.title)}</div>'
        f'<div class="task-sub">Subject: <b>{html.escape(task.subject)}</b>'
        f' &nbsp;|&nbsp; ID: {html.escape(task.task_id)}</div>'
        f'</div>'
        f'<div class="task-meta">'
        f'<span class="badge {badge_class}">{badge_text}</span>'
        f'<div class="task-due">Due: {html.escape(task.due_date)}</div>'
        f'<div class="task-rel">{html.escape(relative_due(task))}</div>'
        f'</div>'
        f'</div>'
    )



# ========================CALLBACKS (checkbox and delete buttons)=====================

def toggle_task(task_id):
    mgr = st.session_state.manager
    task = mgr.get_task(task_id)

    if task is not None:
        done = st.session_state.get(f"check_{task_id}", False)
        task.status = STATUS_COMPLETED if done else STATUS_PENDING
        storage.save_data(mgr)


def ask_delete(task_id):
    st.session_state.delete_target = task_id


def cancel_delete():
    st.session_state.delete_target = None


def delete_confirmed(task_id):
    mgr = st.session_state.manager

    if mgr.delete_task(task_id):
        storage.save_data(mgr)

    for key in list(st.session_state.keys()):
        if str(key).startswith("check_"):
            del st.session_state[key]

    st.session_state.delete_target = None


# =============================PAGE: ADD TASK==================

def page_add_task():
    st.title("Add a New Task")

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task Title", placeholder="e.g. Finish chapter 4 report")
        subject = st.text_input("Subject", placeholder="e.g. Mathematics")
        due_date = st.date_input("Due Date", value=datetime.date.today())

        submitted = st.form_submit_button("Save Task")

        if submitted:
            if not title.strip() or not subject.strip():
                st.error("Error: Subject or title cannot be blank!")
            else:
                task = manager.create_task(title.strip(), subject.strip(), str(due_date))

                if storage.save_data(manager):
                    st.success(f"Task {task.task_id} added successfully")
                else:
                    st.error("The task was added but could not be saved to disk.")



# =================== PAGE: VIEW TASKS ==================

STATUS_FILTERS = {
    "All tasks": None,
    "Pending": STATUS_PENDING,
    "Completed": STATUS_COMPLETED,
}


def render_task_row(task, index, confirming):
    card_col, middle_col, right_col = st.columns([7, 1.8, 1.8])

    with card_col:
        st.markdown(task_card_html(task, index, confirming), unsafe_allow_html=True)

    if confirming:
        with middle_col:
            spacer()
            st.button(
                "Delete",
                key=f"confirm_{task.task_id}",
                on_click=delete_confirmed,
                args=(task.task_id,),
            )
        with right_col:
            spacer()
            st.button("Cancel", key=f"cancel_{task.task_id}", on_click=cancel_delete)
    else:
        with middle_col:
            spacer()
            st.checkbox(
                "Mark Done",
                value=task.is_completed(),
                key=f"check_{task.task_id}",
                on_change=toggle_task,
                args=(task.task_id,),
            )
        with right_col:
            spacer()
            st.button(
                "🗑️",
                key=f"trash_{task.task_id}",
                on_click=ask_delete,
                args=(task.task_id,),
                help="Delete this task",
            )


def page_view_tasks():
    st.title("Your Task List")

    overdue_count = manager.get_summary()["overdue"]
    if overdue_count > 0:
        st.error(f"You have **{overdue_count}** overdue task(s) that need your attention!")
    else:
        st.success("You have no overdue tasks.")

    if not manager.task:
        st.info("Your task list is empty. Please add some tasks first.")
        return

    search_col, filter_col = st.columns([3, 2])
    with search_col:
        query = st.text_input("Search", placeholder="Search by title, subject or ID")
    with filter_col:
        filter_name = st.selectbox("Filter Tasks:", list(STATUS_FILTERS))

    st.caption("Tip: drag a task to the left to delete it.")

    delete_id = st.session_state.delete_target
    if delete_id not in manager.task:
        delete_id = None
        st.session_state.delete_target = None

    if delete_id:
        st.warning(
            f"Delete task **{delete_id}** ({manager.get_task(delete_id).title})? "
            f"This cannot be undone, and the remaining task IDs will be renumbered."
        )

    tasks = manager.filter_tasks(STATUS_FILTERS[filter_name], query)
    if not tasks:
        st.info("No tasks match your search or filter.")
        return

    for index, task in enumerate(tasks):
        render_task_row(task, index, confirming=(task.task_id == delete_id))



# ======================= PAGE: SUMMARY ======================

def page_summary():
    st.title("Summary Statistic")

    summary = manager.get_summary()

    cards = [
        ("card-blue", summary["total"], "Total Tasks"),
        ("card-green", summary["completed"], "Completed"),
        ("card-orange", summary["pending"], "Pending"),
        ("card-red", summary["overdue"], "Overdue"),
    ]
    cards_html = ""
    for i, (css_class, value, label) in enumerate(cards):
        cards_html += (
            f'<div class="summary-card {css_class}" style="animation-delay:{i * 0.1:.1f}s">'
            f'<div class="summary-value count-up">{value}</div>'
            f'<div class="summary-label">{label}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="summary-container">{cards_html}</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("Overall Progress")

    if summary["total"] > 0:
        percent = summary["completed"] / summary["total"] * 100
        st.markdown(
            f'<div class="progress-track">'
            f'<div class="progress-fill" style="width:{percent:.0f}%"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.write(f"You have completed **{percent:.0f}%** of your tasks.")
    else:
        st.info("Add some tasks to see your progress!")

    upcoming = manager.get_upcoming(limit=5)
    if upcoming:
        st.subheader("Up Next")
        items = ""
        for task in upcoming:
            css_class = "upcoming-item overdue" if task.is_overdue() else "upcoming-item"
            items += (
                f'<div class="{css_class}">'
                f'<span class="upcoming-title">{html.escape(task.title)}</span>'
                f'<span class="upcoming-date">{html.escape(task.due_date)}'
                f' &nbsp;·&nbsp; {html.escape(relative_due(task))}</span>'
                f'</div>'
            )
        st.markdown(f'<div class="upcoming-list">{items}</div>', unsafe_allow_html=True)


# =================== SIDEBAR =====================

PAGES = {
    "View Tasks": page_view_tasks,
    "Add Task": page_add_task,
    "Summary": page_summary,
}


def render_sidebar():
    st.sidebar.markdown("## Task Planner")
    st.sidebar.caption("Stay organized, stay ahead.")
    page = st.sidebar.radio("Go to:", list(PAGES))
    st.sidebar.markdown("---")
    stats_slot = st.sidebar.empty()
    st.sidebar.caption(datetime.date.today().strftime("%A, %d %B %Y"))
    return page, stats_slot


def render_sidebar_stats(stats_slot):
    summary = manager.get_summary()
    stats_slot.markdown(
        f'<div class="sidebar-stat"><span>{summary["total"]}</span> total</div>'
        f'<div class="sidebar-stat"><span>{summary["pending"]}</span> pending</div>',
        unsafe_allow_html=True,
    )


# ===================== RUN APP =================

load_css()

current_page, sidebar_stats_slot = render_sidebar()

if current_page != "View Tasks":
    st.session_state.delete_target = None

PAGES[current_page]()

render_sidebar_stats(sidebar_stats_slot)
load_script()