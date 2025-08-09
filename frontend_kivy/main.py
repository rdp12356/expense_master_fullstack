# main.py
import os, webbrowser, threading
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from local_db import init_local_db, execute
from email_service import send_verification_email  # optional if used in-app (not recommended)
KV = Builder.load_string(open(os.path.join(os.path.dirname(__file__),"views.kv")).read())

class LoginScreen(BoxLayout):
    def send_magic(self):
        email = self.ids.email.text.strip()
        if not email:
            return
        import requests, os
        res = requests.post(f"http://127.0.0.1:5000/request-magic-link", json={"email":email})
        if res.ok:
            from kivy.app import App
            App.get_running_app().root.clear_widgets()
            from kivy.uix.label import Label
            App.get_running_app().root.add_widget(Label(text="Magic link sent. Check your email."))

class MainScreen(BoxLayout):
    def open_dashboard(self):
        webbrowser.open("http://127.0.0.1:5000/dashboard")

class ExpenseApp(App):
    def build(self):
        init_local_db()
        return LoginScreen()

if __name__ == "__main__":
    ExpenseApp().run()
