# 👗 Tech Threads: Fashion Trend Analyzer

## Project Overview

Tech Threads is a full stack fashion trend analyzer that evaluates the trendiness of an outfit. It takes into consideration, mood, event and weather of location based on the given user’s inputs, which is matched and compared to Google trends data in real time. It returns a match percentage and detailed summary to the user which can also be emailed to their respective ids. It’s objective is to check how trendy a user’s outfit is helping users be more fashion and trend aware.

---

## 🧠 Features

1.Live outfit trend matching using Google Trends (pytrends module)

2.Real time weather/temperature for user’s inputted location is retrieved/accessed from the Open Weather API

3.Used Open Cage Data API, to find geocodes of user’s location(geocodeing) that was used to access real time Google trends data in given country using pytrends Module

4.Outfit match percentage calculated based on trending queries in the Google Search engine

5.Tkinter GUI, for visual user interface

6.Email summaries sent to given user’s email id, using smtplib module accesing it’s gmail server

7.Saves data in SQLite3 Database

8.Tracks highest match combination, which user’s can view, helping them effectively select their outfits

---

## 🚀 How It Works

1.User selects their mood, event, outfit components (top/bottom/dress/etc.).

2.System fetches temperature using weather API.

3.Uses this and user input to generate fashion trend keywords.

4.Queries Google Trends for popularity of related keywords.

5.Compares user outfit components with trend data and calculates a match %.

6.Displays the result and allows the user to email a summary.

7.Option to check highest match combo so far.

---

## 🛠️ Tech Stack

1.Frontend: Tkinter(Python GUI library)
2.Backend: Python
3.APIs: OpenWeather, Pytrends, OpenCage 
4.Database: SQLite3
5.Email: SMTP with Gmail APP password
6.Version + Ctrl: Git +Github

---

## 📁 Project Structure

```bash
techthreadsfinal.py      # Main application file (GUI + backend logic)
TECH THREADS.docx        # Full project documentation (design + logic)
README.md                # Project summary for GitHub
```

---

## 📩 Email Integration

Emails are sent using Gmail’s SMTP server. For this to work securely:

- Enable **App Passwords** in your Gmail account settings.
- Store the app password in your code securely (not hardcoded for production).

---

## ✅ Status

✅ Fully Functional  
🎨 Final Design Completed  
📧 Email Integration Working  
📊 Trend Analysis Tested

---

## 📌 Author Notes

- This was my **first full-stack project**, integrating GUI, databases, APIs, and external services.
- Built after completing Year 1 of college, aiming to gain real-world experience and explore applied Python.

---

## 📜 License

This project is for **educational and personal portfolio** use.  
Contact the author for collaboration or deployment rights.
