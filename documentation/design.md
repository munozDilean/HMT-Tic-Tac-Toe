# Design Documentation

This project is a web application for the popular game Tic-tac-toe with a
chatbot assistant that can aid the user on the moves to play. The chatbot will be actively giving advice to the user according to set number of metrics that will be taken. This project will have a focus on Human Machine Teaming framwork.

## Tech Stack
* Framework: DJango
* AI-Model: Ollama
* Docker

## Project Aim

Building a chatbot 

## Background

## Alignment with HMT Framework
> _**Note:**_ Keep in mind that all pre-survey questions will be on Qualtrix

## Flow of the Project
1. Pre-survey (experience): Scale 1-5
2. Experience
3. Baseline frustration
4. On second treatment don’t ask again but as #2
5. Pre-survey
6. Do the task
7. Treatment 1: Random Game Advice
8. Post-survey questions
9. Two questions
10. FDS and SUS and TLX
11. For Treatment 2 (Nuance) start from #2 and repeat

### Possible Alternative


#### 🎯 **1. Welcome / Onboarding**
- Brief intro: *“Play Tic-tac-toe with a smart assistant that helps you improve!”*
- Optional: Quick tutorial on how the chatbot gives advice (e.g., “It will suggest moves based on strategy, not just winning”).
- Consent: “We’ll ask you a few short questions after each game to improve the experience.”

---

#### 🎮 **2. Game Start**
- User chooses:
  - **Player vs. Bot** (chatbot plays opponent)
  - **Player + Bot** (chatbot assists user as teammate)
  - *(Optional: Difficulty level or strategy focus — e.g., “Defensive”, “Aggressive”, “Learning Mode”)*
- Board appears. Chatbot introduces itself: *“I’ll suggest moves to help you learn. You can ignore or follow them.”*

---

#### 🤖 **3. During Game — Chatbot Interaction**
- After each user move, chatbot responds with:
  - **Advice**: *“Good move! Consider blocking here next.”*
  - **Strategy tip**: *“In this position, controlling the center is key.”*
  - **Encouragement**: *“You’re setting up a fork — nice!”*
- User can:
  - Accept suggestion (click to place move)
  - Ignore (make own move)
  - Ask for clarification: *“Why that move?”*

> *HMT Principle: Chatbot acts as a teammate — not a controller — offering guidance, not commands.*

---

#### 📝 **4. After Each Game — Feedback Loop**
*(Triggered automatically after game ends)*

##### ➤ **SEQ** (Single Ease Question)
> *“How easy or difficult was this game?”*  
> *(1 = Very Difficult → 7 = Very Easy)*

##### ➤ **NASA-TLX** (Task Load Index)
> Rate 6 dimensions (0–20 scale):
> - Mental Demand, Physical Demand, Temporal Demand, Performance, Effort, Frustration

##### ➤ **HMT-Specific Questions** (Optional, 1–5 scale)
> - “The chatbot’s advice helped me make better moves.”  
> - “I felt like I was collaborating with the chatbot.”  
> - “The chatbot’s timing was helpful.”

---

#### 📊 **5. End of Session — Final Feedback**
*(After 3–5 games, or user chooses to stop)*

##### ➤ **SUS** (System Usability Scale)
> 10 questions (1–5 scale) — e.g., *“I found the application easy to use.”*

##### ➤ Optional: Open-ended
> *“What did you like most about the chatbot? What could be improved?”*

---

#### 🔄 **6. Optional: Replay / Learn Mode**
- User can replay games with chatbot commentary.
- View stats: “You followed 70% of suggestions”, “Your win rate improved from 40% to 65%”.

---

#### 🧩 HMT Design Notes
- **Shared Awareness**: Chatbot explains *why* it suggests a move (not just “play here”).
- **Mutual Trust**: User can override suggestions — no forced compliance.
- **Adaptability**: Chatbot adjusts advice based on user skill (if tracked).
- **Feedback Integration**: Post-game questions inform future chatbot behavior.
