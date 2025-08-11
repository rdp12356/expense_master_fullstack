import os
import sys
from typing import List, Dict, Optional

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout

from kivy_garden.graph import Graph, MeshLinePlot

from services.storage import StorageService
from services.api_client import ApiClient


def resource_path(relative_path: str) -> str:
    """Resolve resource path for dev and PyInstaller bundle."""
    base_path = getattr(sys, '_MEIPASS', None)
    if base_path:
        return os.path.join(base_path, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


class SuperApp(MDApp):
    dialog: Optional[MDDialog] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = StorageService()
        self.api_client = ApiClient()
        self.graph_plot = MeshLinePlot(color=[0.2, 0.6, 0.86, 1])

    def build(self):
        self.title = "SuperApp"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Dark"

        root = Builder.load_file(resource_path("app.kv"))
        # Defer initial UI population to after first frame
        Clock.schedule_once(lambda *_: self.refresh_all())
        return root

    def refresh_all(self):
        self.refresh_tasks_list()
        self.update_graph()

    # UI Actions
    def open_nav(self):
        nav = self.root.ids.nav_drawer
        nav.set_state("toggle")

    def toggle_theme(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        Snackbar(text=f"Theme: {self.theme_cls.theme_style}").open()

    # Tasks
    def _is_online(self) -> bool:
        return bool(getattr(self.api_client, "_base_url", ""))

    def _get_tasks(self):
        if self._is_online():
            try:
                return self.api_client.list_tasks()
            except Exception:
                return self.storage.list_tasks()
        return self.storage.list_tasks()

    def refresh_tasks_list(self):
        container = self.root.ids.tasks_list
        container.clear_widgets()
        tasks = self._get_tasks()
        for task in tasks:
            item = OneLineAvatarIconListItem(text=task["title"], on_release=lambda x, t=task: self.open_edit_dialog(t))
            status_icon = "check-circle" if task["completed"] else "checkbox-blank-circle-outline"
            item.add_widget(IconRightWidget(icon=status_icon, on_release=lambda x, t=task: self.toggle_complete(t)))
            container.add_widget(item)

    def update_graph(self):
        # Simple plot: x=index, y=completed count running total
        tasks = self._get_tasks()
        y_values = []
        total = 0
        for task in tasks:
            total += 1 if task["completed"] else 0
            y_values.append(total)
        if not y_values:
            y_values = [0]
        graph: Graph = self.root.ids.chart
        # Adjust axis bounds dynamically
        xmax = max(10, len(y_values))
        ymax = max(10, max(y_values))
        graph.xmax = xmax
        graph.ymax = ymax
        graph.xmin = 0
        graph.ymin = 0
        if self.graph_plot in graph.plots:
            graph.remove_plot(self.graph_plot)
        self.graph_plot.points = [(i + 1, y) for i, y in enumerate(y_values)]
        graph.add_plot(self.graph_plot)

    def show_add_task_dialog(self):
        if self.dialog:
            self.dialog.dismiss()
        title_field = MDTextField(hint_text="Title", max_text_length=64)
        desc_field = MDTextField(hint_text="Description", max_text_length=256)
        content = MDBoxLayout(orientation="vertical", spacing="12dp", padding="8dp")
        content.add_widget(title_field)
        content.add_widget(desc_field)
        self.dialog = MDDialog(
            title="Add Task",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda *_: self.add_task(title_field.text, desc_field.text)),
            ],
        )
        self.dialog.open()

    def open_edit_dialog(self, task: Dict):
        if self.dialog:
            self.dialog.dismiss()
        title_field = MDTextField(hint_text="Title", text=task["title"], max_text_length=64)
        desc_field = MDTextField(hint_text="Description", text=task["description"] or "", max_text_length=256)
        content = MDBoxLayout(orientation="vertical", spacing="12dp", padding="8dp")
        content.add_widget(title_field)
        content.add_widget(desc_field)
        self.dialog = MDDialog(
            title="Edit Task",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="DELETE", on_release=lambda *_: self.delete_task(task["id"])),
                MDFlatButton(text="CANCEL", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=lambda *_: self.save_task(task["id"], title_field.text, desc_field.text)),
            ],
        )
        self.dialog.open()

    def add_task(self, title: str, description: str):
        if not title.strip():
            Snackbar(text="Title is required").open()
            return
        if self._is_online():
            try:
                self.api_client.create_task(title.strip(), description.strip())
            except Exception:
                self.storage.create_task(title.strip(), description.strip())
        else:
            self.storage.create_task(title.strip(), description.strip())
        if self.dialog:
            self.dialog.dismiss()
        Snackbar(text="Task added").open()
        self.refresh_all()

    def save_task(self, task_id: int, title: str, description: str):
        if not title.strip():
            Snackbar(text="Title is required").open()
            return
        if self._is_online():
            try:
                self.api_client.update_task(task_id, title=title.strip(), description=description.strip())
            except Exception:
                self.storage.update_task(task_id, title=title.strip(), description=description.strip())
        else:
            self.storage.update_task(task_id, title=title.strip(), description=description.strip())
        if self.dialog:
            self.dialog.dismiss()
        Snackbar(text="Task saved").open()
        self.refresh_all()

    def delete_task(self, task_id: int):
        if self._is_online():
            try:
                self.api_client.delete_task(task_id)
            except Exception:
                self.storage.delete_task(task_id)
        else:
            self.storage.delete_task(task_id)
        if self.dialog:
            self.dialog.dismiss()
        Snackbar(text="Task deleted").open()
        self.refresh_all()

    def toggle_complete(self, task: Dict):
        new_completed = 0 if task["completed"] else 1
        if self._is_online():
            try:
                self.api_client.update_task(task["id"], completed=bool(new_completed))
            except Exception:
                self.storage.update_task(task["id"], completed=new_completed)
        else:
            self.storage.update_task(task["id"], completed=new_completed)
        Snackbar(text="Toggled status").open()
        self.refresh_all()

    # Settings
    def save_api_base_url(self, value: str):
        self.api_client.set_base_url(value.strip())
        Snackbar(text="API base URL saved").open()


if __name__ == "__main__":
    SuperApp().run()