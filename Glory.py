import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import os
import json
import sys
import time

class GloryAI:
    def __init__(self):
        self.knowledge = {}
        self.load_knowledge()
        self.custom_layout = {}
        self.load_custom_layout()

    def respond(self, question):
        question = question.lower()
        if question in self.knowledge:
            return self.knowledge[question]
        else:
            response = "Das weiß ich leider noch nicht. Ich werde im Internet nachsehen."
            internet_response = self.search_internet(question)
            return internet_response

    def train(self, question, answer):
        self.knowledge[question.lower()] = answer
        self.save_knowledge()

    def search_internet(self, query):
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = requests.get(search_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                snippets = soup.find_all('span', {'class': 'aCOpRe'})
                collected_data = []
                for snippet in snippets:
                    text = snippet.get_text().strip()
                    if text:
                        collected_data.append(text)
                        if len(collected_data) >= 3:
                            break
                if collected_data:
                    combined_data = " ".join(collected_data)
                    self.train(query, combined_data)
                    return f"Ich habe folgendes gelernt: {combined_data[:200]}..."
                else:
                    return "Keine relevanten Informationen gefunden."
            else:
                return f"Fehler beim Abrufen der Informationen: {response.status_code}"
        except Exception as e:
            return f"Ein Fehler ist aufgetreten: {str(e)}"

    def save_knowledge(self):
        with open("knowledge.json", "w") as file:
            json.dump(self.knowledge, file)

    def load_knowledge(self):
        if os.path.exists("knowledge.json"):
            with open("knowledge.json", "r") as file:
                self.knowledge = json.load(file)

    def save_custom_layout(self):
        with open("layout.json", "w") as file:
            json.dump(self.custom_layout, file)

    def load_custom_layout(self):
        if os.path.exists("layout.json"):
            with open("layout.json", "r") as file:
                self.custom_layout = json.load(file)

    def add_custom_button(self, button_name, command):
        self.custom_layout[button_name] = command
        self.save_custom_layout()

    def get_knowledge_version(self, knowledge_version_url):
        """Holt die Version der Wissensdatei vom Server."""
        try:
            response = requests.get(knowledge_version_url)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Fehler beim Abrufen der Wissensdatei-Version: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {str(e)}")
            return None

    def ensure_knowledge_file(self, knowledge_url, knowledge_version_url, file_name, version_file_name):
        """Stellt sicher, dass die Wissensdatei aktuell ist."""
        server_version = self.get_knowledge_version(knowledge_version_url)
        if not server_version:
            print("Konnte die Wissensdatei-Version nicht abrufen. Überspringe Update.")
            return

        local_version = None
        if os.path.exists(version_file_name):
            with open(version_file_name, "r") as version_file:
                local_version = version_file.read().strip()

        if local_version != server_version:
            print("Wissensdatei ist veraltet oder fehlt. Lade sie herunter...")
            if self.download_file(knowledge_url, file_name):
                with open(version_file_name, "w") as version_file:
                    version_file.write(server_version)
                print("Wissensdatei erfolgreich aktualisiert.")
            else:
                print("Fehler beim Herunterladen der Wissensdatei.")
        else:
            print("Wissensdatei ist aktuell.")

    def download_file(self, url, file_name):
        """Lädt eine Datei von einer URL herunter."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_name, "wb") as file:
                    file.write(response.content)
                return True
            else:
                print(f"Fehler beim Herunterladen der Datei: {response.status_code}")
                return False
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {str(e)}")
            return False

    def save_chat_history(self, chat_history):
        with open("chat_history.json", "w") as file:
            json.dump(chat_history, file)

    def load_chat_history(self):
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r") as file:
                return json.load(file)
        return []

# KI-Instanz
if __name__ == "__main__":
    # URLs und Versionsinformationen
    VERSION_URL = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/version.txt"
    UPDATE_URL = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/Glory.exe"
    KNOWLEDGE_URL = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/knowledge.json"
    KNOWLEDGE_VERSION_URL = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/knowledge_version.txt"
    CURRENT_VERSION = "1.0.0"  # Aktuelle Version

    # Dateinamen
    CURRENT_FILE = "Glory.exe"
    NEW_FILE = "Glory_new.exe"
    KNOWLEDGE_FILE = "knowledge.json"
    KNOWLEDGE_VERSION_FILE = "knowledge_version.txt"

    # Prüfe auf Updates
    try:
        response = requests.get(VERSION_URL)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version > CURRENT_VERSION:
                print(f"Neue Version gefunden: {latest_version}. Update wird heruntergeladen...")
                response = requests.get(UPDATE_URL, stream=True)
                with open(NEW_FILE, "wb") as file:
                    file.write(response.content)
                print("Update wird angewendet...")
                os.remove(CURRENT_FILE)
                os.rename(NEW_FILE, CURRENT_FILE)
                os.startfile(CURRENT_FILE)
                sys.exit()
            else:
                print("Keine Updates verfügbar. Überprüfe die Wissensdatei...")
        else:
            print(f"Fehler beim Abrufen der Version: {response.status_code}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {str(e)}")

    # Stelle sicher, dass die Wissensdatei vorhanden und aktuell ist
    glory = GloryAI()
    glory.ensure_knowledge_file(KNOWLEDGE_URL, KNOWLEDGE_VERSION_URL, KNOWLEDGE_FILE, KNOWLEDGE_VERSION_FILE)

    # GUI erstellen
    root = tk.Tk()
    root.title("Glory AI")
    root.geometry("500x600")
    root.configure(bg="#f0f8ff")

    chat_history = glory.load_chat_history()

    def update_chat(message, sender="User"):
        chat_box.configure(state="normal")
        chat_box.insert("end", f"{sender}: {message}\n")
        chat_box.see("end")
        chat_box.configure(state="disabled")
        chat_history.append({"sender": sender, "message": message})
        glory.save_chat_history(chat_history)

    def handle_input(event=None):
        user_message = user_input.get()
        if user_message.strip():
            update_chat(user_message, sender="User")
            response = glory.respond(user_message)
            update_chat(response, sender="Glory")
        user_input.delete(0, "end")

    header = tk.Frame(root, bg="#f0f8ff", pady=10)
    header.pack(fill="x")

    sun_icon = tk.Label(header, text="☀", font=("Arial", 24), bg="#f0f8ff", fg="#ffcc00")
    sun_icon.pack(side="left", padx=10)

    title = tk.Label(header, text="Glory AI", font=("Arial", 20, "bold"), bg="#f0f8ff", fg="#4682b4")
    title.pack(side="left")

    chat_frame = tk.Frame(root, bg="#f0f8ff")
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    chat_box = tk.Text(chat_frame, wrap="word", height=20, state="disabled", bg="#ffffff", fg="#000000", font=("Arial", 12))
    chat_box.pack(padx=5, pady=5, fill="both", expand=True)

    chat_scroll = tk.Scrollbar(chat_frame, command=chat_box.yview)
    chat_box["yscrollcommand"] = chat_scroll.set
    chat_scroll.pack(side="right", fill="y")

    input_frame = tk.Frame(root, bg="#f0f8ff")
    input_frame.pack(padx=10, pady=10, fill="x")

    user_input = tk.Entry(input_frame, font=("Arial", 12), width=40)
    user_input.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    user_input.bind("<Return>", handle_input)

    send_button = tk.Button(user_input_frame, text="Senden", font=("Arial", 12), bg="#4682b4", fg="#ffffff", command=handle_input)
    send_button.pack(side="right", padx=5)

    def close_application():
        if messagebox.askyesno("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_application)

    # Chat-Historie wiederherstellen
    for entry in chat_history:
        update_chat(entry["message"], sender=entry["sender"])

    root.mainloop()
   
