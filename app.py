import os
import html
import datetime
import streamlit as st
import streamlit.components.v1 as components
import storage
from model import Task

icon = "icon.png" if os.path.exists("icon.png") else "✅"
st.set_page_config(page_title="Task Planner", page_icon=icon, layout="wide")

if "manager" not in st.session_state:
    st.session_state.manager = storage.load_data()

manager = st.session_state.manager

if os.path.exists("style.css"):
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def toggle_task(task_id):
    mgr = st.session_state.manager
    task = mgr.get_task(task_id)
    if task is not None:
        done = st.session_state.get(f"check_{task_id}", False)
        task.status = "completed" if done else "pending"
        storage.save_data(mgr)


def delete_task(task_id):
    mgr = st.session_state.manager
    if mgr.delete_task(task_id):
        storage.save_data(mgr)
    st.session_state.pop(f"check_{task_id}", None)


def next_task_id():
    numbers = []
    for tid in manager.task.keys():
        digits = "".join(ch for ch in str(tid) if ch.isdigit())
        if digits:
            numbers.append(int(digits))
    return f"T{(max(numbers) + 1 if numbers else 1):03d}"


def relative_due(due, completed):
    if completed:
        return "Done"
    try:
        days = (datetime.date.fromisoformat(str(due)) - datetime.date.today()).days
    except ValueError:
        return ""
    if days < 0:
        return f"{-days} day(s) overdue"
    if days == 0:
        return "Due today"
    if days == 1:
        return "Due tomorrow"
    return f"In {days} days"


def animate_ui():
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.querySelectorAll('.count-up').forEach(function (el) {
            if (el.dataset.done) return;
            el.dataset.done = '1';
            const target = parseInt(el.textContent, 10) || 0;
            const start = performance.now();
            const duration = 900;
            el.textContent = '0';
            function step(now) {
                const p = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - p, 3);
                el.textContent = Math.round(target * eased);
                if (p < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        });
        doc.querySelectorAll('.progress-fill').forEach(function (el) {
            if (el.dataset.done) return;
            el.dataset.done = '1';
            const width = parseFloat(el.style.width) || 0;
            el.style.width = '0%';
            setTimeout(function () { el.style.width = width + '%'; }, 80);
        });
        </script>
        """,
        height=0,
    )


today = datetime.date.today().strftime("%Y-%m-%d")

st.sidebar.markdown("## Task Planner")
st.sidebar.caption("Stay organized, stay ahead.")
page = st.sidebar.radio("Go to:", ["View Tasks", "Add Task", "Summary"])
st.sidebar.markdown("---")
stats_slot = st.sidebar.empty()
st.sidebar.caption(datetime.date.today().strftime("%A, %d %B %Y"))


if page == "Add Task":
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
                task_id = next_task_id()
                new_task = Task(task_id, title.strip(), subject.strip(), str(due_date))
                manager.add_task(new_task)
                if storage.save_data(manager):
                    st.success(f"Task {task_id} added successfully")
                else:
                    st.error("The task was added but could not be saved to disk.")


elif page == "View Tasks":
    st.title("Your Task List")

    overdue_count = sum(
        1 for t in manager.task.values()
        if str(t.status).lower() == "pending" and str(t.due_date) < today
    )

    if overdue_count > 0:
        st.error(f"You have **{overdue_count}** overdue task(s) that need your attention!")
    else:
        st.success("You have no overdue tasks.")

    if not manager.task:
        st.info("Your task list is empty. Please add some tasks first.")
    else:
        fcol1, fcol2 = st.columns([3, 2])
        with fcol1:
            query = st.text_input("Search", placeholder="Search by title, subject or ID")
        with fcol2:
            filter_option = st.selectbox("Filter Tasks:", ["All tasks", "Pending", "Completed"])

        tasks = sorted(
            manager.task.values(),
            key=lambda t: (str(t.status).lower() == "completed", str(t.due_date)),
        )

        shown = 0
        for t in tasks:
            status = str(t.status).lower()
            if filter_option == "Pending" and status != "pending":
                continue
            if filter_option == "Completed" and status != "completed":
                continue
            if query:
                q = query.lower().strip()
                if (
                    q not in str(t.title).lower()
                    and q not in str(t.subject).lower()
                    and q not in str(t.task_id).lower()
                ):
                    continue

            is_completed = status == "completed"
            is_overdue = (not is_completed) and str(t.due_date) < today

            card_class = "task-card"
            badge = '<span class="badge badge-pending">Pending</span>'
            if is_completed:
                card_class += " completed"
                badge = '<span class="badge badge-done">Completed</span>'
            elif is_overdue:
                card_class += " overdue"
                badge = '<span class="badge badge-overdue">Overdue</span>'

            delay = min(shown * 0.05, 0.5)
            card_html = (
                f'<div class="{card_class}" style="animation-delay:{delay:.2f}s">'
                f'<div class="task-info">'
                f'<div class="task-title">{html.escape(str(t.title))}</div>'
                f'<div class="task-sub">Subject: <b>{html.escape(str(t.subject))}</b>'
                f' &nbsp;|&nbsp; ID: {html.escape(str(t.task_id))}</div>'
                f'</div>'
                f'<div class="task-meta">{badge}'
                f'<div class="task-due">Due: {html.escape(str(t.due_date))}</div>'
                f'<div class="task-rel">{html.escape(relative_due(t.due_date, is_completed))}</div>'
                f'</div>'
                f'</div>'
            )

            col1, col2, col3 = st.columns([8, 2, 1.2])
            with col1:
                st.markdown(card_html, unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
                st.checkbox(
                    "Mark Done",
                    value=is_completed,
                    key=f"check_{t.task_id}",
                    on_change=toggle_task,
                    args=(t.task_id,),
                )
            with col3:
                st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
                st.button(
                    "🗑",
                    key=f"del_{t.task_id}",
                    on_click=delete_task,
                    args=(t.task_id,),
                    help="Delete this task",
                )
            shown += 1

        if shown == 0:
            st.info("No tasks match your search or filter.")


elif page == "Summary":
    st.title("Summary Statistic")

    all_tasks = list(manager.task.values())
    done_count = sum(1 for t in all_tasks if str(t.status).lower() == "completed")
    summary = {
        "total": len(all_tasks),
        "completed": done_count,
        "pending": len(all_tasks) - done_count,
        "overdue": sum(
            1 for t in all_tasks
            if str(t.status).lower() == "pending" and str(t.due_date) < today
        ),
    }

    cards = [
        ("card-blue", summary["total"], "Total Tasks"),
        ("card-green", summary["completed"], "Completed"),
        ("card-orange", summary["pending"], "Pending"),
        ("card-red", summary["overdue"], "Overdue"),
    ]
    cards_html = ""
    for i, (cls, value, label) in enumerate(cards):
        cards_html += (
            f'<div class="summary-card {cls}" style="animation-delay:{i * 0.1:.1f}s">'
            f'<div class="summary-value count-up">{value}</div>'
            f'<div class="summary-label">{label}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="summary-container">{cards_html}</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("Overall Progress")

    if summary["total"] > 0:
        pct = summary["completed"] / summary["total"] * 100
        st.markdown(
            f'<div class="progress-track"><div class="progress-fill" style="width:{pct:.0f}%"></div></div>',
            unsafe_allow_html=True,
        )
        st.write(f"You have completed **{pct:.0f}%** of your tasks.")
    else:
        st.info("Add some tasks to see your progress!")

    upcoming = sorted(
        [t for t in all_tasks if str(t.status).lower() == "pending"],
        key=lambda t: str(t.due_date),
    )[:5]

    if upcoming:
        st.subheader("Up Next")
        items = ""
        for t in upcoming:
            cls = "upcoming-item overdue" if str(t.due_date) < today else "upcoming-item"
            items += (
                f'<div class="{cls}">'
                f'<span class="upcoming-title">{html.escape(str(t.title))}</span>'
                f'<span class="upcoming-date">{html.escape(str(t.due_date))}'
                f' &nbsp;·&nbsp; {html.escape(relative_due(t.due_date, False))}</span>'
                f'</div>'
            )
        st.markdown(f'<div class="upcoming-list">{items}</div>', unsafe_allow_html=True)


total_tasks = len(manager.task)
pending_tasks = sum(1 for t in manager.task.values() if str(t.status).lower() == "pending")
stats_slot.markdown(
    f'<div class="sidebar-stat"><span>{total_tasks}</span> total</div>'
    f'<div class="sidebar-stat"><span>{pending_tasks}</span> pending</div>',
    unsafe_allow_html=True,
)

animate_ui()