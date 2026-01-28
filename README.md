# AI Learning Game

**COSC 5360 - Artificial Intelligence | Spring 2026**  
**Tarleton State University** - Member of The Texas A&M University System

---

## Overview

An interactive, gamified learning application designed for the COSC 5360 Artificial Intelligence course. Master AI concepts through engaging quizzes, interactive visualizations, and a rewarding progression system.

**Built with evidence-based learning science:**
- BJ Fogg's B=MAP Model (Behavior = Motivation + Ability + Prompt)
- Self-Determination Theory (Autonomy, Competence, Relatedness)
- Spaced Repetition for long-term memory
- Retrieval Practice ("Testing Effect") for enhanced learning

---

## Quick Start

### Option 1: Run the Executable (Recommended)

1. Download `AI_Learning_Game.exe` and `TSU.png`
2. Place both files in the same folder
3. Double-click `AI_Learning_Game.exe`

**No Python installation required!**

### Option 2: Run from Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python ai_learning_app.py
```

### Option 3: Build Your Own Executable

```bash
# Windows
build_executable.bat

# Or manually:
pip install -r requirements.txt
python -m PyInstaller --onefile --windowed --name "AI_Learning_Game" --add-data "TSU.png;." ai_learning_app.py
```

The executable will be created in the `dist` folder.

---

## Features

### Dashboard
- **Daily Challenge** - Quick 2-3 minute practice to maintain streaks
- **Exam Readiness Indicator** - See your overall preparedness at a glance
- **Smart Recommendations** - Review Due, Weak Area Booster
- **Reduced Decision Fatigue** - Clear next steps for optimal learning

### Learning Content
- **10 Course Topics** covering all aspects of AI and Machine Learning
- **100+ Quiz Questions** with at least 10 questions per topic
- **Comprehensive Study Materials** for each topic
- **Interactive Algorithm Visualizations**
- **Enhanced Feedback** - Explanations for correct answers

### Gamification
- **XP & Leveling System** - Earn experience points and level up
- **Daily Streaks** - Track study habits with streak freezes
- **Daily/Weekly Quests** - Targeted challenges tied to course objectives
- **Achievements & Unlockables** - Unlock Hard Mode, Exam Simulator, Case Studies
- **Personal Bests Leaderboard** - Track your own records
- **Class Leaderboard** - Multiple categories with privacy controls

### Smart Learning System
- **Per-Question Memory Tracking** - Smarter spaced repetition
- **Confidence Ratings** - Low confidence answers still get reviewed
- **Adaptive Difficulty** - Questions adjust based on your accuracy
- **Review Queue** - Add difficult questions for targeted practice
- **Skills Map** - Visual mastery growth tracking

### Quiz Modes
- **Daily Challenge** - Quick 2-3 minute mixed practice
- **Random Quiz** - Test overall knowledge
- **Interleaved Quiz** - Mixed topics for deeper learning
- **Time Attack** - 2 or 5 minute speed challenges
- **Short Answer Mode** - Advanced learners, no multiple choice
- **Weak Area Drill** - Adaptive practice on struggling topics

### Interactive Tools
- **Neural Network Builder** - Drag-and-drop network architecture
- **Algorithm Visualizations** - Decision Trees, K-Means, Gradient Descent
- **Spaced Repetition** - Smart review scheduling

---

## Course Topics

1. Introduction to AI and Applications
2. Probability, Linear Algebra, and Optimization
3. Regression Methods in ML
4. Classification Algorithms
5. Clustering and Unsupervised Learning
6. Neural Networks and Model Evaluation
7. Practical AI and ML Applications
8. Dimensionality Reduction and Model Selection
9. Markov Decision Process and Reinforcement Learning
10. Exam Review and Recitation

---

## Files

| File | Description |
|------|-------------|
| `ai_learning_app.py` | Main application source code |
| `TSU.png` | Tarleton State University logo |
| `requirements.txt` | Python dependencies |
| `build_executable.bat` | Windows build script |
| `AI_Learning_Game.exe` | Pre-built portable executable |

---

## Requirements

**For running from source:**
- Python 3.7 or higher
- Pillow (for logo support)

**For the executable:**
- Windows 10/11
- No additional requirements

---

## Tips for Success

1. **Daily Practice** - Maintain your streak for bonus XP
2. **Study First** - Review materials before quizzes
3. **Review Mistakes** - Learn from incorrect answers
4. **Use Visualizations** - Interactive tools help understanding
5. **Follow Spaced Repetition** - Review when prompted

---

## Achievement Examples

- **Perfect Score** - Get 100% on a quiz
- **Excellent Performance** - Score 90%+ on a quiz
- **7 Day Streak** - Study 7 days in a row
- **Century Club** - Answer 100 questions
- **Topic Mastery** - Complete a topic's study material

---

## Instructor

**Dr. Mohamed Massaoudi**  
Email: MMASSAOUDI@tarleton.edu

---

## License

This application is for educational use in COSC 5360 at Tarleton State University.

---

**Good luck with your AI studies!**

*COSC 5360 - Artificial Intelligence | Spring 2026*
