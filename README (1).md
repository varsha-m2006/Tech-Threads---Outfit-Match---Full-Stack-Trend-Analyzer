# 👗 Tech Threads: Fashion Trend Analyzer

**Tech Threads** is a full-stack fashion trend analyzer that evaluates how trendy a user's outfit is by comparing it with real-time Google Trends data. Designed to promote fashion awareness, the system helps users determine how well their outfit aligns with current fashion trends based on mood, event, and weather.

---

## 🧠 Features

- **Smart Outfit Matching:**  
  Matches user outfit details (top, bottom, color, fabric, etc.) with trending keywords from Google Trends.

- **Real-time Trend Analysis:**  
  Uses PyTrends to fetch the latest fashion-related data based on geographic location and user mood/event.

- **Match Percentage Score:**  
  Calculates how closely the user’s outfit matches trending fashion data.

- **Email Summary Option:**  
  Automatically sends the trend match summary to the user's email address.

- **User-friendly GUI:**  
  Built using Tkinter with a clean layout, color themes, and interactive buttons.

---

## 🚀 How It Works

1. **User Inputs:**  
   Users select their outfit details along with their current mood, event, and location (temperature retrieved using weather APIs).

2. **Keyword Generation:**  
   A set of search keywords is generated from the inputs.

3. **Trend Fetching:**  
   Keywords are used to pull current trend data and related queries from Google Trends.

4. **Match Calculation:**  
   Outfit keywords are compared with trending terms using intelligent loose-matching logic.

5. **Result Display:**  
   A match percentage is displayed in the GUI, along with the matched terms. Users can optionally receive the result via email.

---

## 🛠️ Tech Stack

- **Frontend:** Tkinter (Python GUI)
- **Backend:** SQLite (for user data), PyTrends (Google Trends API), smtplib (Email Service), OpenWeatherMap API
- **Language:** Python 3
- **Environment:** Desktop application

---

## 📁 Project Structure

```bash
techthreadsfinal.py      # Main application file (GUI + backend logic)
TECH THREADS.docx        # Full project documentation (design + logic)
README.md                # Project summary for GitHub
```

---

## 📷 Screenshots

> _Optional: You can add images of the interface here using_  
> `![Screenshot](path/to/image.png)`

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