from typing import Callable
from terminal import *
from app.components.SplitMenu import Entry, SplitMenu
from app.modules.GlobalStore import use_store
from app.components.Navigation import SECTIONS, ROLE_TITLES, Section, navigate

def NavigationPage() -> Page:
    title = TextLabel("PayWise Dashboard", style=(BOLD, UNDERLINE, BRIGHT_BLUE))
    status = TextLabel("", style=(BRIGHT_RED,))
    body = StackLayout()
    reset: Callable[[], None] = lambda: None

    def log_out() -> None:
        use_store.set("current_user", None)
        navigate("login")

    def open_section(section: Section):
        def action() -> None:
            if navigate(section.page):
                status.set_text("")
            else:
                status.set_text(f"{section.label} is not available yet.")
        return action

    def rebuild(role: str | None) -> None:
        nonlocal reset
        sections = SECTIONS.get(role, ())
        title.set_text(f"PayWise Dashboard - {ROLE_TITLES.get(role, role)}" if role else "PayWise Dashboard")
        status.size = (max([len(f"{s.label} is not available yet.") for s in sections] + [1]), 1)
        status.set_text("")
        entries = [
            Entry(s.label, open_section(s), [f"- {action}" for action in s.actions], (BRIGHT_BLUE,))
            for s in sections
        ]
        split, reset = SplitMenu(
            entries,
            footer=[("Log out", log_out, (BRIGHT_RED,)), ("Exit", Scheduler.stop, (DIM,))],
            on_focus=lambda: status.set_text(""),
        )
        for child in list(body.children):
            body.remove_child(child)
        body.add_child(split)

    rebuild(use_store.get("current_role"))
    use_store.subscribe("current_role", lambda new, old: rebuild(new))

    stack = StackLayout(
        title,
        body,
        status,
        spacing=1,
        align="center",
        position=(0.5, 0.5),
        anchor_point=(0.5, 0.5),
    )

    def on_enter() -> None:
        status.set_text("")
        reset()

    return Page(stack, name="navigation", onEnter=on_enter)

__all__ = ["NavigationPage"]