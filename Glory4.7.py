import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import os
import json
import sys
import subprocess

class GloryAI:
    def __init__(self):
        self.knowledge = {}
        self.load_knowledge()

    def respond(self, question):
        question = question.lower()
        if question in self.knowledge:
            return self.knowledge[question]
        else:
            # Frage nach Erlaubnis, im Internet zu suchen
            response = "Das weiß ich leider noch nicht. Soll ich im Internet nachsehen?"
            if messagebox.askyesno("Internet", response):
                internet_response = self.search_internet(question)
                return internet_response
            else:
                return "Okay, ich werde nicht suchen."

    def train(self, question, answer):
        self.knowledge[question.lower()] = answer
        self.save_knowledge()

    def search_internet(self, query):
        try:
            url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                
                # Sammle die ersten sinnvollen Absätze
                collected_data = []
                for paragraph in paragraphs:
                    if paragraph.text.strip():
                        collected_data.append(paragraph.text.strip())
                        if len(collected_data) >= 3:  # Begrenze die Anzahl der Absätze
                            break
                
                # Speichere die gesammelten Daten in den Wissensspeicher
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

    def log_search(self, query, result):
        with open("search_log.txt", "a") as file:
            file.write(f"Query: {query}\nResult: {result}\n{'-'*50}\n")

    def modify_program(self, pattern, replacement):
        """Ändere den Code basierend auf dem gegebenen Muster und Ersatz."""
        try:
            with open(__file__, "r") as file:
                code = file.read()

            # Ersetze den Code basierend auf dem gegebenen Muster
            if pattern in code:
                new_code = code.replace(pattern, replacement)

                # Schreibe den neuen Code zurück in die Datei
                with open(__file__, "w") as file:
                    file.write(new_code)

                return "Der Code wurde erfolgreich geändert."
            else:
                return "Das Muster wurde im Code nicht gefunden."
        except Exception as e:
            return f"Ein Fehler ist aufgetreten: {str(e)}"

    def update_program(self, update_url):
        """Ändert den Programmcode durch Download der neuesten Version."""
        try:
            response = requests.get(update_url, stream=True)
            if response.status_code == 200:
                temp_file = "temp_update.exe"
                with open(temp_file, "wb") as file:
                    file.write(response.content)
                
                # Starte die neue Datei und beende die aktuelle Instanz
                os.startfile(temp_file)
                sys.exit()  # Beendet das aktuelle Programm
            else:
                return f"Fehler beim Herunterladen der Aktualisierung: {response.status_code}"
        except Exception as e:
            return f"Ein Fehler ist aufgetreten: {str(e)}"

    def restart_program(self):
        """Startet das Programm neu."""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def check_for_update(self, version_url):
        """Prüft, ob eine neue Version verfügbar ist."""
        try:
            response = requests.get(version_url)
            if response.status_code == 200:
                latest_version = response.text.strip()
                current_version = "1.0.0"  # Setze die aktuelle Programmversion hier
                if latest_version > current_version:
                    return True, latest_version
                else:
                    return False, current_version
            else:
                return False, "Fehler bei der Versionsprüfung"
        except Exception as e:
            return False, f"Ein Fehler ist aufgetreten: {str(e)}"

# KI-Instanz
glory = GloryAI()

# Prüfen auf Updates
update_url = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/Glory4.py"  # Beispiel-URL für den Code
version_url = "https://raw.githubusercontent.com/GloryVision/GloryVision/main/version.txt"  # Beispiel-URL für die Version

update_available, info = glory.check_for_update(version_url)
if update_available:
    if messagebox.askyesno("Update verfügbar", f"Eine neue Version ({info}) ist verfügbar. Jetzt aktualisieren?"):
        glory.update_program(update_url)

# GUI erstellen
root = tk.Tk()
root.title("Glory AI")
root.geometry("500x600")
root.configure(bg="#f0f8ff")

# Kopfbereich
header = tk.Frame(root, bg="#f0f8ff", pady=10)
header.pack(fill="x")

sun_icon = tk.Label(header, text="☀", font=("Arial", 24), bg="#f0f8ff", fg="#ffcc00")
sun_icon.pack(side="left", padx=10)

title = tk.Label(header, text="Glory AI", font=("Arial", 20, "bold"), bg="#f0f8ff", fg="#4682b4")
title.pack(side="left")

# Chatbereich
chat_frame = tk.Frame(root, bg="#f0f8ff")
chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

chat_box = tk.Text(chat_frame, wrap="word", height=20, state="normal", bg="#ffffff", fg="#000000", font=("Arial", 12))
chat_box.pack(padx=5, pady=5, fill="both", expand=True)

chat_scroll = tk.Scrollbar(chat_frame, command=chat_box.yview)
chat_box["yscrollcommand"] = chat_scroll.set
chat_scroll.pack(side="right", fill="y")

# Eingabefeld
input_frame = tk.Frame(root, bg="#f0f8ff")
input_frame.pack(padx=10, pady=10, fill="x")

user_input = tk.Entry(input_frame, font=("Arial", 12), width=40)
user_input.pack(side="left", padx=5, pady=5, fill="x", expand=True)

def send_message():
    user_message = user_input.get()
    if not user_message.strip():
        return
    chat_box.insert(tk.END, f"Du: {user_message}\n")
    response = glory.respond(user_message)
    chat_box.insert(tk.END, f"Glory: {response}\n\n")
    user_input.delete(0, tk.END)

def collect_information():
    topic = user_input.get().strip()
    if topic:
        response = glory.search_internet(topic)
        messagebox.showinfo("Information gesammelt", response)
    else:
        messagebox.showwarning("Fehler", "Bitte ein Thema eingeben.")

send_button = tk.Button(input_frame, text="Senden", command=send_message, bg="#4682b4", fg="#ffffff", font=("Arial", 12, "bold"))
send_button.pack(side="left", padx=5)

collect_button = tk.Button(input_frame, text="Information sammeln", command=collect_information, bg="#4682b4", fg="#ffffff", font=("Arial", 12, "bold"))
collect_button.pack(side="left", padx=5)

update_button = tk.Button(input_frame, text="Update ausführen", command=lambda: glory.update_program(update_url), bg="#4682b4", fg="#ffffff", font=("Arial", 12, "bold"))
update_button.pack(side="left", padx=5)

# Wissen hinzufügen
knowledge_frame = tk.LabelFrame(root, text="Glory trainieren", bg="#f0f8ff", fg="#4682b4", font=("Arial", 12))
knowledge_frame.pack(padx=10, pady=10, fill="x")

tk.Label(knowledge_frame, text="Frage:", bg="#f0f8ff", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
entry_question = tk.Entry(knowledge_frame, font=("Arial", 12), width=30)
entry_question.grid(row=0, column=1, padx=5, pady=5)

tk.Label(knowledge_frame, text="Antwort:", bg="#f0f8ff", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
entry_answer = tk.Entry(knowledge_frame, font=("Arial", 12), width=30)
entry_answer.grid(row=1, column=1, padx=5, pady=5)

def add_knowledge():
    question = entry_question.get().strip()
    answer = entry_answer.get().strip()
    if question and answer:
        glory.train(question, answer)
        messagebox.showinfo("Erfolg", f"Neue Information hinzugefügt:\nFrage: {question}\nAntwort: {answer}")
        entry_question.delete(0, tk.END)
        entry_answer.delete(0, tk.END)
    else:
        messagebox.showwarning("Fehler", "Bitte sowohl Frage als auch Antwort ausfüllen.")

add_button = tk.Button(knowledge_frame, text="Hinzufügen", command=add_knowledge, bg="#4682b4", fg="#ffffff", font=("Arial", 12))
add_button.grid(row=2, column=0, columnspan=2, pady=10)

# Hauptloop starten
root.mainloop()
