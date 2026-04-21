import asyncio
import os
import sys
import logging
import subprocess
import re
import datetime # Added for the 'time' command
import psutil
import webbrowser # Added for web navigation
import pyautogui # Added for system controls like volume
import wikipedia # Added for information retrieval
import pyjokes # Added for jokes
import time # Added for screenshot filename
import pyperclip
import pyttsx3
import requests
import speech_recognition as sr
from openai import OpenAI
from typing import Optional

# --- 1. THE BRAIN & SPEECH CONFIG ---
API_KEY = "your-api-key-here"
client = OpenAI(api_key=API_KEY)

class JayVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.configure_voice()

    def configure_voice(self):
        try:
            voices = self.engine.getProperty('voices')
            # Jarvis-like voice settings: Look for David or any non-Zira male voice
            for v in voices: # type: ignore
                if "david" in v.name.lower() or ("male" in v.name.lower() and "zira" not in v.name.lower()):
                    self.engine.setProperty('voice', v.id)
                    break
            self.engine.setProperty('rate', 180) 
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            logging.error(f"Voice configuration error: {e}")

    def speak(self, text: str):
        print(f"JAY: {text}")
        try:
            # Prevent engine from hanging if already in a loop
            if self.engine._inLoop:
                self.engine.endLoop()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass

# --- 2. THE MAIL PROTOCOL (FIXED EZGMAIL) ---
class JayMail:
    def __init__(self):
        self.active = False
        try:
            # We import inside __init__ to handle 'ezgmail' potentially missing
            import ezgmail # type: ignore
            self.ez = ezgmail
            # Check for credentials before initializing
            if os.path.exists('credentials.json'):
                # token.json stores your login. If it doesn't exist, init() opens browser.
                self.ez.init() 
                self.active = True
            else:
                logging.warning("credentials.json not found. Mail protocols bypassed.")
        except Exception as e:
            logging.error(f"Mail Link Failed: {e}")

    async def check_inbox(self) -> str:
        if not self.active: return "My apologies, but my connection to your Gmail is currently offline."
        unread = await asyncio.to_thread(self.ez.unread)
        if not unread:
            return "Your inbox is clear, sir. No new transmissions."
        return f"You have {len(unread)} unread threads. The latest is from {unread[0].messages[0].sender}."

    async def send(self, to: str, sub: str, body: str):
        if not self.active: return "Communication systems are offline."
        await asyncio.to_thread(self.ez.send, to, sub, body)
        return "Transmission sent successfully."

# --- 3. THE CORE ASSISTANT ---
class JayAssistant:
    def __init__(self):
        self.voice = JayVoice()
        self.mail = JayMail()
        self.recognizer = sr.Recognizer()
        self.contacts = {
            "devansh": "devansh@example.com",
            "manager": "office@company.com",
            "home": "family@gmail.com"
        }
        self.is_running = True

    async def ai_brain(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are J.A.Y., a highly advanced AI system designed by and serving Devansh Prabhakar. You are sophisticated, efficient, and professional."},
                    {"role": "user", "content": prompt}
                ],
                timeout=10
            )
            return response.choices[0].message.content or "I'm processing that, sir."
        except Exception:
            return "My neural processors are experiencing latency, sir."

    async def listen(self) -> str:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # type: ignore
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return self.recognizer.recognize_google(audio).lower() # type: ignore
            except:
                return ""

    async def run(self):
        self.voice.speak("Synaptic link established. J.A.Y. is online. How can I assist you today, Mr. Prabhakar?")
        
        while self.is_running:
            cmd = await self.listen()
            if not cmd: 
                continue

            # Wake word filter
            for word in ["jay", "hey jay", "hello jay"]:
                cmd = cmd.replace(word, "").strip()

            # MAIL COMMANDS
            if ("mail" in cmd or "email" in cmd) and len(cmd) < 50:
                if "check" in cmd or "read" in cmd:
                    status = await self.mail.check_inbox()
                    self.voice.speak(status)
                
                elif "send" in cmd:
                    self.voice.speak("Who is the recipient, sir?")
                    name = (await self.listen()).lower()
                    
                    # Contact Lookup
                    recipient = self.contacts.get(name)
                    if not recipient:
                        self.voice.speak(f"Contact {name} not found. Defaulting to voice-to-mail.")
                        recipient = name.replace(" ", "") + "@gmail.com"
                    else:
                        self.voice.speak(f"Accessing records for {name}.")
                    
                    self.voice.speak(f"What is the subject of this transmission?")
                    subject = await self.listen()
                    
                    self.voice.speak("And the message content?")
                    body = await self.listen()
                    
                    res = await self.mail.send(recipient, subject, body)
                    self.voice.speak(res)

            # WEB NAVIGATION & SEARCH
            elif "google search" in cmd or "search google" in cmd:
                query = cmd.replace("google search", "").replace("search google", "").replace("for", "").strip()
                self.voice.speak(f"Searching the web for {query}, sir.")
                await asyncio.to_thread(webbrowser.open, f"https://www.google.com/search?q={query}")

            elif "stack overflow" in cmd:
                query = cmd.replace("stack overflow", "").replace("search", "").strip()
                self.voice.speak(f"Checking Stack Overflow for {query}, sir.")
                await asyncio.to_thread(webbrowser.open, f"https://stackoverflow.com/search?q={query}")

            elif "github" in cmd:
                repo = cmd.replace("github", "").replace("search", "").strip()
                self.voice.speak(f"Searching GitHub repositories for {repo}.")
                await asyncio.to_thread(webbrowser.open, f"https://github.com/search?q={repo}")

            elif "play" in cmd and "spotify" in cmd:
                song = cmd.replace("play", "").replace("on spotify", "").strip()
                self.voice.speak(f"Queuing {song} on Spotify, sir.")
                await asyncio.to_thread(webbrowser.open, f"spotify:search:{song}")

            elif "play" in cmd and "youtube" in cmd:
                video = cmd.replace("play", "").replace("on youtube", "").strip()
                self.voice.speak(f"Opening {video} on YouTube, sir.")
                await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/results?search_query={video}")

            elif "open" in cmd and ("whatsapp" in cmd or "wa" in cmd):
                self.voice.speak("Opening WhatsApp Web, sir.")
                await asyncio.to_thread(webbrowser.open, "https://web.whatsapp.com")

            elif "open" in cmd and "gmail" in cmd:
                self.voice.speak("Opening your inbox, sir.")
                await asyncio.to_thread(webbrowser.open, "https://mail.google.com")

            # LOCAL APPLICATION LAUNCH
            elif "open notepad" in cmd:
                self.voice.speak("Launching Notepad, sir.")
                await asyncio.to_thread(subprocess.Popen, ["notepad.exe"])

            elif "open calculator" in cmd:
                self.voice.speak("Opening Calculator, sir.")
                await asyncio.to_thread(subprocess.Popen, ["calc.exe"])

            elif "close" in cmd:
                app = cmd.replace("close", "").strip()
                self.voice.speak(f"Terminating {app} process, sir.")
                if "notepad" in app: os.system("taskkill /f /im notepad.exe")
                elif "calculator" in app: os.system("taskkill /f /im calc.exe")
                elif "chrome" in app: os.system("taskkill /f /im chrome.exe")
                else:
                    self.voice.speak("I am not authorized to terminate that specific process.")

            elif "clipboard" in cmd:
                if "read" in cmd or "what" in cmd:
                    text = await asyncio.to_thread(pyperclip.paste)
                    self.voice.speak(f"The clipboard contains: {text}")
                elif "clear" in cmd:
                    await asyncio.to_thread(pyperclip.copy, "")
                    self.voice.speak("Clipboard has been cleared, sir.")

            elif "news" in cmd:
                self.voice.speak("Fetching the latest headlines for you, sir.")
                await asyncio.to_thread(webbrowser.open, "https://news.google.com")

            # INFORMATION RETRIEVAL
            elif "wikipedia" in cmd:
                topic = cmd.replace("wikipedia", "").strip()
                try:
                    summary = await asyncio.to_thread(wikipedia.summary, topic, sentences=2)
                    self.voice.speak(summary)
                except Exception:
                    self.voice.speak("My apologies, sir. The archives are unresponsive on that specific topic.")

            elif "joke" in cmd:
                joke = await asyncio.to_thread(pyjokes.get_joke)
                self.voice.speak(joke)

            # TIME COMMAND
            elif "time" in cmd:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.voice.speak(f"The current time is {current_time}, sir.")

            # SYSTEM CONTROLS
            elif "volume up" in cmd:
                await asyncio.to_thread(pyautogui.press, "volumeup", presses=5)
                self.voice.speak("Volume increased, sir.")

            elif "volume down" in cmd:
                await asyncio.to_thread(pyautogui.press, "volumedown", presses=5)
                self.voice.speak("Volume decreased, sir.")

            elif "mute" in cmd:
                await asyncio.to_thread(pyautogui.press, "volumemute")
                self.voice.speak("System muted, sir.")

            elif "screenshot" in cmd:
                filename = f"jay_snap_{int(time.time())}.png"
                await asyncio.to_thread(pyautogui.screenshot, filename)
                self.voice.speak("Screenshot captured and saved to your directory, sir.")

            # SYSTEM COMMANDS
            elif "status" in cmd:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.voice.speak(f"All systems are nominal, sir. CPU is at {cpu} percent, and RAM usage is at {ram} percent.")

            elif "ip address" in cmd or "network" in cmd:
                try:
                    ip = await asyncio.to_thread(lambda: requests.get('https://api.ipify.org').text)
                    self.voice.speak(f"Your public IP address is {ip}, sir.")
                except Exception:
                    self.voice.speak("I'm unable to ping the external network, sir.")

            elif "go to sleep" in cmd or "shutdown" in cmd:
                self.voice.speak("As you wish. Powering down systems. Goodbye, sir.")
                self.is_running = False

            # AI BRAIN FALLBACK
            elif len(cmd) > 3:
                response = await self.ai_brain(cmd)
                self.voice.speak(response)

# --- 4. EXECUTION ---
if __name__ == "__main__":
    assistant = JayAssistant()
    try:
        asyncio.run(assistant.run())
    except KeyboardInterrupt:
        pass
