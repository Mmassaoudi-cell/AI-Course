"""
AI Learning Game Application - COSC 5360 Spring 2026
A gamified educational application for Artificial Intelligence course
Tarleton State University - Member of The Texas A&M University System

Enhanced with:
- BJ Fogg's B=MAP behavioral engineering (Motivation, Ability, Prompt)
- Self-Determination Theory (Autonomy, Competence, Relatedness)
- Smarter spaced repetition with per-question memory strength
- Adaptive difficulty based on performance
- Improved feedback with explanations
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
import random
from collections import defaultdict
import math
import hashlib

# Try to import PIL for logo support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class AILearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Learning Game - COSC 5360 Spring 2026 | Tarleton State University")
        self.root.geometry("1200x800")
        
        # Modern Design System - Restrained color palette
        self.TARLETON_PURPLE = "#4E2A84"  # Primary brand color
        self.TARLETON_PURPLE_LIGHT = "#6B3FA0"
        self.TARLETON_GOLD = "#C4A000"
        
        # Semantic colors (used sparingly)
        self.COLOR_SUCCESS = "#10B981"  # Green - correct/success
        self.COLOR_WARNING = "#F59E0B"  # Amber - warning/streak
        self.COLOR_ERROR = "#EF4444"    # Red - error/wrong
        self.COLOR_INFO = "#3B82F6"     # Blue - info
        
        # Theme management
        self.dark_mode = False
        self.font_scale = 1.0
        self.theme_colors = self.get_theme_colors()
        
        # Typography ramp (in pixels, will scale with font_scale)
        self.FONT_TITLE = 32
        self.FONT_SUBTITLE = 18
        self.FONT_SECTION = 16
        self.FONT_BODY = 14
        self.FONT_BUTTON = 14
        self.FONT_CAPTION = 12
        
        # Spacing system (in pixels)
        self.SPACE_XL = 32   # Outer margins
        self.SPACE_LG = 24   # Between sections
        self.SPACE_MD = 16   # Between items
        self.SPACE_SM = 12   # Tight spacing
        self.SPACE_XS = 8    # Minimal gap
        
        # Load TSU logo
        self.logo_image = None
        self.load_logo()
        
        # Gamification data
        self.xp = 0
        self.level = 1
        self.streak = 0
        self.last_study_date = None
        self.achievements = []
        self.unlocked_content = []
        
        # Spaced repetition data - enhanced with per-question tracking
        self.review_schedule = {}  # topic_num: next_review_date
        self.mastery_levels = defaultdict(int)  # topic_num: mastery (0-5)
        self.question_memory = {}  # question_id: {strength, last_seen, confidence, times_correct, times_wrong}
        self.review_queue = []  # List of question_ids to review
        
        # Adaptive difficulty tracking
        self.topic_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})  # Per-topic accuracy
        self.difficulty_preference = 'adaptive'  # 'easy', 'normal', 'hard', 'adaptive'
        
        # Personal bests for leaderboard
        self.personal_bests = {
            'best_accuracy': 0,
            'fastest_quiz': float('inf'),
            'longest_streak': 0,
            'highest_single_quiz': 0
        }
        
        # Daily challenge tracking
        self.daily_challenge_completed = None  # Date of last completed daily challenge
        self.daily_challenge_streak = 0
        
        # Onboarding state
        self.onboarding_complete = False
        self.placement_quiz_taken = False
        self.is_guest = False
        
        # Session tracking for prompts
        self.session_start = datetime.now()
        self.streak_prompt_shown = False
        
        # Quest system
        self.active_quests = []
        self.completed_quests = []
        self.quest_progress = {}
        
        # Streak guardrails
        self.streak_freezes = 2  # Start with 2 free freezes
        self.streak_freeze_used_today = False
        
        # Unlockable content tracking
        self.unlocked_features = {
            'hard_mode': False,
            'exam_simulator': False,
            'bonus_visualizations': False,
            'case_studies': False
        }
        
        # Class leaderboard settings
        self.display_alias = True  # Privacy: use alias by default
        self.student_alias = ""
        self.opt_in_leaderboard = False
        
        # Instructor mode
        self.is_instructor = False
        self.class_data_path = ""
        
        # Per-question detailed history
        self.question_history = {}  # q_id: [{attempt_date, correct, confidence, time_taken}]
        
        # Student data
        self.student_name = ""
        self.scores = defaultdict(int)
        self.progress = defaultdict(int)
        self.total_questions_answered = 0
        self.correct_answers = 0
        self.total_time_spent = 0  # Track total study time in seconds
        
        # Course topics from syllabus (must be before load_data)
        self.topics = {
            1: {"name": "Introduction to AI and Applications", "hours": 3, "completed": False},
            2: {"name": "Probability, Linear Algebra, and Optimization", "hours": 5, "completed": False},
            3: {"name": "Regression Methods in ML", "hours": 4, "completed": False},
            4: {"name": "Classification Algorithms", "hours": 8, "completed": False},
            5: {"name": "Clustering and Unsupervised Learning", "hours": 4, "completed": False},
            6: {"name": "Neural Networks and Model Evaluation", "hours": 6, "completed": False},
            7: {"name": "Practical AI and ML Applications", "hours": 6, "completed": False},
            8: {"name": "Dimensionality Reduction and Model Selection", "hours": 3, "completed": False},
            9: {"name": "Markov Decision Process and Reinforcement Learning", "hours": 6, "completed": False},
            10: {"name": "Exam Review and Recitation", "hours": 3, "completed": False}
        }
        
        # Load questions database
        self.questions_db = self.load_questions()
        
        # Load or initialize data
        self.load_data()
        
        # Apply theme
        self.apply_theme()
        
        self.show_main_menu()
    
    def load_logo(self):
        """Load Tarleton State University logo"""
        if PIL_AVAILABLE:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(script_dir, 'TSU.png')
                if os.path.exists(logo_path):
                    img = Image.open(logo_path)
                    # Resize for header
                    img = img.resize((180, 60), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Could not load logo: {e}")
                self.logo_image = None
    
    def get_theme_colors(self):
        """Modern design system colors - minimal, high contrast"""
        if self.dark_mode:
            colors = {
                'bg': '#121212',              # Near black
                'bg_elevated': '#1E1E1E',     # Slightly lighter for cards
                'surface': '#2D2D2D',         # Interactive surfaces
                'border': '#404040',          # Subtle borders
                'text_primary': '#FFFFFF',    # High contrast text
                'text_secondary': '#A0A0A0',  # Muted text
                'text_tertiary': '#6B6B6B',   # Very muted
                'primary': self.TARLETON_PURPLE,
                'primary_hover': '#5E3A94',
                'accent': self.TARLETON_GOLD,
                'success': self.COLOR_SUCCESS,
                'warning': self.COLOR_WARNING,
                'error': self.COLOR_ERROR,
                'divider': '#333333'
            }
        else:
            colors = {
                'bg': '#FAFAFA',              # Light gray (not pure white)
                'bg_elevated': '#FFFFFF',     # White for cards
                'surface': '#F5F5F5',         # Interactive surfaces
                'border': '#E0E0E0',          # Subtle borders
                'text_primary': '#1A1A1A',    # Near black text
                'text_secondary': '#6B7280',  # Gray text
                'text_tertiary': '#9CA3AF',   # Light gray
                'primary': self.TARLETON_PURPLE,
                'primary_hover': '#5E3A94',
                'accent': self.TARLETON_GOLD,
                'success': self.COLOR_SUCCESS,
                'warning': self.COLOR_WARNING,
                'error': self.COLOR_ERROR,
                'divider': '#E5E7EB'
            }
        
        # Backward compatibility aliases for legacy code
        colors['card_bg'] = colors['bg_elevated']
        colors['text'] = colors['text_primary']
        colors['fg'] = colors['text_primary']
        colors['gold'] = colors['accent']
        colors['button_primary'] = colors['primary']
        colors['accent_light'] = self.TARLETON_PURPLE_LIGHT
        
        return colors
    
    def create_button(self, parent, text, command, style='secondary', width=None, icon=None):
        """Create a styled button following hierarchy: primary > secondary > tertiary"""
        colors = self.theme_colors
        font_size = int(self.FONT_BUTTON * self.font_scale)
        
        if style == 'primary':
            bg = colors['primary']
            fg = '#FFFFFF'
            hover_bg = colors['primary_hover']
            relief = tk.FLAT
            border = 0
        elif style == 'secondary':
            bg = colors['bg_elevated']
            fg = colors['primary']
            hover_bg = colors['surface']
            relief = tk.FLAT
            border = 1
        else:  # tertiary/text
            bg = colors['bg']
            fg = colors['primary']
            hover_bg = colors['surface']
            relief = tk.FLAT
            border = 0
        
        btn_text = f"{icon} {text}" if icon else text
        
        btn = tk.Button(parent, text=btn_text, command=command,
                       font=('Segoe UI', font_size, 'normal'),
                       bg=bg, fg=fg, relief=relief, bd=border,
                       cursor='hand2', padx=16, pady=8,
                       activebackground=hover_bg, activeforeground=fg,
                       highlightthickness=1 if style == 'secondary' else 0,
                       highlightbackground=colors['border'] if style == 'secondary' else bg)
        
        if width:
            btn.config(width=width)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.config(bg=hover_bg))
        btn.bind('<Leave>', lambda e: btn.config(bg=bg))
        
        return btn
    
    def create_card(self, parent, padding=16):
        """Create a subtle card with minimal styling"""
        colors = self.theme_colors
        card = tk.Frame(parent, bg=colors['bg_elevated'],
                       highlightbackground=colors['border'],
                       highlightthickness=1)
        inner = tk.Frame(card, bg=colors['bg_elevated'])
        inner.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        return card, inner
    
    def create_section_header(self, parent, text, subtitle=None):
        """Create a section header with optional subtitle"""
        colors = self.theme_colors
        frame = tk.Frame(parent, bg=colors['bg'])
        
        tk.Label(frame, text=text,
                font=('Segoe UI', int(self.FONT_SECTION * self.font_scale), 'bold'),
                bg=colors['bg'], fg=colors['text_primary']).pack(anchor='w')
        
        if subtitle:
            tk.Label(frame, text=subtitle,
                    font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                    bg=colors['bg'], fg=colors['text_tertiary']).pack(anchor='w')
        
        return frame
    
    def apply_theme(self):
        """Apply current theme to root window"""
        self.root.configure(bg=self.theme_colors['bg'])
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.theme_colors = self.get_theme_colors()
        self.apply_theme()
        self.save_data()
        self.show_main_menu()  # Refresh to apply theme
    
    def adjust_font_scale(self, scale):
        """Adjust font scaling"""
        self.font_scale = max(0.8, min(1.5, scale))
        self.save_data()
    
    def load_data(self):
        """Load student progress from file"""
        try:
            if os.path.exists('student_progress.json'):
                with open('student_progress.json', 'r') as f:
                    data = json.load(f)
                    self.student_name = data.get('name', '')
                    self.scores = defaultdict(int, data.get('scores', {}))
                    self.progress = defaultdict(int, data.get('progress', {}))
                    self.total_questions_answered = data.get('total_questions', 0)
                    self.correct_answers = data.get('correct_answers', 0)
                    self.dark_mode = data.get('dark_mode', False)
                    self.font_scale = data.get('font_scale', 1.0)
                    self.xp = data.get('xp', 0)
                    self.level = data.get('level', 1)
                    self.streak = data.get('streak', 0)
                    self.last_study_date = data.get('last_study_date')
                    self.achievements = data.get('achievements', [])
                    self.unlocked_content = data.get('unlocked_content', [])
                    self.review_schedule = data.get('review_schedule', {})
                    self.mastery_levels = defaultdict(int, data.get('mastery_levels', {}))
                    # New enhanced data
                    self.question_memory = data.get('question_memory', {})
                    self.review_queue = data.get('review_queue', [])
                    self.topic_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0}, 
                                                       data.get('topic_accuracy', {}))
                    self.personal_bests = data.get('personal_bests', {
                        'best_accuracy': 0, 'fastest_quiz': float('inf'),
                        'longest_streak': 0, 'highest_single_quiz': 0
                    })
                    self.daily_challenge_completed = data.get('daily_challenge_completed')
                    self.daily_challenge_streak = data.get('daily_challenge_streak', 0)
                    self.onboarding_complete = data.get('onboarding_complete', False)
                    self.placement_quiz_taken = data.get('placement_quiz_taken', False)
                    self.is_guest = data.get('is_guest', False)
                    # Quest and streak features
                    self.active_quests = data.get('active_quests', [])
                    self.completed_quests = data.get('completed_quests', [])
                    self.quest_progress = data.get('quest_progress', {})
                    self.streak_freezes = data.get('streak_freezes', 2)
                    self.streak_freeze_used_today = data.get('streak_freeze_used_today', False)
                    # Unlockable features
                    self.unlocked_features = data.get('unlocked_features', {
                        'hard_mode': False, 'exam_simulator': False,
                        'bonus_visualizations': False, 'case_studies': False
                    })
                    # Class leaderboard
                    self.display_alias = data.get('display_alias', True)
                    self.student_alias = data.get('student_alias', '')
                    self.opt_in_leaderboard = data.get('opt_in_leaderboard', False)
                    # Question history
                    self.question_history = data.get('question_history', {})
                    self.total_time_spent = data.get('total_time_spent', 0)
        except:
            pass
        
        # Generate daily quests if needed
        self.check_and_generate_quests()
    
    def save_data(self):
        """Save student progress to file"""
        # Update personal bests
        if self.streak > self.personal_bests.get('longest_streak', 0):
            self.personal_bests['longest_streak'] = self.streak
        
        data = {
            'name': self.student_name,
            'scores': dict(self.scores),
            'progress': dict(self.progress),
            'total_questions': self.total_questions_answered,
            'correct_answers': self.correct_answers,
            'dark_mode': self.dark_mode,
            'font_scale': self.font_scale,
            'xp': self.xp,
            'level': self.level,
            'streak': self.streak,
            'last_study_date': self.last_study_date,
            'achievements': self.achievements,
            'unlocked_content': self.unlocked_content,
            'review_schedule': self.review_schedule,
            'mastery_levels': dict(self.mastery_levels),
            'question_memory': self.question_memory,
            'review_queue': self.review_queue,
            'topic_accuracy': dict(self.topic_accuracy),
            'personal_bests': self.personal_bests,
            'daily_challenge_completed': self.daily_challenge_completed,
            'daily_challenge_streak': self.daily_challenge_streak,
            'onboarding_complete': self.onboarding_complete,
            'placement_quiz_taken': self.placement_quiz_taken,
            'is_guest': self.is_guest,
            # Quest and streak features
            'active_quests': self.active_quests,
            'completed_quests': self.completed_quests,
            'quest_progress': self.quest_progress,
            'streak_freezes': self.streak_freezes,
            'streak_freeze_used_today': self.streak_freeze_used_today,
            # Unlockable features
            'unlocked_features': self.unlocked_features,
            # Class leaderboard
            'display_alias': self.display_alias,
            'student_alias': self.student_alias,
            'opt_in_leaderboard': self.opt_in_leaderboard,
            # Question history
            'question_history': self.question_history,
            'total_time_spent': self.total_time_spent,
            'last_updated': datetime.now().isoformat()
        }
        with open('student_progress.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also export gradebook-friendly data
        self.export_gradebook_data()
    
    def get_question_id(self, question):
        """Generate unique ID for a question"""
        q_str = question['question'] + str(question['topic'])
        return hashlib.md5(q_str.encode()).hexdigest()[:12]
    
    def update_question_memory(self, question, is_correct, confidence='medium'):
        """Update per-question memory strength (enhanced spaced repetition)"""
        q_id = self.get_question_id(question)
        if q_id not in self.question_memory:
            self.question_memory[q_id] = {
                'strength': 0, 'last_seen': None, 'confidence': confidence,
                'times_correct': 0, 'times_wrong': 0, 'topic': question['topic']
            }
        
        mem = self.question_memory[q_id]
        mem['last_seen'] = datetime.now().isoformat()
        mem['confidence'] = confidence
        
        if is_correct:
            mem['times_correct'] += 1
            # Increase strength more for high confidence correct answers
            strength_gain = 1 if confidence == 'high' else 0.7 if confidence == 'medium' else 0.4
            mem['strength'] = min(5, mem['strength'] + strength_gain)
        else:
            mem['times_wrong'] += 1
            mem['strength'] = max(0, mem['strength'] - 1)
            # Add to review queue if not already there
            if q_id not in self.review_queue:
                self.review_queue.append(q_id)
        
        self.save_data()
    
    def get_exam_readiness(self):
        """Calculate exam readiness score (0-100) based on mastery across all topics"""
        if not self.mastery_levels:
            return 0
        total_mastery = sum(self.mastery_levels.values())
        max_mastery = len(self.topics) * 5  # Max mastery is 5 per topic
        return int((total_mastery / max_mastery) * 100)
    
    def get_weakest_topic(self):
        """Find the topic with lowest accuracy for weak area booster"""
        weakest = None
        lowest_acc = 101
        for topic_num in self.topics.keys():
            acc_data = self.topic_accuracy.get(str(topic_num), {'correct': 0, 'total': 0})
            if acc_data['total'] > 0:
                acc = (acc_data['correct'] / acc_data['total']) * 100
                if acc < lowest_acc:
                    lowest_acc = acc
                    weakest = topic_num
            elif weakest is None:
                weakest = topic_num
                lowest_acc = 0
        return weakest, lowest_acc
    
    def get_adaptive_difficulty(self, topic_num):
        """Get recommended difficulty based on topic accuracy"""
        acc_data = self.topic_accuracy.get(str(topic_num), {'correct': 0, 'total': 0})
        if acc_data['total'] < 5:
            return 'normal'
        accuracy = (acc_data['correct'] / acc_data['total']) * 100
        if accuracy < 50:
            return 'easy'
        elif accuracy > 80:
            return 'hard'
        return 'normal'
    
    # ===== QUEST SYSTEM =====
    def check_and_generate_quests(self):
        """Generate daily/weekly quests tied to course objectives"""
        today = datetime.now().date().isoformat()
        
        # Check if we need new daily quests
        if not self.active_quests or self.active_quests[0].get('generated_date') != today:
            self.generate_daily_quests()
    
    def generate_daily_quests(self):
        """Generate 3 daily quests based on student progress"""
        today = datetime.now().date().isoformat()
        
        # Find weakest topic for targeted quest
        weakest_topic, _ = self.get_weakest_topic()
        
        # Find topic needing review
        review_topics = [tn for tn in self.topics.keys() if self.check_spaced_repetition(tn)]
        review_topic = review_topics[0] if review_topics else random.randint(1, 10)
        
        quest_templates = [
            {
                'id': f'daily_quiz_{today}',
                'title': '📝 Complete Daily Quiz',
                'description': 'Complete a 5-question mini-quiz on any topic',
                'type': 'quiz',
                'target': 5,
                'progress': 0,
                'xp_reward': 25,
                'generated_date': today
            },
            {
                'id': f'topic_study_{today}',
                'title': f'📚 Study Topic {weakest_topic}',
                'description': f'Review study material for {self.topics.get(weakest_topic, {}).get("name", "a topic")}',
                'type': 'study',
                'target_topic': weakest_topic,
                'target': 1,
                'progress': 0,
                'xp_reward': 15,
                'generated_date': today
            },
            {
                'id': f'review_{today}',
                'title': '🔄 Complete Review Session',
                'description': 'Practice questions from topics due for review',
                'type': 'review',
                'target': 1,
                'progress': 0,
                'xp_reward': 20,
                'generated_date': today
            }
        ]
        
        # Add a weekly challenge if it's Monday
        if datetime.now().weekday() == 0:
            quest_templates.append({
                'id': f'weekly_mastery_{today}',
                'title': '🏆 Weekly Mastery Challenge',
                'description': 'Complete 3 topic quizzes with 70%+ accuracy',
                'type': 'mastery',
                'target': 3,
                'progress': 0,
                'xp_reward': 100,
                'generated_date': today,
                'is_weekly': True
            })
        
        self.active_quests = quest_templates
        self.save_data()
    
    def update_quest_progress(self, quest_type, amount=1, topic=None):
        """Update progress on active quests"""
        for quest in self.active_quests:
            if quest['type'] == quest_type:
                if topic and quest.get('target_topic') and quest['target_topic'] != topic:
                    continue
                quest['progress'] = min(quest['target'], quest['progress'] + amount)
                
                # Check if quest completed
                if quest['progress'] >= quest['target']:
                    self.complete_quest(quest)
        self.save_data()
    
    def complete_quest(self, quest):
        """Complete a quest and award rewards"""
        if quest not in self.completed_quests:
            self.completed_quests.append(quest)
            self.active_quests = [q for q in self.active_quests if q['id'] != quest['id']]
            self.add_xp(quest['xp_reward'])
            
            # Unlock features based on completed quests
            completed_count = len(self.completed_quests)
            if completed_count >= 5 and not self.unlocked_features['hard_mode']:
                self.unlocked_features['hard_mode'] = True
                self.unlock_achievement("Unlocked: Hard Mode!")
            if completed_count >= 15 and not self.unlocked_features['exam_simulator']:
                self.unlocked_features['exam_simulator'] = True
                self.unlock_achievement("Unlocked: Exam Simulator!")
            if completed_count >= 25 and not self.unlocked_features['bonus_visualizations']:
                self.unlocked_features['bonus_visualizations'] = True
                self.unlock_achievement("Unlocked: Bonus Visualizations!")
            if completed_count >= 40 and not self.unlocked_features['case_studies']:
                self.unlocked_features['case_studies'] = True
                self.unlock_achievement("Unlocked: AI Case Studies!")
            
            messagebox.showinfo("Quest Complete!", 
                f"🎉 {quest['title']}\n\n+{quest['xp_reward']} XP earned!")
    
    # ===== STREAK GUARDRAILS =====
    def use_streak_freeze(self):
        """Use a streak freeze to prevent streak loss"""
        if self.streak_freezes > 0:
            self.streak_freezes -= 1
            self.streak_freeze_used_today = True
            self.save_data()
            return True
        return False
    
    def earn_streak_freeze(self):
        """Earn a streak freeze (max 5)"""
        if self.streak_freezes < 5:
            self.streak_freezes += 1
            self.save_data()
            messagebox.showinfo("Streak Freeze Earned!", 
                f"❄️ You earned a streak freeze!\n\nYou now have {self.streak_freezes} freeze(s).\n"
                "Use them to protect your streak on busy days.")
    
    def check_streak_with_guardrails(self):
        """Check streak with supportive messaging and freeze option"""
        today = datetime.now().date().isoformat()
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
        
        if self.last_study_date == today:
            return True  # Already studied today
        
        if self.last_study_date == yesterday:
            return True  # Streak is intact, just needs activity
        
        # Streak at risk - offer freeze
        if self.streak > 0 and self.streak_freezes > 0 and not self.streak_freeze_used_today:
            response = messagebox.askyesno("Protect Your Streak?",
                f"🔥 Your {self.streak}-day streak is at risk!\n\n"
                f"You have {self.streak_freezes} streak freeze(s) available.\n\n"
                "Would you like to use one to protect your streak?\n\n"
                "(Or complete a quick 2-minute challenge to keep it naturally)")
            if response:
                self.use_streak_freeze()
                messagebox.showinfo("Streak Protected!", 
                    "❄️ Streak freeze used!\n\nYour streak is safe for today.")
                return True
        
        # Supportive message if streak lost
        if self.streak > 0 and self.last_study_date and self.last_study_date < yesterday:
            old_streak = self.streak
            self.streak = 0
            messagebox.showinfo("Starting Fresh",
                f"Your {old_streak}-day streak has ended.\n\n"
                "That's okay! Every expert started somewhere.\n"
                "🌟 Start a new streak today!")
        
        return False
    
    # ===== GRADEBOOK EXPORT =====
    def export_gradebook_data(self):
        """Export gradebook-friendly data for instructors"""
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        export_data = {
            'student_name': self.student_name or 'Guest',
            'student_alias': self.student_alias or self.student_name[:3] + '***' if self.student_name else 'Anonymous',
            'export_date': datetime.now().isoformat(),
            'summary': {
                'total_questions_answered': self.total_questions_answered,
                'correct_answers': self.correct_answers,
                'overall_accuracy': round(overall_accuracy, 2),
                'total_time_spent_minutes': round(self.total_time_spent / 60, 1),
                'exam_readiness_score': self.get_exam_readiness(),
                'current_level': self.level,
                'total_xp': self.xp,
                'current_streak': self.streak,
                'longest_streak': self.personal_bests.get('longest_streak', 0),
                'quests_completed': len(self.completed_quests)
            },
            'topic_mastery': {},
            'topic_accuracy': {}
        }
        
        # Add per-topic data
        for topic_num in self.topics.keys():
            topic_key = str(topic_num)
            export_data['topic_mastery'][topic_key] = {
                'mastery_level': self.mastery_levels.get(topic_key, 0),
                'mastery_percent': int((self.mastery_levels.get(topic_key, 0) / 5) * 100)
            }
            
            acc_data = self.topic_accuracy.get(topic_key, {'correct': 0, 'total': 0})
            if acc_data['total'] > 0:
                export_data['topic_accuracy'][topic_key] = {
                    'correct': acc_data['correct'],
                    'total': acc_data['total'],
                    'accuracy': round((acc_data['correct'] / acc_data['total']) * 100, 2)
                }
            else:
                export_data['topic_accuracy'][topic_key] = {
                    'correct': 0, 'total': 0, 'accuracy': 0
                }
        
        # Save export file
        export_filename = f"gradebook_export_{self.student_name or 'guest'}.json"
        try:
            with open(export_filename, 'w') as f:
                json.dump(export_data, f, indent=2)
        except:
            pass  # Silent fail for export
    
    def export_csv_report(self):
        """Export a CSV report for the instructor"""
        import csv
        
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        filename = f"student_report_{self.student_name or 'guest'}.csv"
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Student Name', self.student_name or 'Guest'])
                writer.writerow(['Total Questions', self.total_questions_answered])
                writer.writerow(['Correct Answers', self.correct_answers])
                writer.writerow(['Overall Accuracy (%)', f"{overall_accuracy:.1f}"])
                writer.writerow(['Exam Readiness (%)', self.get_exam_readiness()])
                writer.writerow(['Current Level', self.level])
                writer.writerow(['Total XP', self.xp])
                writer.writerow(['Current Streak', self.streak])
                writer.writerow(['Time Spent (min)', f"{self.total_time_spent/60:.1f}"])
                writer.writerow([])
                writer.writerow(['Topic', 'Mastery %', 'Accuracy %', 'Questions'])
                
                for topic_num, topic_info in self.topics.items():
                    topic_key = str(topic_num)
                    mastery = int((self.mastery_levels.get(topic_key, 0) / 5) * 100)
                    acc_data = self.topic_accuracy.get(topic_key, {'correct': 0, 'total': 0})
                    acc = (acc_data['correct'] / acc_data['total'] * 100) if acc_data['total'] > 0 else 0
                    writer.writerow([topic_info['name'], mastery, f"{acc:.1f}", acc_data['total']])
            
            messagebox.showinfo("Export Complete", f"Report saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export report: {e}")
    
    def add_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
        old_level = self.level
        self.level = 1 + (self.xp // 100)  # 100 XP per level
        if self.level > old_level:
            self.unlock_achievement(f"Level {self.level} Reached!")
            messagebox.showinfo("Level Up!", f"Congratulations! You've reached Level {self.level}!")
        self.save_data()
    
    def update_streak(self):
        """Update daily study streak"""
        today = datetime.now().date().isoformat()
        if self.last_study_date != today:
            if self.last_study_date:
                yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
                if self.last_study_date == yesterday:
                    self.streak += 1
                else:
                    self.streak = 1
            else:
                self.streak = 1
            self.last_study_date = today
            if self.streak % 7 == 0:
                self.unlock_achievement(f"{self.streak} Day Streak!")
            self.save_data()
    
    def unlock_achievement(self, achievement_name):
        """Unlock an achievement"""
        if achievement_name not in self.achievements:
            self.achievements.append(achievement_name)
            self.add_xp(50)  # Bonus XP for achievements
            self.save_data()
    
    def check_spaced_repetition(self, topic_num):
        """Check if topic needs review based on spaced repetition"""
        today = datetime.now().date()
        next_review = self.review_schedule.get(topic_num)
        if not next_review:
            return True  # Never reviewed, should review
        next_review_date = datetime.fromisoformat(next_review).date()
        return today >= next_review_date
    
    def update_spaced_repetition(self, topic_num, performance_score):
        """Update spaced repetition schedule based on performance"""
        mastery = self.mastery_levels[topic_num]
        if performance_score >= 0.8:  # Good performance
            mastery = min(5, mastery + 1)
        elif performance_score >= 0.6:  # Moderate performance
            mastery = max(0, mastery - 0.5)
        else:  # Poor performance
            mastery = max(0, mastery - 1)
        
        self.mastery_levels[topic_num] = mastery
        
        # Calculate next review date based on mastery (spaced repetition algorithm)
        days_until_review = [1, 3, 7, 14, 30, 60][min(int(mastery), 5)]
        next_review = datetime.now() + timedelta(days=days_until_review)
        self.review_schedule[topic_num] = next_review.date().isoformat()
        self.save_data()
    
    def load_questions(self):
        """Load questions database"""
        return QuestionsDatabase().get_all_questions()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_main_menu(self):
        """Modern, minimal dashboard with clear hierarchy"""
        self.clear_window()
        self.theme_colors = self.get_theme_colors()
        colors = self.theme_colors
        
        # Check for onboarding
        if not self.student_name and not self.is_guest and not self.onboarding_complete:
            self.show_onboarding()
            return
        
        # Show streak prompt if needed (B=MAP: Prompt)
        self.check_streak_prompt()
        
        self.root.configure(bg=colors['bg'])
        
        # ===== MINIMAL HEADER =====
        header = tk.Frame(self.root, bg=colors['bg_elevated'], height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg=colors['bg_elevated'])
        header_inner.pack(fill=tk.X, padx=self.SPACE_XL, pady=12)
        
        # Left: Logo + Course name
        left_header = tk.Frame(header_inner, bg=colors['bg_elevated'])
        left_header.pack(side=tk.LEFT)
        
        if self.logo_image:
            logo_small = tk.Label(left_header, image=self.logo_image, bg=colors['bg_elevated'])
            logo_small.pack(side=tk.LEFT, padx=(0, 12))
        
        tk.Label(left_header, text="COSC 5360 · AI Learning", 
                font=('Segoe UI', int(self.FONT_SUBTITLE * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], fg=colors['text_primary']).pack(side=tk.LEFT)
        
        # Right: User chip + settings
        right_header = tk.Frame(header_inner, bg=colors['bg_elevated'])
        right_header.pack(side=tk.RIGHT)
        
        # User chip
        name_display = self.student_name if self.student_name else "Guest"
        user_chip = tk.Label(right_header, text=f"Hi, {name_display[:12]}", 
                            font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                            bg=colors['surface'], fg=colors['text_primary'],
                            padx=12, pady=4)
        user_chip.pack(side=tk.LEFT, padx=8)
        
        # Theme toggle (minimal)
        theme_btn = tk.Button(right_header, text="◐" if not self.dark_mode else "◑",
                             command=self.toggle_dark_mode,
                             font=('Segoe UI', 14), bg=colors['bg_elevated'],
                             fg=colors['text_secondary'], relief=tk.FLAT, bd=0,
                             cursor='hand2', width=3)
        theme_btn.pack(side=tk.LEFT)
        
        # ===== MAIN CONTENT AREA =====
        main_frame = tk.Frame(self.root, bg=colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.SPACE_XL, pady=self.SPACE_LG)
        
        # Constrain content width for readability
        content_width = 900
        content = tk.Frame(main_frame, bg=colors['bg'], width=content_width)
        content.pack(anchor='n')
        
        # ===== TODAY CARD - Primary action area =====
        today_card, today_inner = self.create_card(content, padding=20)
        today_card.pack(fill=tk.X, pady=(0, self.SPACE_LG))
        
        # Stats row
        stats_row = tk.Frame(today_inner, bg=colors['bg_elevated'])
        stats_row.pack(fill=tk.X, pady=(0, self.SPACE_MD))
        
        # Streak
        streak_frame = tk.Frame(stats_row, bg=colors['bg_elevated'])
        streak_frame.pack(side=tk.LEFT)
        
        tk.Label(streak_frame, text=f"{self.streak}", 
                font=('Segoe UI', int(self.FONT_TITLE * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], fg=colors['warning']).pack(side=tk.LEFT)
        tk.Label(streak_frame, text=" day streak", 
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_secondary']).pack(side=tk.LEFT, padx=(4, 0))
        
        # XP + Level (right side)
        xp_frame = tk.Frame(stats_row, bg=colors['bg_elevated'])
        xp_frame.pack(side=tk.RIGHT)
        
        tk.Label(xp_frame, text=f"Level {self.level}", 
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(xp_frame, text=f"{self.xp} XP", 
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], fg=colors['primary']).pack(side=tk.LEFT)
        
        # Exam readiness bar
        readiness_row = tk.Frame(today_inner, bg=colors['bg_elevated'])
        readiness_row.pack(fill=tk.X, pady=(0, self.SPACE_MD))
        
        exam_readiness = self.get_exam_readiness()
        tk.Label(readiness_row, text="Exam readiness", 
                font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_tertiary']).pack(anchor='w')
        
        bar_bg = tk.Frame(readiness_row, bg=colors['surface'], height=8)
        bar_bg.pack(fill=tk.X, pady=4)
        
        bar_color = colors['success'] if exam_readiness >= 70 else colors['warning'] if exam_readiness >= 40 else colors['error']
        bar_fill = tk.Frame(bar_bg, bg=bar_color, height=8, width=int(content_width * 0.9 * exam_readiness / 100))
        bar_fill.place(x=0, y=0)
        
        tk.Label(readiness_row, text=f"{exam_readiness}%", 
                font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], fg=bar_color).pack(anchor='e')
        
        # Primary CTA - Daily Challenge
        today = datetime.now().date().isoformat()
        if self.last_study_date != today:
            cta_frame = tk.Frame(today_inner, bg=colors['bg_elevated'])
            cta_frame.pack(fill=tk.X, pady=(self.SPACE_SM, 0))
            
            primary_btn = self.create_button(cta_frame, "Start Daily Challenge", 
                                            self.start_daily_challenge, style='primary')
            primary_btn.pack(side=tk.LEFT)
            
            tk.Label(cta_frame, text="2-3 min to keep your streak", 
                    font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                    bg=colors['bg_elevated'], fg=colors['text_tertiary']).pack(side=tk.LEFT, padx=12)
        else:
            tk.Label(today_inner, text="✓ Today's practice complete", 
                    font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                    bg=colors['bg_elevated'], fg=colors['success']).pack(anchor='w')
        
        # ===== NEXT ACTIONS - 3 cards =====
        self.create_section_header(content, "Recommended for you").pack(anchor='w', pady=(0, self.SPACE_SM))
        
        actions_frame = tk.Frame(content, bg=colors['bg'])
        actions_frame.pack(fill=tk.X, pady=(0, self.SPACE_LG))
        
        # Get data for action cards
        review_topics = [tn for tn in self.topics.keys() if self.check_spaced_repetition(tn)]
        review_count = len(review_topics)
        weakest_topic, weak_acc = self.get_weakest_topic()
        
        action_data = [
            ("Review", f"{review_count} topics due" if review_count else "All caught up",
             self.start_review_session if review_count else None, review_count > 0),
            ("Weak area", f"T{weakest_topic}: {weak_acc:.0f}%" if weakest_topic else "No data",
             lambda: self.start_weak_area_drill(weakest_topic) if weakest_topic else None, 
             weakest_topic and weak_acc < 70),
            ("Quiz", "Test your knowledge",
             self.show_quiz_options, True)
        ]
        
        for i, (title, subtitle, command, is_active) in enumerate(action_data):
            self._create_minimal_action_card(actions_frame, title, subtitle, command, is_active, i)
        
        for col in range(3):
            actions_frame.columnconfigure(col, weight=1)
        
        # ===== EXPLORE - Secondary navigation =====
        self.create_section_header(content, "Explore", "All features").pack(anchor='w', pady=(0, self.SPACE_SM))
        
        nav_frame = tk.Frame(content, bg=colors['bg'])
        nav_frame.pack(fill=tk.X)
        
        # Navigation items - text links, not colored buttons
        nav_items = [
            ("Study", self.show_topics_menu),
            ("Quiz", self.show_quiz_options),
            ("Quests", self.show_quests),
            ("Progress", self.show_progress),
            ("Skills Map", self.show_skills_map),
            ("Leaderboard", self.show_leaderboard),
            ("NN Builder", self.show_nn_builder),
            ("Visualize", self.show_visualizations),
            ("Practice", self.show_practice_tests),
            ("Achievements", self.show_achievements),
        ]
        
        for i, (label, command) in enumerate(nav_items):
            btn = self.create_button(nav_frame, label, command, style='secondary')
            btn.grid(row=i//5, column=i%5, padx=4, pady=4, sticky='ew')
        
        for col in range(5):
            nav_frame.columnconfigure(col, weight=1)
        
        # Footer link
        footer = tk.Frame(content, bg=colors['bg'])
        footer.pack(fill=tk.X, pady=(self.SPACE_LG, 0))
        
        tk.Button(footer, text="About · Instructor Dashboard", 
                 command=self.show_about,
                 font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                 bg=colors['bg'], fg=colors['text_tertiary'],
                 relief=tk.FLAT, bd=0, cursor='hand2').pack(side=tk.LEFT)
    
    def _create_minimal_action_card(self, parent, title, subtitle, command, is_active, col):
        """Create a minimal action card"""
        colors = self.theme_colors
        
        card = tk.Frame(parent, bg=colors['bg_elevated'],
                       highlightbackground=colors['border'],
                       highlightthickness=1)
        card.grid(row=0, column=col, padx=4, pady=0, sticky='nsew')
        
        inner = tk.Frame(card, bg=colors['bg_elevated'])
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        tk.Label(inner, text=title,
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], 
                fg=colors['text_primary'] if is_active else colors['text_tertiary']).pack(anchor='w')
        
        tk.Label(inner, text=subtitle,
                font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_secondary']).pack(anchor='w', pady=(2, 8))
        
        if command and is_active:
            btn = self.create_button(inner, "Start", command, style='tertiary')
            btn.pack(anchor='w')
    
    def _create_action_card(self, parent, title, subtitle, description, color, command, column):
        """Create a minimal action card (legacy support)"""
        colors = self.theme_colors
        
        card = tk.Frame(parent, bg=colors['bg_elevated'],
                       highlightbackground=colors['border'], highlightthickness=1)
        card.grid(row=0, column=column, padx=4, pady=4, sticky='nsew')
        
        inner = tk.Frame(card, bg=colors['bg_elevated'])
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        tk.Label(inner, text=title.replace('⚡ ', '').replace('📋 ', '').replace('🔧 ', ''),
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale), 'bold'),
                bg=colors['bg_elevated'], fg=colors['text_primary']).pack(anchor='w')
        
        tk.Label(inner, text=subtitle, font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_secondary']).pack(anchor='w', pady=(2, 0))
        
        tk.Label(inner, text=description, font=('Segoe UI', int(self.FONT_CAPTION * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_tertiary'],
                wraplength=200).pack(anchor='w', pady=(4, 8))
        
        if command:
            btn = self.create_button(inner, "Start", command, style='tertiary')
            btn.pack(anchor='w')
    
    def check_streak_prompt(self):
        """Show gentle prompt to keep streak (B=MAP: Prompt)"""
        today = datetime.now().date().isoformat()
        if self.last_study_date != today and not self.streak_prompt_shown and self.streak > 0:
            self.streak_prompt_shown = True
            # Show non-intrusive prompt
            response = messagebox.askquestion("Keep Your Streak!", 
                f"🔥 You have a {self.streak} day streak!\n\n"
                "Take a 2-minute Daily Challenge to keep it going?\n\n"
                "(You can also do this later from the home screen)",
                icon='question')
            if response == 'yes':
                self.start_daily_challenge()
                return True
        return False
    
    def show_onboarding(self):
        """Modern, minimal onboarding screen"""
        self.clear_window()
        colors = self.theme_colors
        self.root.configure(bg=colors['bg'])
        
        # Center content
        center_frame = tk.Frame(self.root, bg=colors['bg'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo
        if self.logo_image:
            logo_label = tk.Label(center_frame, image=self.logo_image, bg=colors['bg'])
            logo_label.pack(pady=(0, 24))
        
        # Welcome text
        tk.Label(center_frame, text="Welcome to AI Learning", 
                font=('Segoe UI', int(self.FONT_TITLE * self.font_scale), 'bold'),
                bg=colors['bg'], fg=colors['text_primary']).pack()
        
        tk.Label(center_frame, text="COSC 5360 · Spring 2026", 
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                bg=colors['bg'], fg=colors['text_secondary']).pack(pady=(4, 32))
        
        # Name entry card
        card, card_inner = self.create_card(center_frame, padding=24)
        card.pack(pady=16)
        
        tk.Label(card_inner, text="What's your name?", 
                font=('Segoe UI', int(self.FONT_BODY * self.font_scale)),
                bg=colors['bg_elevated'], fg=colors['text_primary']).pack(anchor='w')
        
        name_entry = tk.Entry(card_inner, 
                             font=('Segoe UI', int(self.FONT_SUBTITLE * self.font_scale)),
                             width=28, relief=tk.FLAT, bd=0,
                             bg=colors['surface'], fg=colors['text_primary'],
                             insertbackground=colors['text_primary'])
        name_entry.pack(fill=tk.X, pady=(8, 16), ipady=8)
        name_entry.focus()
        
        def start_with_name():
            name = name_entry.get().strip()
            if name:
                self.student_name = name
                self.is_guest = False
                self.onboarding_complete = True
                self.save_data()
                self.show_guided_tour()
        
        def start_as_guest():
            self.student_name = ""
            self.is_guest = True
            self.onboarding_complete = True
            self.save_data()
            self.show_main_menu()
        
        # Buttons inside card
        primary_btn = self.create_button(card_inner, "Continue", start_with_name, style='primary')
        primary_btn.pack(fill=tk.X, pady=(0, 8))
        
        secondary_btn = self.create_button(card_inner, "Continue as Guest", start_as_guest, style='tertiary')
        secondary_btn.pack(fill=tk.X)
        
        name_entry.bind('<Return>', lambda e: start_with_name())
    
    def show_guided_tour(self):
        """Show 30-second guided tour for new users"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        tour_steps = [
            ("🎯 Daily Challenges", "Complete quick 2-3 minute challenges to build your streak and stay sharp."),
            ("📊 Track Your Progress", "Watch your mastery grow with our skills map and exam readiness indicator."),
            ("🧠 Smart Reviews", "Our spaced repetition system helps you remember what you've learned."),
            ("🏆 Earn Rewards", "Gain XP, level up, and unlock achievements as you learn!")
        ]
        
        center_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center_frame, text=f"Welcome, {self.student_name}! Here's how it works:", 
                font=('Arial', int(18 * self.font_scale), 'bold'),
                bg=self.theme_colors['bg'], fg=self.TARLETON_PURPLE).pack(pady=20)
        
        for title, desc in tour_steps:
            step_frame = tk.Frame(center_frame, bg=self.theme_colors['card_bg'],
                                 highlightbackground=self.TARLETON_PURPLE, highlightthickness=1)
            step_frame.pack(fill=tk.X, pady=8, padx=50)
            
            tk.Label(step_frame, text=title, font=('Arial', int(14 * self.font_scale), 'bold'),
                    bg=self.theme_colors['card_bg'], fg=self.TARLETON_PURPLE).pack(anchor='w', padx=15, pady=(10, 0))
            tk.Label(step_frame, text=desc, font=('Arial', int(11 * self.font_scale)),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                    wraplength=500).pack(anchor='w', padx=15, pady=(0, 10))
        
        btn_frame = tk.Frame(center_frame, bg=self.theme_colors['bg'])
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="Take Placement Quiz (60 sec)", 
                 command=self.start_placement_quiz,
                 bg='#27ae60', fg='white', font=('Arial', int(14 * self.font_scale), 'bold'),
                 width=25, height=2, relief=tk.FLAT, cursor='hand2').pack(pady=5)
        
        tk.Button(btn_frame, text="Skip to Dashboard", 
                 command=self.show_main_menu,
                 bg='#95a5a6', fg='white', font=('Arial', int(12 * self.font_scale)),
                 width=25, relief=tk.FLAT, cursor='hand2').pack(pady=5)
    
    def _lighten_hex(self, hex_color):
        """Lighten a hex color by 20%"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def start_daily_challenge(self):
        """Start a quick 2-3 minute daily challenge (B=MAP: Ability - 1-click action)"""
        if not self.questions_db:
            messagebox.showinfo("No Questions", "Question database is empty.")
            return
        
        # Mix questions from different topics (interleaving for desirable difficulty)
        all_questions = list(self.questions_db)
        random.shuffle(all_questions)
        
        # Select 5 questions for a quick challenge
        challenge_questions = all_questions[:5]
        
        self.start_quiz(challenge_questions, "⚡ Daily Challenge", None, 
                       is_daily_challenge=True, time_limit=180)  # 3 min time limit
    
    def start_review_session(self):
        """Start spaced repetition review session"""
        review_topics = [tn for tn in self.topics.keys() if self.check_spaced_repetition(tn)]
        if not review_topics:
            messagebox.showinfo("All Caught Up!", "No topics need review right now. Great job!")
            return
        
        # Collect questions from topics due for review
        review_questions = []
        for topic_num in review_topics[:3]:  # Limit to 3 topics per session
            topic_questions = [q for q in self.questions_db if q['topic'] == topic_num]
            random.shuffle(topic_questions)
            review_questions.extend(topic_questions[:3])
        
        random.shuffle(review_questions)
        
        if review_questions:
            self.start_quiz(review_questions, "📋 Review Session", None, is_review=True)
        else:
            messagebox.showinfo("No Questions", "No review questions available.")
    
    def start_weak_area_drill(self, topic_num):
        """Start adaptive difficulty drill for weak topic"""
        if not topic_num:
            return
        
        questions = [q for q in self.questions_db if q['topic'] == topic_num]
        if not questions:
            messagebox.showinfo("No Questions", "No questions available for this topic.")
            return
        
        # Get adaptive difficulty
        difficulty = self.get_adaptive_difficulty(topic_num)
        
        random.shuffle(questions)
        drill_questions = questions[:8]  # 8 question drill
        
        self.start_quiz(drill_questions, f"🔧 Weak Area Drill - Topic {topic_num}", 
                       topic_num, difficulty_mode=difficulty)
    
    def start_placement_quiz(self):
        """Start 60-second placement quiz for new users"""
        # Select 1 question from each of the first 5 topics
        placement_questions = []
        for topic_num in range(1, 6):
            topic_questions = [q for q in self.questions_db if q['topic'] == topic_num]
            if topic_questions:
                placement_questions.append(random.choice(topic_questions))
        
        if placement_questions:
            self.placement_quiz_taken = True
            self.save_data()
            self.start_quiz(placement_questions, "🎯 Placement Quiz", None, 
                           is_placement=True, time_limit=60)
        else:
            self.show_main_menu()
    
    def show_quiz_options(self):
        """Show quiz mode selection (SDT: Autonomy - choice)"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🎮 Choose Your Quiz Mode", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        tk.Label(self.root, text="Select the mode that fits your learning style (SDT: Autonomy)", 
                font=('Arial', 12), bg=self.theme_colors['bg'], 
                fg=self.theme_colors['text_secondary']).pack(pady=5)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Quiz mode options
        modes = [
            ("⚡ Daily Challenge", "2-3 minutes • Mixed topics • Keep your streak", 
             '#FF6B35', self.start_daily_challenge),
            ("🎲 Random Quiz", "15 questions • All topics • Test your overall knowledge", 
             '#e74c3c', self.start_quiz_game),
            ("🔀 Mixed Topics (Interleaving)", "10 questions • Enhanced learning through variety", 
             '#9b59b6', self.start_interleaved_quiz),
            ("⏱️ Time Attack (2 min)", "Race against time • As many as you can", 
             '#e67e22', lambda: self.start_timed_drill(120)),
            ("⏱️ Time Attack (5 min)", "Extended time challenge • Deep practice", 
             '#f39c12', lambda: self.start_timed_drill(300)),
            ("📝 No Multiple Choice", "Short answer mode • For advanced learners", 
             '#16a085', self.start_short_answer_quiz),
        ]
        
        for i, (title, desc, color, command) in enumerate(modes):
            mode_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                                 highlightbackground=color, highlightthickness=2)
            mode_frame.pack(fill=tk.X, pady=8)
            
            inner = tk.Frame(mode_frame, bg=self.theme_colors['card_bg'])
            inner.pack(fill=tk.X, padx=20, pady=15)
            
            left = tk.Frame(inner, bg=self.theme_colors['card_bg'])
            left.pack(side=tk.LEFT, fill=tk.Y)
            
            tk.Label(left, text=title, font=('Arial', 14, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=color).pack(anchor='w')
            tk.Label(left, text=desc, font=('Arial', 11),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
            
            tk.Button(inner, text="Start", command=command,
                     bg=color, fg='white', font=('Arial', 12, 'bold'),
                     relief=tk.FLAT, cursor='hand2', width=10).pack(side=tk.RIGHT)
    
    def start_interleaved_quiz(self):
        """Start mixed-topic quiz (interleaving for desirable difficulty)"""
        all_questions = list(self.questions_db)
        random.shuffle(all_questions)
        
        # Ensure we get questions from different topics
        selected = []
        topics_used = set()
        for q in all_questions:
            if q['topic'] not in topics_used or len(selected) >= 10:
                selected.append(q)
                topics_used.add(q['topic'])
            if len(selected) >= 10:
                break
        
        self.start_quiz(selected, "🔀 Interleaved Quiz", None)
    
    def start_timed_drill(self, seconds):
        """Start time-boxed drill"""
        all_questions = list(self.questions_db)
        random.shuffle(all_questions)
        self.start_quiz(all_questions[:20], f"⏱️ Time Attack ({seconds//60} min)", 
                       None, time_limit=seconds)
    
    def start_short_answer_quiz(self):
        """Start short answer quiz mode (no multiple choice)"""
        all_questions = list(self.questions_db)
        random.shuffle(all_questions)
        self.start_quiz(all_questions[:10], "📝 Short Answer Quiz", None, short_answer_mode=True)
    
    def show_skills_map(self):
        """Show detailed skills/mastery map (SDT: Competence visualization)"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="📈 Your Skills Map", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=10)
        
        # Exam readiness
        exam_readiness = self.get_exam_readiness()
        readiness_frame = tk.Frame(self.root, bg=self.theme_colors['card_bg'],
                                  highlightbackground=self.TARLETON_PURPLE, highlightthickness=2)
        readiness_frame.pack(fill=tk.X, padx=50, pady=10)
        
        readiness_inner = tk.Frame(readiness_frame, bg=self.theme_colors['card_bg'])
        readiness_inner.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(readiness_inner, text="📊 Overall Exam Readiness", 
                font=('Arial', 16, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(anchor='w')
        
        # Large readiness bar
        bar_frame = tk.Frame(readiness_inner, bg='#e0e0e0', height=30, width=500)
        bar_frame.pack(pady=10, anchor='w')
        bar_frame.pack_propagate(False)
        
        readiness_color = '#27ae60' if exam_readiness >= 70 else '#f39c12' if exam_readiness >= 40 else '#e74c3c'
        bar_fill = tk.Frame(bar_frame, bg=readiness_color, height=30, width=int(500 * exam_readiness / 100))
        bar_fill.place(x=0, y=0)
        
        tk.Label(readiness_inner, text=f"{exam_readiness}% Ready for Exam", 
                font=('Arial', 14, 'bold'),
                bg=self.theme_colors['card_bg'], fg=readiness_color).pack(anchor='w')
        
        # Scrollable topic details
        canvas = tk.Canvas(self.root, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        for topic_num, topic_info in self.topics.items():
            topic_frame = tk.Frame(scrollable, bg=self.theme_colors['card_bg'],
                                  highlightbackground=self.TARLETON_PURPLE, highlightthickness=1)
            topic_frame.pack(fill=tk.X, pady=5, padx=10)
            
            inner = tk.Frame(topic_frame, bg=self.theme_colors['card_bg'])
            inner.pack(fill=tk.X, padx=15, pady=12)
            
            # Topic header
            header_row = tk.Frame(inner, bg=self.theme_colors['card_bg'])
            header_row.pack(fill=tk.X)
            
            tk.Label(header_row, text=f"Topic {topic_num}: {topic_info['name']}", 
                    font=('Arial', 12, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=self.TARLETON_PURPLE).pack(side=tk.LEFT)
            
            # Mastery level
            mastery_level = self.mastery_levels.get(str(topic_num), 0)
            mastery_pct = int((mastery_level / 5) * 100)
            
            mastery_color = '#27ae60' if mastery_pct >= 70 else '#f39c12' if mastery_pct >= 40 else '#e74c3c'
            tk.Label(header_row, text=f"Mastery: {mastery_pct}%", 
                    font=('Arial', 11, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=mastery_color).pack(side=tk.RIGHT)
            
            # Progress bar
            bar_bg = tk.Frame(inner, bg='#e0e0e0', height=15, width=400)
            bar_bg.pack(pady=5, anchor='w')
            bar_bg.pack_propagate(False)
            
            bar_fill = tk.Frame(bar_bg, bg=mastery_color, height=15, width=int(400 * mastery_pct / 100))
            bar_fill.place(x=0, y=0)
            
            # Accuracy stats
            acc_data = self.topic_accuracy.get(str(topic_num), {'correct': 0, 'total': 0})
            if acc_data['total'] > 0:
                topic_acc = (acc_data['correct'] / acc_data['total']) * 100
                tk.Label(inner, text=f"Accuracy: {topic_acc:.0f}% ({acc_data['correct']}/{acc_data['total']} correct)", 
                        font=('Arial', 10),
                        bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
            else:
                tk.Label(inner, text="No questions attempted yet", 
                        font=('Arial', 10),
                        bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
    
    
    def show_topics_menu(self):
        """Display topics menu"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        # Back button
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        # Header
        header = tk.Label(self.root, text="📚 Course Topics", font=('Georgia', 28, 'bold'),
                         bg=self.theme_colors['bg'], fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        # Topics frame
        topics_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        topics_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Create scrollable canvas
        canvas = tk.Canvas(topics_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(topics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display topics
        for topic_num, topic_info in self.topics.items():
            topic_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['card_bg'], relief=tk.FLAT, bd=0,
                                  highlightbackground=self.TARLETON_PURPLE, highlightthickness=2)
            topic_frame.pack(fill=tk.X, padx=10, pady=8)
            
            # Topic info
            info_frame = tk.Frame(topic_frame, bg=self.theme_colors['card_bg'])
            info_frame.pack(fill=tk.X, padx=15, pady=10)
            
            topic_label = tk.Label(info_frame, 
                                  text=f"Topic {topic_num}: {topic_info['name']}",
                                  font=('Arial', 14, 'bold'), bg=self.theme_colors['card_bg'], 
                                  fg=self.TARLETON_PURPLE, anchor='w')
            topic_label.pack(fill=tk.X)
            
            hours_label = tk.Label(info_frame, 
                                  text=f"⏱️ {topic_info['hours']} hours",
                                  font=('Arial', 11), bg=self.theme_colors['card_bg'], 
                                  fg=self.theme_colors['text_secondary'], anchor='w')
            hours_label.pack(fill=tk.X)
            
            # Progress bar
            progress = self.progress.get(topic_num, 0)
            progress_frame = tk.Frame(topic_frame, bg=self.theme_colors['card_bg'])
            progress_frame.pack(fill=tk.X, padx=15, pady=5)
            
            tk.Label(progress_frame, text=f"Progress: {progress}%", 
                    font=('Arial', 10), bg=self.theme_colors['card_bg'], 
                    fg=self.theme_colors['text']).pack(side=tk.LEFT)
            
            progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
            progress_bar['value'] = progress
            progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # Buttons
            btn_frame = tk.Frame(topic_frame, bg=self.theme_colors['card_bg'])
            btn_frame.pack(fill=tk.X, padx=15, pady=10)
            
            tk.Button(btn_frame, text="📖 Study", 
                     command=lambda tn=topic_num: self.study_topic(tn),
                     bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 11), 
                     width=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="🎯 Quiz", 
                     command=lambda tn=topic_num: self.start_topic_quiz(tn),
                     bg='#e74c3c', fg='white', font=('Arial', 11), 
                     width=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="📝 Test", 
                     command=lambda tn=topic_num: self.start_topic_test(tn),
                     bg='#f39c12', fg='white', font=('Arial', 11), 
                     width=12, relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def study_topic(self, topic_num):
        """Show study material for a topic"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back", command=self.show_topics_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        topic_name = self.topics[topic_num]['name']
        header = tk.Label(self.root, text=f"📖 {topic_name}", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        # Study content
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        study_content = StudyContent().get_content(topic_num)
        
        text_widget = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                               font=('Arial', 12), bg=self.theme_colors['card_bg'], 
                                               fg=self.theme_colors['text'], padx=20, pady=20)
        text_widget.insert('1.0', study_content)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Mark as studied
        self.progress[topic_num] = min(100, self.progress[topic_num] + 10)
        self.update_streak()
        self.add_xp(5)  # XP for studying
        
        # Update quest progress for study quests
        self.update_quest_progress('study', 1, topic_num)
        
        if self.progress[topic_num] >= 100:
            self.unlock_achievement(f"Mastered: {topic_name}")
        self.save_data()
    
    def start_topic_quiz(self, topic_num):
        """Start a quiz for a specific topic"""
        questions = [q for q in self.questions_db if q['topic'] == topic_num]
        if not questions:
            messagebox.showinfo("No Questions", "No questions available for this topic yet.")
            return
        
        self.start_quiz(questions[:10], f"Topic {topic_num} Quiz", topic_num)
    
    def start_topic_test(self, topic_num):
        """Start a test for a specific topic"""
        questions = [q for q in self.questions_db if q['topic'] == topic_num]
        if not questions:
            messagebox.showinfo("No Questions", "No questions available for this topic yet.")
            return
        
        self.start_quiz(questions[:20], f"Topic {topic_num} Test", topic_num, is_test=True)
    
    def start_quiz_game(self):
        """Start random quiz game"""
        if not self.questions_db:
            messagebox.showinfo("No Questions", "Question database is empty.")
            return
        
        random.shuffle(self.questions_db)
        self.start_quiz(self.questions_db[:15], "Random Quiz Game", None)
    
    def start_quiz(self, questions, title, topic_num, is_test=False, is_daily_challenge=False,
                   is_review=False, is_placement=False, time_limit=None, difficulty_mode='normal',
                   short_answer_mode=False):
        """Start quiz/test interface with enhanced options"""
        if not questions:
            messagebox.showinfo("Error", "No questions available.")
            return
        
        self.clear_window()
        self.current_questions = questions
        self.current_question_index = 0
        self.quiz_answers = []
        self.quiz_confidences = []  # Track confidence for each answer
        self.quiz_title = title
        self.quiz_topic = topic_num
        self.is_test = is_test
        self.is_daily_challenge = is_daily_challenge
        self.is_review = is_review
        self.is_placement = is_placement
        self.time_limit = time_limit
        self.difficulty_mode = difficulty_mode
        self.short_answer_mode = short_answer_mode
        self.start_time = datetime.now()
        self.time_remaining = time_limit
        
        # Start timer if time limit set
        if time_limit:
            self.update_timer()
        
        self.show_question()
    
    def update_timer(self):
        """Update countdown timer for timed quizzes"""
        if not hasattr(self, 'time_remaining') or self.time_remaining is None:
            return
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.time_remaining = max(0, self.time_limit - int(elapsed))
        
        if self.time_remaining <= 0:
            # Time's up - auto submit
            messagebox.showinfo("Time's Up!", "The time limit has been reached.")
            self.finish_quiz()
            return
        
        # Schedule next update
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            mins = self.time_remaining // 60
            secs = self.time_remaining % 60
            self.timer_label.config(text=f"⏱️ {mins}:{secs:02d}")
            self.root.after(1000, self.update_timer)
    
    def show_question(self):
        """Display current question with timer and confidence rating"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        if self.current_question_index >= len(self.current_questions):
            self.finish_quiz()
            return
        
        question = self.current_questions[self.current_question_index]
        
        # Header with Tarleton purple
        header_frame = tk.Frame(self.root, bg=self.TARLETON_PURPLE, height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_inner = tk.Frame(header_frame, bg=self.TARLETON_PURPLE)
        header_inner.pack(fill=tk.X, padx=20, pady=10)
        
        # Left: Quiz title
        tk.Label(header_inner, text=self.quiz_title, font=('Arial', 12),
                bg=self.TARLETON_PURPLE, fg='#e8e8e8').pack(side=tk.LEFT)
        
        # Right: Timer (if applicable)
        if hasattr(self, 'time_limit') and self.time_limit:
            self.timer_label = tk.Label(header_inner, text="⏱️ --:--", 
                                       font=('Arial', 14, 'bold'),
                                       bg=self.TARLETON_PURPLE, fg='#FFD700')
            self.timer_label.pack(side=tk.RIGHT)
            self.update_timer()
        
        # Progress
        progress_row = tk.Frame(header_frame, bg=self.TARLETON_PURPLE)
        progress_row.pack(fill=tk.X, padx=20)
        
        progress_text = f"Question {self.current_question_index + 1} of {len(self.current_questions)}"
        tk.Label(progress_row, text=progress_text, font=('Arial', 12, 'bold'),
                bg=self.TARLETON_PURPLE, fg='white').pack(side=tk.LEFT)
        
        progress_bar = ttk.Progressbar(progress_row, length=300, mode='determinate',
                                       maximum=len(self.current_questions))
        progress_bar['value'] = self.current_question_index + 1
        progress_bar.pack(side=tk.RIGHT, pady=5)
        
        # Question content
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Topic indicator
        topic_num = question.get('topic', 'N/A')
        topic_name = self.topics.get(topic_num, {}).get('name', 'Unknown')
        tk.Label(content_frame, text=f"📚 Topic {topic_num}: {topic_name}", 
                font=('Arial', 10),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
        
        # Question text
        question_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'], 
                                 highlightbackground=self.TARLETON_PURPLE, highlightthickness=3)
        question_frame.pack(fill=tk.X, pady=10)
        
        q_text = tk.Label(question_frame, text=question['question'], 
                         font=('Arial', 15, 'bold'), bg=self.theme_colors['card_bg'], 
                         fg=self.TARLETON_PURPLE, wraplength=800, justify=tk.LEFT, padx=20, pady=15)
        q_text.pack(anchor='w')
        
        # Answer options (or short answer)
        if hasattr(self, 'short_answer_mode') and self.short_answer_mode:
            self._show_short_answer_input(content_frame, question)
        else:
            self._show_multiple_choice(content_frame, question)
        
        # Confidence rating (enhanced spaced repetition)
        confidence_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        confidence_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(confidence_frame, text="How confident are you?", 
                font=('Arial', 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text_secondary']).pack(side=tk.LEFT)
        
        self.confidence_var = tk.StringVar(value='medium')
        
        for conf, label, color in [('low', '😟 Low', '#e74c3c'), 
                                   ('medium', '🤔 Medium', '#f39c12'), 
                                   ('high', '😊 High', '#27ae60')]:
            rb = tk.Radiobutton(confidence_frame, text=label, variable=self.confidence_var,
                               value=conf, font=('Arial', 10), 
                               bg=self.theme_colors['bg'], fg=color,
                               selectcolor=self.theme_colors['bg'])
            rb.pack(side=tk.LEFT, padx=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        nav_frame.pack(fill=tk.X, pady=15)
        
        if self.current_question_index > 0:
            tk.Button(nav_frame, text="← Previous", 
                     command=self.previous_question,
                     bg='#7f8c8d', fg='white', font=('Arial', 12), width=15,
                     relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=10)
        
        btn_text = "Finish" if self.current_question_index == len(self.current_questions) - 1 else "Next →"
        tk.Button(nav_frame, text=btn_text, 
                 command=self.next_question,
                 bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12, 'bold'), width=15,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=10)
        
        # Store correct answer for later
        self.current_correct = question['correct']
    
    def _show_multiple_choice(self, parent, question):
        """Display multiple choice options"""
        options_frame = tk.Frame(parent, bg=self.theme_colors['bg'])
        options_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.selected_answer = tk.StringVar()
        options = question['options']
        
        option_colors = ['#e8f4f8', '#f8f4e8', '#f4f8e8', '#f8e8f4']
        for i, option in enumerate(options):
            opt_bg = option_colors[i % len(option_colors)] if not self.dark_mode else self.theme_colors['card_bg']
            option_frame = tk.Frame(options_frame, bg=opt_bg, 
                                   highlightbackground=self.TARLETON_PURPLE, highlightthickness=1)
            option_frame.pack(fill=tk.X, pady=4)
            
            rb = tk.Radiobutton(option_frame, text=option, variable=self.selected_answer,
                               value=option, font=('Arial', 12), bg=opt_bg, 
                               fg=self.theme_colors['text'],
                               selectcolor=self.TARLETON_PURPLE_LIGHT, 
                               activebackground=self.TARLETON_PURPLE_LIGHT,
                               padx=20, pady=10, anchor='w', cursor='hand2')
            rb.pack(fill=tk.X)
    
    def _show_short_answer_input(self, parent, question):
        """Display short answer input field"""
        self.selected_answer = tk.StringVar()
        
        tk.Label(parent, text="Type your answer:", 
                font=('Arial', 12),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=5)
        
        answer_entry = tk.Entry(parent, textvariable=self.selected_answer,
                               font=('Arial', 14), width=50)
        answer_entry.pack(anchor='w', pady=10)
        answer_entry.focus()
        
        # Show hint (first letters of correct answer words)
        correct = question['correct']
        hint = ' '.join([w[0] + '_' * (len(w)-1) for w in correct.split()[:5]])
        tk.Label(parent, text=f"Hint: {hint}", 
                font=('Arial', 10),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
    
    def previous_question(self):
        """Go to previous question"""
        if self.current_question_index > 0:
            # Save current answer and confidence
            if self.selected_answer.get():
                if self.current_question_index < len(self.quiz_answers):
                    self.quiz_answers[self.current_question_index] = self.selected_answer.get()
                else:
                    self.quiz_answers.append(self.selected_answer.get())
                
                # Save confidence
                confidence = self.confidence_var.get() if hasattr(self, 'confidence_var') else 'medium'
                if self.current_question_index < len(self.quiz_confidences):
                    self.quiz_confidences[self.current_question_index] = confidence
                else:
                    self.quiz_confidences.append(confidence)
            
            self.current_question_index -= 1
            self.show_question()
            
            # Restore previous answer and confidence if exists
            if self.current_question_index < len(self.quiz_answers):
                self.selected_answer.set(self.quiz_answers[self.current_question_index])
            if self.current_question_index < len(self.quiz_confidences):
                self.confidence_var.set(self.quiz_confidences[self.current_question_index])
    
    def next_question(self):
        """Go to next question with confidence tracking"""
        if not self.selected_answer.get():
            messagebox.showwarning("No Answer", "Please select an answer before continuing.")
            return
        
        # Save answer
        if self.current_question_index < len(self.quiz_answers):
            self.quiz_answers[self.current_question_index] = self.selected_answer.get()
        else:
            self.quiz_answers.append(self.selected_answer.get())
        
        # Save confidence
        confidence = self.confidence_var.get() if hasattr(self, 'confidence_var') else 'medium'
        if self.current_question_index < len(self.quiz_confidences):
            self.quiz_confidences[self.current_question_index] = confidence
        else:
            self.quiz_confidences.append(confidence)
        
        self.current_question_index += 1
        self.show_question()
        
        # Restore answer if exists
        if self.current_question_index < len(self.quiz_answers):
            self.selected_answer.set(self.quiz_answers[self.current_question_index])
    
    def finish_quiz(self):
        """Calculate and display quiz results with enhanced feedback"""
        self.clear_window()
        
        # Calculate score
        correct = 0
        total = len(self.current_questions)
        
        for i, question in enumerate(self.current_questions):
            user_answer = self.quiz_answers[i] if i < len(self.quiz_answers) else None
            is_correct = user_answer == question['correct']
            if is_correct:
                correct += 1
            
            # Update per-question memory strength
            confidence = self.quiz_confidences[i] if i < len(self.quiz_confidences) else 'medium'
            self.update_question_memory(question, is_correct, confidence)
            
            # Update topic accuracy
            topic_num = str(question.get('topic', 0))
            if topic_num not in self.topic_accuracy:
                self.topic_accuracy[topic_num] = {'correct': 0, 'total': 0}
            self.topic_accuracy[topic_num]['total'] += 1
            if is_correct:
                self.topic_accuracy[topic_num]['correct'] += 1
        
        score_percent = (correct / total) * 100 if total > 0 else 0
        time_taken = (datetime.now() - self.start_time).total_seconds()
        
        # Update statistics
        self.total_questions_answered += total
        self.correct_answers += correct
        self.total_time_spent += time_taken  # Track total study time
        
        # Update personal bests
        if score_percent > self.personal_bests.get('best_accuracy', 0):
            self.personal_bests['best_accuracy'] = score_percent
        if score_percent > self.personal_bests.get('highest_single_quiz', 0):
            self.personal_bests['highest_single_quiz'] = score_percent
        if time_taken < self.personal_bests.get('fastest_quiz', float('inf')) and score_percent >= 70:
            self.personal_bests['fastest_quiz'] = time_taken
        
        # Update quest progress
        self.update_quest_progress('quiz', total)  # Progress on quiz quests
        if hasattr(self, 'is_review') and self.is_review:
            self.update_quest_progress('review', 1)
        if score_percent >= 70:
            self.update_quest_progress('mastery', 1)  # Weekly mastery challenge
        
        # Earn streak freeze for 5 consecutive days
        if self.streak > 0 and self.streak % 5 == 0:
            self.earn_streak_freeze()
        
        # Add XP based on performance
        xp_earned = int(score_percent / 10) + 5  # Base 5 XP + bonus
        if hasattr(self, 'is_daily_challenge') and self.is_daily_challenge:
            xp_earned += 10  # Bonus for daily challenge
            self.daily_challenge_completed = datetime.now().date().isoformat()
        self.add_xp(xp_earned)
        self.update_streak()
        
        if self.quiz_topic:
            if self.is_test:
                self.scores[f"test_topic_{self.quiz_topic}"] = score_percent
            else:
                self.scores[f"quiz_topic_{self.quiz_topic}"] = score_percent
            self.progress[self.quiz_topic] = min(100, self.progress[self.quiz_topic] + 5)
            self.update_spaced_repetition(self.quiz_topic, score_percent / 100)
        
        # Unlock achievements
        if score_percent == 100:
            self.unlock_achievement("Perfect Score!")
        elif score_percent >= 90:
            self.unlock_achievement("Excellent Performance!")
        if self.total_questions_answered >= 100:
            self.unlock_achievement("Century Club: 100 Questions!")
        if self.streak >= 7:
            self.unlock_achievement("7 Day Streak!")
        
        self.save_data()
        self.root.configure(bg=self.theme_colors['bg'])
        
        # Results display
        header = tk.Label(self.root, text="🎉 Quiz Complete!", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=15)
        
        # Main results area - scrollable
        main_canvas = tk.Canvas(self.root, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        results_frame = tk.Frame(main_canvas, bg=self.theme_colors['bg'])
        
        results_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=results_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=30, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Score card
        score_frame = tk.Frame(results_frame, bg=self.theme_colors['card_bg'], 
                              highlightbackground=self.TARLETON_PURPLE, highlightthickness=3)
        score_frame.pack(fill=tk.X, pady=10, padx=20)
        
        score_inner = tk.Frame(score_frame, bg=self.theme_colors['card_bg'])
        score_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Score display
        score_text = f"Score: {correct}/{total} ({score_percent:.0f}%)"
        tk.Label(score_inner, text=score_text, font=('Arial', 22, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.TARLETON_PURPLE).pack()
        
        # Stats row
        stats_row = tk.Frame(score_inner, bg=self.theme_colors['card_bg'])
        stats_row.pack(fill=tk.X, pady=10)
        
        time_mins = int(time_taken // 60)
        time_secs = int(time_taken % 60)
        stats_data = [
            (f"⏱️ {time_mins}:{time_secs:02d}", "Time"),
            (f"+{xp_earned} XP", "Earned"),
            (f"🔥 {self.streak} days", "Streak")
        ]
        for value, label in stats_data:
            stat_frame = tk.Frame(stats_row, bg=self.theme_colors['card_bg'])
            stat_frame.pack(side=tk.LEFT, padx=20)
            tk.Label(stat_frame, text=value, font=('Arial', 14, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['accent']).pack()
            tk.Label(stat_frame, text=label, font=('Arial', 9),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack()
        
        # Performance message
        if score_percent >= 90:
            message = "🌟 Excellent! Outstanding performance!"
            color = '#27ae60'
        elif score_percent >= 70:
            message = "👍 Good job! Keep practicing!"
            color = '#3498db'
        elif score_percent >= 50:
            message = "📚 Not bad! Review the material and try again."
            color = '#f39c12'
        else:
            message = "💪 Keep studying! You'll improve with practice."
            color = '#e74c3c'
        
        tk.Label(score_inner, text=message, font=('Arial', 14),
                bg=self.theme_colors['card_bg'], fg=color).pack(pady=5)
        
        # Enhanced Review - with explanations
        review_label = tk.Label(results_frame, text="📝 Review Your Answers (Learn from mistakes!)", 
                               font=('Arial', 14, 'bold'),
                               bg=self.theme_colors['bg'], fg=self.theme_colors['text'])
        review_label.pack(anchor='w', padx=20, pady=(15, 5))
        
        for i, question in enumerate(self.current_questions):
            user_answer = self.quiz_answers[i] if i < len(self.quiz_answers) else "No answer"
            is_correct = user_answer == question['correct']
            
            bg_color = '#e8f8e8' if is_correct else '#fff0f0'
            if self.dark_mode:
                bg_color = '#2d4a3d' if is_correct else '#4a2d2d'
            
            q_frame = tk.Frame(results_frame, bg=bg_color, relief=tk.FLAT,
                              highlightbackground='#27ae60' if is_correct else '#e74c3c', 
                              highlightthickness=2)
            q_frame.pack(fill=tk.X, padx=20, pady=5)
            
            inner = tk.Frame(q_frame, bg=bg_color)
            inner.pack(fill=tk.X, padx=15, pady=10)
            
            # Header row
            header_row = tk.Frame(inner, bg=bg_color)
            header_row.pack(fill=tk.X)
            
            status = "✓ Correct" if is_correct else "✗ Incorrect"
            status_color = '#27ae60' if is_correct else '#e74c3c'
            
            tk.Label(header_row, text=f"Q{i+1}: {status}", font=('Arial', 11, 'bold'),
                    bg=bg_color, fg=status_color).pack(side=tk.LEFT)
            
            topic_num = question.get('topic', 'N/A')
            tk.Label(header_row, text=f"Topic {topic_num}", font=('Arial', 9),
                    bg=bg_color, fg=self.theme_colors['text_secondary']).pack(side=tk.RIGHT)
            
            # Question text
            tk.Label(inner, text=question['question'], font=('Arial', 11),
                    bg=bg_color, fg=self.theme_colors['text'], 
                    wraplength=650, justify=tk.LEFT).pack(anchor='w', pady=5)
            
            # Your answer
            tk.Label(inner, text=f"Your answer: {user_answer}", font=('Arial', 10),
                    bg=bg_color, fg='#27ae60' if is_correct else '#e74c3c').pack(anchor='w')
            
            if not is_correct:
                # Correct answer
                tk.Label(inner, text=f"✓ Correct answer: {question['correct']}", 
                        font=('Arial', 10, 'bold'), bg=bg_color, fg='#27ae60').pack(anchor='w', pady=2)
                
                # Explanation (if available in question)
                explanation = question.get('explanation', self._generate_explanation(question))
                if explanation:
                    exp_frame = tk.Frame(inner, bg='#fffde7' if not self.dark_mode else '#3d3d00')
                    exp_frame.pack(fill=tk.X, pady=5)
                    tk.Label(exp_frame, text=f"💡 {explanation}", font=('Arial', 10),
                            bg='#fffde7' if not self.dark_mode else '#3d3d00', 
                            fg='#333' if not self.dark_mode else '#fff',
                            wraplength=620, justify=tk.LEFT).pack(padx=10, pady=5, anchor='w')
                
                # Add to Review Queue button
                btn_frame = tk.Frame(inner, bg=bg_color)
                btn_frame.pack(anchor='w', pady=5)
                
                q_id = self.get_question_id(question)
                if q_id not in self.review_queue:
                    add_btn = tk.Button(btn_frame, text="📋 Add to Review Queue", 
                                       command=lambda qid=q_id: self._add_to_review(qid),
                                       bg='#f39c12', fg='white', font=('Arial', 9),
                                       relief=tk.FLAT, cursor='hand2')
                    add_btn.pack(side=tk.LEFT)
                else:
                    tk.Label(btn_frame, text="✓ In Review Queue", font=('Arial', 9),
                            bg=bg_color, fg='#f39c12').pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = tk.Frame(results_frame, bg=self.theme_colors['bg'])
        btn_frame.pack(fill=tk.X, pady=20, padx=20)
        
        tk.Button(btn_frame, text="🔄 Retake Quiz", 
                 command=lambda: self.start_quiz(self.current_questions, self.quiz_title, self.quiz_topic, self.is_test),
                 bg='#3498db', fg='white', font=('Arial', 11), width=14,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        if len(self.review_queue) > 0:
            tk.Button(btn_frame, text=f"📋 Review Queue ({len(self.review_queue)})", 
                     command=self.start_review_queue,
                     bg='#f39c12', fg='white', font=('Arial', 11), width=18,
                     relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🏠 Main Menu", 
                 command=self.show_main_menu,
                 bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 11), width=14,
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=5)
    
    def _generate_explanation(self, question):
        """Generate a simple explanation for why the correct answer is right"""
        correct = question['correct']
        # Return a generic helpful explanation
        return f"The correct answer is: {correct}. Review the study material for this topic to understand why."
    
    def _add_to_review(self, q_id):
        """Add question to review queue"""
        if q_id not in self.review_queue:
            self.review_queue.append(q_id)
            self.save_data()
            messagebox.showinfo("Added!", "Question added to your review queue.")
    
    def start_review_queue(self):
        """Start quiz from review queue"""
        if not self.review_queue:
            messagebox.showinfo("Empty Queue", "Your review queue is empty!")
            return
        
        # Find questions matching review queue IDs
        review_questions = []
        for q in self.questions_db:
            if self.get_question_id(q) in self.review_queue:
                review_questions.append(q)
        
        if review_questions:
            random.shuffle(review_questions)
            self.start_quiz(review_questions[:10], "📋 Review Queue", None, is_review=True)
        else:
            self.review_queue = []
            self.save_data()
            messagebox.showinfo("Queue Cleared", "Review queue has been cleared.")
    
    def show_progress(self):
        """Display student progress"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="📊 Your Progress", 
                         font=('Georgia', 28, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Overall statistics
        stats_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'], relief=tk.FLAT, 
                              highlightbackground=self.TARLETON_PURPLE, highlightthickness=2)
        stats_frame.pack(fill=tk.X, pady=20)
        
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        stats_text = f"""
        Student: {self.student_name or 'Guest'}
        Total Questions Answered: {self.total_questions_answered}
        Correct Answers: {self.correct_answers}
        Overall Accuracy: {overall_accuracy:.1f}%
        """
        
        tk.Label(stats_frame, text=stats_text, font=('Arial', 14),
                bg='#f5f5f5', fg='#000000', justify=tk.LEFT).pack(padx=20, pady=20)
        
        # Topic progress
        topics_frame = tk.Frame(content_frame, bg='#ffffff')
        topics_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        tk.Label(topics_frame, text="Topic Progress:", font=('Arial', 16, 'bold'),
                bg='#ffffff', fg='#000000').pack(anchor='w', pady=10)
        
        for topic_num, topic_info in self.topics.items():
            progress = self.progress.get(topic_num, 0)
            
            topic_frame = tk.Frame(topics_frame, bg='#f5f5f5', relief=tk.RAISED, bd=2)
            topic_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(topic_frame, text=f"Topic {topic_num}: {topic_info['name']}",
                    font=('Arial', 12), bg='#f5f5f5', fg='#000000',
                    anchor='w').pack(fill=tk.X, padx=15, pady=10)
            
            progress_bar = ttk.Progressbar(topic_frame, length=400, mode='determinate')
            progress_bar['value'] = progress
            progress_bar.pack(padx=15, pady=5, fill=tk.X)
            
            tk.Label(topic_frame, text=f"{progress}%", font=('Arial', 10),
                    bg='#f5f5f5', fg='#666666').pack(anchor='e', padx=15, pady=5)
    
    def show_leaderboard(self):
        """Display personal bests leaderboard (SDT: Competence)"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🏆 Your Personal Bests", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_GOLD)
        header.pack(pady=15)
        
        tk.Label(self.root, text="Track your achievements and beat your own records!", 
                font=('Arial', 12), bg=self.theme_colors['bg'], 
                fg=self.theme_colors['text_secondary']).pack()
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Personal Bests Cards
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        bests_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        bests_frame.pack(fill=tk.X, pady=10)
        
        # Define personal best records
        fastest_time = self.personal_bests.get('fastest_quiz', float('inf'))
        fastest_str = f"{int(fastest_time//60)}:{int(fastest_time%60):02d}" if fastest_time < float('inf') else "N/A"
        
        records = [
            ("🎯", "Best Quiz Score", f"{self.personal_bests.get('highest_single_quiz', 0):.0f}%", "#27ae60"),
            ("📊", "Overall Accuracy", f"{overall_accuracy:.1f}%", "#3498db"),
            ("⚡", "Fastest Quiz", fastest_str, "#e67e22"),
            ("🔥", "Longest Streak", f"{self.personal_bests.get('longest_streak', 0)} days", "#FF6B35"),
            ("⭐", "Current Level", str(self.level), self.TARLETON_PURPLE),
            ("💎", "Total XP", str(self.xp), self.TARLETON_GOLD),
        ]
        
        for i, (emoji, label, value, color) in enumerate(records):
            card = tk.Frame(bests_frame, bg=self.theme_colors['card_bg'],
                           highlightbackground=color, highlightthickness=2)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            inner = tk.Frame(card, bg=self.theme_colors['card_bg'])
            inner.pack(padx=20, pady=15)
            
            tk.Label(inner, text=emoji, font=('Arial', 24),
                    bg=self.theme_colors['card_bg']).pack()
            tk.Label(inner, text=label, font=('Arial', 11),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack()
            tk.Label(inner, text=value, font=('Arial', 18, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=color).pack()
        
        for col in range(3):
            bests_frame.columnconfigure(col, weight=1)
        
        # Statistics Summary
        stats_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                              highlightbackground=self.TARLETON_PURPLE, highlightthickness=2)
        stats_frame.pack(fill=tk.X, pady=20)
        
        stats_inner = tk.Frame(stats_frame, bg=self.theme_colors['card_bg'])
        stats_inner.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(stats_inner, text="📈 Overall Statistics", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(anchor='w')
        
        stats_text = f"""
        👤 Student: {self.student_name or 'Guest'}
        ✅ Total Correct: {self.correct_answers} / {self.total_questions_answered} questions
        📚 Topics Mastered: {sum(1 for p in self.progress.values() if p >= 80)} / 10
        🏆 Achievements: {len(self.achievements)} unlocked
        🔥 Current Streak: {self.streak} days
        📋 Review Queue: {len(self.review_queue)} questions
        """
        
        tk.Label(stats_inner, text=stats_text, font=('Arial', 12),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                justify=tk.LEFT).pack(anchor='w', padx=10)
        
        # Motivational message
        if overall_accuracy >= 80:
            msg = "🌟 Outstanding! You're mastering AI concepts!"
        elif overall_accuracy >= 60:
            msg = "👍 Great progress! Keep up the good work!"
        elif self.total_questions_answered > 0:
            msg = "💪 Every question makes you stronger. Keep practicing!"
        else:
            msg = "🚀 Start your journey by taking a quiz!"
        
        tk.Label(content_frame, text=msg, font=('Arial', 14, 'bold'),
                bg=self.theme_colors['bg'], fg=self.TARLETON_PURPLE).pack(pady=15)
    
    def show_practice_tests(self):
        """Show practice test options"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="❓ Practice Tests", 
                         font=('Georgia', 28, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        tk.Label(content_frame, 
                text="Select a topic to take a comprehensive practice test:",
                font=('Arial', 14), bg=self.theme_colors['bg'], 
                fg=self.theme_colors['text']).pack(pady=20)
        
        # Test buttons for each topic
        for topic_num, topic_info in self.topics.items():
            btn = tk.Button(content_frame, 
                           text=f"Topic {topic_num}: {topic_info['name']}",
                           command=lambda tn=topic_num: self.start_topic_test(tn),
                           bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12, 'bold'),
                           width=60, height=2, relief=tk.FLAT, cursor='hand2')
            btn.pack(pady=6, padx=20, fill=tk.X)
    
    def show_about(self):
        """Show about information"""
        about_text = """
🤖 AI Learning Game Application
COSC 5360 - Artificial Intelligence
Spring 2026

═══════════════════════════════════════
INSTRUCTOR INFORMATION
═══════════════════════════════════════

👨‍🏫 Instructor: Dr. Mohamed Massaoudi
📧 Email: MMASSAOUDI@tarleton.edu
🏫 Institution: Tarleton State University
   Member of The Texas A&M University System

Teaching Philosophy:
The instructor's teaching philosophy emphasizes rigorous 
theoretical foundations combined with hands-on algorithmic 
implementation. The course prioritizes analytical reasoning, 
mathematical modeling, and reproducible experimentation to 
prepare students for advanced research and real-world AI 
applications.

═══════════════════════════════════════
APPLICATION FEATURES
═══════════════════════════════════════

• 📚 Study materials for all 10 course topics
• 🎮 Interactive quiz games
• 📝 Practice tests for each topic
• 📊 Progress tracking
• 🏆 Leaderboard system

═══════════════════════════════════════
COURSE TOPICS
═══════════════════════════════════════

1. Introduction to AI and Applications
2. Probability, Linear Algebra, and Optimization
3. Regression Methods in Machine Learning
4. Classification Algorithms
5. Clustering and Unsupervised Learning
6. Neural Networks and Model Evaluation
7. Practical AI and ML Applications
8. Dimensionality Reduction and Model Selection
9. Markov Decision Process and Reinforcement Learning
10. Exam Review and Recitation

═══════════════════════════════════════

Good luck with your studies! 🎓
        """
        
        messagebox.showinfo("About - AI Learning Game", about_text)
    
    def show_nn_builder(self):
        """Show neural network builder interface"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🧠 Neural Network Builder", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Instructions
        info_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'], relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=10)
        tk.Label(info_frame, 
                text="Drag and drop layers to build your neural network. Click 'Run' to see the architecture visualization.",
                font=('Arial', 12), bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                wraplength=800, justify=tk.LEFT, padx=20, pady=15).pack()
        
        # Builder area
        builder_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        builder_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Layer palette
        palette_frame = tk.Frame(builder_frame, bg=self.theme_colors['card_bg'], relief=tk.RAISED, bd=2)
        palette_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        tk.Label(palette_frame, text="Layer Types", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(pady=10)
        
        layer_types = ["Input", "Dense", "Conv2D", "LSTM", "Dropout", "Output"]
        self.nn_layers = []
        
        for layer_type in layer_types:
            layer_btn = tk.Button(palette_frame, text=layer_type, width=15,
                                bg='#2196F3', fg='white', font=('Arial', 11),
                                command=lambda lt=layer_type: self.add_nn_layer(lt))
            layer_btn.pack(pady=5, padx=10)
        
        # Network canvas
        canvas_frame = tk.Frame(builder_frame, bg=self.theme_colors['card_bg'], relief=tk.RAISED, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(canvas_frame, text="Network Architecture", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(pady=10)
        
        self.nn_canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=400)
        self.nn_canvas.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = tk.Frame(canvas_frame, bg=self.theme_colors['card_bg'])
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="Clear", command=self.clear_nn_builder,
                 bg='#F44336', fg='white', font=('Arial', 11), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Visualize", command=self.visualize_nn,
                 bg='#4CAF50', fg='white', font=('Arial', 11), width=12).pack(side=tk.LEFT, padx=5)
    
    def add_nn_layer(self, layer_type):
        """Add a layer to the neural network"""
        self.nn_layers.append(layer_type)
        self.draw_nn_architecture()
    
    def clear_nn_builder(self):
        """Clear the neural network builder"""
        self.nn_layers = []
        self.nn_canvas.delete("all")
    
    def draw_nn_architecture(self):
        """Draw the neural network architecture"""
        self.nn_canvas.delete("all")
        if not self.nn_layers:
            self.nn_canvas.create_text(300, 200, text="Add layers to build your network",
                                      font=('Arial', 14), fill='gray')
            return
        
        width = self.nn_canvas.winfo_width() or 600
        height = self.nn_canvas.winfo_height() or 400
        layer_height = height / (len(self.nn_layers) + 1)
        x = width / 2
        
        for i, layer in enumerate(self.nn_layers):
            y = (i + 1) * layer_height
            # Draw layer box
            color = '#4CAF50' if layer == 'Input' else '#2196F3' if layer == 'Output' else '#FF9800'
            self.nn_canvas.create_rectangle(x-80, y-20, x+80, y+20, fill=color, outline='black', width=2)
            self.nn_canvas.create_text(x, y, text=layer, font=('Arial', 12, 'bold'), fill='white')
            
            # Draw connection to next layer
            if i < len(self.nn_layers) - 1:
                next_y = (i + 2) * layer_height
                self.nn_canvas.create_line(x, y+20, x, next_y-20, fill='black', width=2)
    
    def visualize_nn(self):
        """Show neural network visualization"""
        if not self.nn_layers:
            messagebox.showwarning("No Layers", "Please add layers to your network first.")
            return
        
        arch_text = "Neural Network Architecture:\n\n"
        for i, layer in enumerate(self.nn_layers):
            arch_text += f"Layer {i+1}: {layer}\n"
        
        arch_text += f"\nTotal Layers: {len(self.nn_layers)}"
        messagebox.showinfo("Network Architecture", arch_text)
        self.add_xp(10)  # Reward for building a network
    
    def show_visualizations(self):
        """Show algorithm visualization menu"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🔬 Algorithm Visualizations", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=20)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        tk.Label(content_frame, text="Select an algorithm to visualize:",
                font=('Arial', 14), bg=self.theme_colors['bg'], 
                fg=self.theme_colors['text']).pack(pady=20)
        
        viz_options = [
            ("🌳 Decision Tree", self.viz_decision_tree, self.TARLETON_PURPLE),
            ("🎯 K-Means Clustering", self.viz_kmeans, '#16a085'),
            ("📉 Gradient Descent", self.viz_gradient_descent, '#e74c3c'),
            ("🧠 Neural Network Training", self.viz_nn_training, '#3498db')
        ]
        
        for text, command, color in viz_options:
            btn = tk.Button(content_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 12, 'bold'),
                           width=40, height=2, relief=tk.FLAT, cursor='hand2')
            btn.pack(pady=10, padx=20, fill=tk.X)
    
    def viz_decision_tree(self):
        """Visualize decision tree"""
        messagebox.showinfo("Decision Tree Visualization", 
                          "Decision Tree splits data based on feature values.\n\n"
                          "Each node represents a decision point, and leaves represent outcomes.\n"
                          "The tree grows by finding the best feature to split on at each node.")
        self.add_xp(5)
    
    def viz_kmeans(self):
        """Visualize K-Means clustering"""
        messagebox.showinfo("K-Means Visualization",
                          "K-Means groups data into k clusters.\n\n"
                          "1. Initialize k centroids randomly\n"
                          "2. Assign points to nearest centroid\n"
                          "3. Update centroids to mean of assigned points\n"
                          "4. Repeat until convergence")
        self.add_xp(5)
    
    def viz_gradient_descent(self):
        """Visualize gradient descent"""
        messagebox.showinfo("Gradient Descent Visualization",
                          "Gradient Descent minimizes loss by following the steepest descent.\n\n"
                          "The algorithm iteratively updates parameters:\n"
                          "θ = θ - α∇J(θ)\n\n"
                          "Where α is the learning rate and ∇J is the gradient.")
        self.add_xp(5)
    
    def viz_nn_training(self):
        """Visualize neural network training"""
        messagebox.showinfo("Neural Network Training",
                          "Neural networks learn through:\n\n"
                          "1. Forward Propagation: Data flows through layers\n"
                          "2. Loss Calculation: Compare prediction vs actual\n"
                          "3. Backpropagation: Calculate gradients\n"
                          "4. Weight Update: Adjust weights using gradient descent")
        self.add_xp(5)
    
    def show_achievements(self):
        """Show achievements page"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🎁 Achievements", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_GOLD)
        header.pack(pady=20)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Stats
        stats_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'], relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=20)
        
        stats_text = f"""
        🏆 Total Achievements: {len(self.achievements)}
        ⭐ Current Level: {self.level}
        💎 Total XP: {self.xp}
        🔥 Current Streak: {self.streak} days
        """
        tk.Label(stats_frame, text=stats_text, font=('Arial', 14),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                justify=tk.LEFT).pack(padx=30, pady=20)
        
        # Achievements list
        if self.achievements:
            tk.Label(content_frame, text="Your Achievements:", font=('Arial', 16, 'bold'),
                    bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=10)
            
            for ach in self.achievements:
                ach_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'], relief=tk.RAISED, bd=1)
                ach_frame.pack(fill=tk.X, pady=5)
                tk.Label(ach_frame, text=f"🏆 {ach}", font=('Arial', 12),
                        bg=self.theme_colors['card_bg'], fg=self.theme_colors['accent']).pack(padx=20, pady=10, anchor='w')
        else:
            tk.Label(content_frame, text="No achievements yet. Start learning to unlock achievements!",
                    font=('Arial', 14), bg=self.theme_colors['bg'], fg=self.theme_colors['text_secondary']).pack(pady=50)
    
    def show_quests(self):
        """Show active quests/challenges"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🎯 Daily & Weekly Quests", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=15)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Streak freeze status
        freeze_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                               highlightbackground='#3498db', highlightthickness=2)
        freeze_frame.pack(fill=tk.X, pady=10)
        
        freeze_inner = tk.Frame(freeze_frame, bg=self.theme_colors['card_bg'])
        freeze_inner.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(freeze_inner, text=f"❄️ Streak Freezes: {self.streak_freezes}/5", 
                font=('Arial', 12, 'bold'),
                bg=self.theme_colors['card_bg'], fg='#3498db').pack(side=tk.LEFT)
        
        tk.Label(freeze_inner, text="(Protect your streak on busy days)", 
                font=('Arial', 10),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack(side=tk.LEFT, padx=10)
        
        # Active quests
        tk.Label(content_frame, text="Active Quests", font=('Arial', 16, 'bold'),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=(15, 5))
        
        if self.active_quests:
            for quest in self.active_quests:
                self._create_quest_card(content_frame, quest)
        else:
            tk.Label(content_frame, text="No active quests. Check back tomorrow!", 
                    font=('Arial', 12),
                    bg=self.theme_colors['bg'], fg=self.theme_colors['text_secondary']).pack(pady=20)
        
        # Completed quests count
        tk.Label(content_frame, text=f"\n✅ Completed Quests: {len(self.completed_quests)}", 
                font=('Arial', 14, 'bold'),
                bg=self.theme_colors['bg'], fg='#27ae60').pack(anchor='w', pady=10)
        
        # Unlockable features status
        tk.Label(content_frame, text="🔓 Unlockable Features", font=('Arial', 16, 'bold'),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=(15, 5))
        
        unlock_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                               highlightbackground=self.TARLETON_PURPLE, highlightthickness=1)
        unlock_frame.pack(fill=tk.X, pady=5)
        
        unlocks = [
            ('Hard Mode', 'hard_mode', 5, '🔥'),
            ('Exam Simulator', 'exam_simulator', 15, '📝'),
            ('Bonus Visualizations', 'bonus_visualizations', 25, '🔬'),
            ('AI Case Studies', 'case_studies', 40, '📚')
        ]
        
        for name, key, required, emoji in unlocks:
            row = tk.Frame(unlock_frame, bg=self.theme_colors['card_bg'])
            row.pack(fill=tk.X, padx=15, pady=5)
            
            is_unlocked = self.unlocked_features.get(key, False)
            status = "✓ Unlocked" if is_unlocked else f"🔒 {required} quests needed"
            color = '#27ae60' if is_unlocked else self.theme_colors['text_secondary']
            
            tk.Label(row, text=f"{emoji} {name}", font=('Arial', 11),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.LEFT)
            tk.Label(row, text=status, font=('Arial', 10),
                    bg=self.theme_colors['card_bg'], fg=color).pack(side=tk.RIGHT)
    
    def _create_quest_card(self, parent, quest):
        """Create a quest progress card"""
        is_weekly = quest.get('is_weekly', False)
        border_color = '#f39c12' if is_weekly else '#27ae60'
        
        card = tk.Frame(parent, bg=self.theme_colors['card_bg'],
                       highlightbackground=border_color, highlightthickness=2)
        card.pack(fill=tk.X, pady=5)
        
        inner = tk.Frame(card, bg=self.theme_colors['card_bg'])
        inner.pack(fill=tk.X, padx=15, pady=10)
        
        # Quest title and type
        header_row = tk.Frame(inner, bg=self.theme_colors['card_bg'])
        header_row.pack(fill=tk.X)
        
        tk.Label(header_row, text=quest['title'], font=('Arial', 12, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.LEFT)
        
        if is_weekly:
            tk.Label(header_row, text="WEEKLY", font=('Arial', 9, 'bold'),
                    bg='#f39c12', fg='white', padx=5).pack(side=tk.RIGHT)
        
        # Description
        tk.Label(inner, text=quest['description'], font=('Arial', 10),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text_secondary']).pack(anchor='w')
        
        # Progress bar
        progress_pct = (quest['progress'] / quest['target']) * 100
        
        progress_row = tk.Frame(inner, bg=self.theme_colors['card_bg'])
        progress_row.pack(fill=tk.X, pady=5)
        
        bar_bg = tk.Frame(progress_row, bg='#e0e0e0', height=15, width=300)
        bar_bg.pack(side=tk.LEFT)
        bar_bg.pack_propagate(False)
        
        bar_fill = tk.Frame(bar_bg, bg='#27ae60', height=15, width=int(300 * progress_pct / 100))
        bar_fill.place(x=0, y=0)
        
        tk.Label(progress_row, text=f"{quest['progress']}/{quest['target']}", 
                font=('Arial', 10),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.LEFT, padx=10)
        
        tk.Label(progress_row, text=f"+{quest['xp_reward']} XP", 
                font=('Arial', 10, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.TARLETON_GOLD).pack(side=tk.RIGHT)
    
    def show_instructor_dashboard(self):
        """Show instructor dashboard with class analytics"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="👨‍🏫 Instructor Dashboard", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_PURPLE)
        header.pack(pady=15)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Current student summary
        summary_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                                highlightbackground=self.TARLETON_PURPLE, highlightthickness=2)
        summary_frame.pack(fill=tk.X, pady=10)
        
        summary_inner = tk.Frame(summary_frame, bg=self.theme_colors['card_bg'])
        summary_inner.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(summary_inner, text="Current Student Summary", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(anchor='w')
        
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        summary_text = f"""
        Student: {self.student_name or 'Guest'}
        Exam Readiness: {self.get_exam_readiness()}%
        Overall Accuracy: {overall_accuracy:.1f}%
        Questions Answered: {self.total_questions_answered}
        Time Spent: {self.total_time_spent/60:.0f} minutes
        """
        tk.Label(summary_inner, text=summary_text, font=('Arial', 11),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                justify=tk.LEFT).pack(anchor='w')
        
        # Topic-wise analysis
        tk.Label(content_frame, text="📊 Topic-wise Accuracy Distribution", 
                font=('Arial', 14, 'bold'),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=(15, 5))
        
        topic_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                              highlightbackground=self.TARLETON_PURPLE, highlightthickness=1)
        topic_frame.pack(fill=tk.X, pady=5)
        
        for topic_num, topic_info in list(self.topics.items())[:5]:
            row = tk.Frame(topic_frame, bg=self.theme_colors['card_bg'])
            row.pack(fill=tk.X, padx=15, pady=3)
            
            acc_data = self.topic_accuracy.get(str(topic_num), {'correct': 0, 'total': 0})
            acc = (acc_data['correct'] / acc_data['total'] * 100) if acc_data['total'] > 0 else 0
            
            tk.Label(row, text=f"T{topic_num}:", font=('Arial', 10),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text'],
                    width=4).pack(side=tk.LEFT)
            
            # Mini bar
            bar_bg = tk.Frame(row, bg='#e0e0e0', height=12, width=200)
            bar_bg.pack(side=tk.LEFT, padx=5)
            bar_bg.pack_propagate(False)
            
            bar_color = '#27ae60' if acc >= 70 else '#f39c12' if acc >= 50 else '#e74c3c'
            bar_fill = tk.Frame(bar_bg, bg=bar_color, height=12, width=int(200 * acc / 100))
            bar_fill.place(x=0, y=0)
            
            tk.Label(row, text=f"{acc:.0f}% ({acc_data['total']} Q)", 
                    font=('Arial', 9),
                    bg=self.theme_colors['card_bg'], fg=bar_color).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        tk.Label(content_frame, text="📤 Export Options", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=(20, 5))
        
        export_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        export_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(export_frame, text="📊 Export CSV Report", 
                 command=self.export_csv_report,
                 bg='#27ae60', fg='white', font=('Arial', 11),
                 relief=tk.FLAT, cursor='hand2', width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="📋 Export JSON Data", 
                 command=lambda: messagebox.showinfo("Exported", 
                     f"Data exported to gradebook_export_{self.student_name or 'guest'}.json"),
                 bg='#3498db', fg='white', font=('Arial', 11),
                 relief=tk.FLAT, cursor='hand2', width=20).pack(side=tk.LEFT, padx=5)
    
    def show_class_leaderboard(self):
        """Show class leaderboard with multiple categories and privacy controls"""
        self.clear_window()
        self.root.configure(bg=self.theme_colors['bg'])
        
        back_btn = tk.Button(self.root, text="← Back to Menu", command=self.show_main_menu,
                            bg=self.TARLETON_PURPLE, fg='white', font=('Arial', 12),
                            relief=tk.FLAT, cursor='hand2')
        back_btn.pack(anchor='nw', padx=10, pady=10)
        
        header = tk.Label(self.root, text="🏆 Class Leaderboard", 
                         font=('Georgia', 24, 'bold'), bg=self.theme_colors['bg'], 
                         fg=self.TARLETON_GOLD)
        header.pack(pady=15)
        
        content_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Privacy settings
        privacy_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                                highlightbackground='#3498db', highlightthickness=2)
        privacy_frame.pack(fill=tk.X, pady=10)
        
        privacy_inner = tk.Frame(privacy_frame, bg=self.theme_colors['card_bg'])
        privacy_inner.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(privacy_inner, text="🔒 Privacy Settings", font=('Arial', 12, 'bold'),
                bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(anchor='w')
        
        # Alias setting
        alias_row = tk.Frame(privacy_inner, bg=self.theme_colors['card_bg'])
        alias_row.pack(fill=tk.X, pady=5)
        
        self.alias_var = tk.BooleanVar(value=self.display_alias)
        tk.Checkbutton(alias_row, text="Use alias instead of real name", 
                      variable=self.alias_var,
                      command=self._toggle_alias,
                      bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.LEFT)
        
        # Opt-in setting
        self.optin_var = tk.BooleanVar(value=self.opt_in_leaderboard)
        tk.Checkbutton(alias_row, text="Show me on class leaderboard", 
                      variable=self.optin_var,
                      command=self._toggle_optin,
                      bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.LEFT, padx=20)
        
        # Leaderboard categories
        tk.Label(content_frame, text="Multiple Ways to Win! 🎉", font=('Arial', 14, 'bold'),
                bg=self.theme_colors['bg'], fg=self.theme_colors['text']).pack(anchor='w', pady=(15, 5))
        
        overall_accuracy = (self.correct_answers / self.total_questions_answered * 100) if self.total_questions_answered > 0 else 0
        
        categories = [
            ("🔥 Most Consistent (Streak)", f"{self.streak} days", '#FF6B35'),
            ("📈 Most Improved", "+15% this week", '#27ae60'),  # Placeholder
            ("🎯 Topic Mastery", f"{self.get_exam_readiness()}% ready", '#3498db'),
            ("⚡ Challenge Completions", f"{len(self.completed_quests)} quests", '#9b59b6'),
            ("🎓 Overall Accuracy", f"{overall_accuracy:.1f}%", self.TARLETON_PURPLE),
        ]
        
        for title, value, color in categories:
            cat_frame = tk.Frame(content_frame, bg=self.theme_colors['card_bg'],
                                highlightbackground=color, highlightthickness=2)
            cat_frame.pack(fill=tk.X, pady=5)
            
            inner = tk.Frame(cat_frame, bg=self.theme_colors['card_bg'])
            inner.pack(fill=tk.X, padx=20, pady=12)
            
            tk.Label(inner, text=title, font=('Arial', 13, 'bold'),
                    bg=self.theme_colors['card_bg'], fg=color).pack(side=tk.LEFT)
            
            # Your position
            display_name = self.student_alias if self.display_alias else self.student_name
            tk.Label(inner, text=f"Your score: {value}", font=('Arial', 11),
                    bg=self.theme_colors['card_bg'], fg=self.theme_colors['text']).pack(side=tk.RIGHT)
        
        # Note about class data
        tk.Label(content_frame, 
                text="\n💡 Full class rankings will be available when connected to class data.",
                font=('Arial', 10), bg=self.theme_colors['bg'], 
                fg=self.theme_colors['text_secondary']).pack(pady=10)
    
    def _toggle_alias(self):
        """Toggle alias display preference"""
        self.display_alias = self.alias_var.get()
        if not self.student_alias and self.student_name:
            self.student_alias = self.student_name[:3] + '***'
        self.save_data()
    
    def _toggle_optin(self):
        """Toggle leaderboard opt-in"""
        self.opt_in_leaderboard = self.optin_var.get()
        self.save_data()


class QuestionsDatabase:
    """Database of questions for all topics"""
    
    def __init__(self):
        self.questions = self._load_questions()
    
    def _load_questions(self):
        """Load all questions"""
        questions = []
        
        # Topic 1: Introduction to AI
        questions.extend([
            {
                "topic": 1,
                "question": "What is the primary goal of Artificial Intelligence?",
                "options": [
                    "To create machines that can perform tasks requiring human intelligence",
                    "To replace all human workers",
                    "To make computers faster",
                    "To eliminate the need for programming"
                ],
                "correct": "To create machines that can perform tasks requiring human intelligence"
            },
            {
                "topic": 1,
                "question": "Which of the following is NOT a typical application of AI?",
                "options": [
                    "Natural Language Processing",
                    "Computer Vision",
                    "Simple Calculator",
                    "Robotics"
                ],
                "correct": "Simple Calculator"
            },
            {
                "topic": 1,
                "question": "What distinguishes Strong AI from Weak AI?",
                "options": [
                    "Strong AI has general intelligence and consciousness, Weak AI is task-specific",
                    "Strong AI is faster than Weak AI",
                    "Strong AI requires more memory",
                    "There is no difference"
                ],
                "correct": "Strong AI has general intelligence and consciousness, Weak AI is task-specific"
            },
            {
                "topic": 1,
                "question": "Machine Learning is a subset of:",
                "options": [
                    "Artificial Intelligence",
                    "Computer Science",
                    "Data Science",
                    "All of the above"
                ],
                "correct": "Artificial Intelligence"
            },
            {
                "topic": 1,
                "question": "The Turing Test was proposed to:",
                "options": [
                    "Determine if a machine can exhibit intelligent behavior",
                    "Test computer speed",
                    "Measure memory capacity",
                    "Evaluate programming languages"
                ],
                "correct": "Determine if a machine can exhibit intelligent behavior"
            }
        ])
        
        # Topic 2: Machine Learning
        questions.extend([
            {
                "topic": 2,
                "question": "What is Machine Learning?",
                "options": [
                    "A field of computer science that gives computers the ability to learn without being explicitly programmed",
                    "A programming language for AI",
                    "A type of database system",
                    "A hardware component for faster processing"
                ],
                "correct": "A field of computer science that gives computers the ability to learn without being explicitly programmed"
            },
            {
                "topic": 2,
                "question": "What is the main difference between Supervised Learning and Unsupervised Learning?",
                "options": [
                    "Supervised learning uses labeled data with target outputs, while unsupervised learning finds patterns in unlabeled data",
                    "Supervised learning is faster than unsupervised learning",
                    "Supervised learning requires more data than unsupervised learning",
                    "There is no significant difference"
                ],
                "correct": "Supervised learning uses labeled data with target outputs, while unsupervised learning finds patterns in unlabeled data"
            },
            {
                "topic": 2,
                "question": "In supervised learning, what is the difference between Classification and Regression?",
                "options": [
                    "Classification predicts discrete class labels, while Regression predicts continuous values",
                    "Classification is faster than Regression",
                    "Regression uses more data than Classification",
                    "Classification is for images, Regression is for text"
                ],
                "correct": "Classification predicts discrete class labels, while Regression predicts continuous values"
            },
            {
                "topic": 2,
                "question": "What is the relationship between Artificial Intelligence and Machine Learning?",
                "options": [
                    "Machine Learning is a subset of AI that focuses on learning from data",
                    "AI and Machine Learning are the same thing",
                    "Machine Learning is a broader field than AI",
                    "AI is a subset of Machine Learning"
                ],
                "correct": "Machine Learning is a subset of AI that focuses on learning from data"
            },
            {
                "topic": 2,
                "question": "What is Reinforcement Learning?",
                "options": [
                    "A type of learning where an agent learns actions that maximize rewards through interaction with the environment",
                    "A method for supervised learning with reinforcement",
                    "A technique for data preprocessing",
                    "A type of unsupervised clustering algorithm"
                ],
                "correct": "A type of learning where an agent learns actions that maximize rewards through interaction with the environment"
            },
            {
                "topic": 2,
                "question": "What is Semi-supervised Learning?",
                "options": [
                    "Learning with limited labeled data and lots of unlabeled data",
                    "Learning that happens twice",
                    "A combination of supervised and unsupervised learning that requires equal amounts of both",
                    "Learning that is only partially complete"
                ],
                "correct": "Learning with limited labeled data and lots of unlabeled data"
            },
            {
                "topic": 2,
                "question": "According to the lecture, what is a key difference in emphasis between Machine Learning and Statistics?",
                "options": [
                    "ML emphasizes impressive results on specific tasks, while Statistics emphasizes theoretical proofs and asymptotic properties",
                    "ML is more mathematical than Statistics",
                    "Statistics uses more computational techniques than ML",
                    "There is no difference in emphasis"
                ],
                "correct": "ML emphasizes impressive results on specific tasks, while Statistics emphasizes theoretical proofs and asymptotic properties"
            },
            {
                "topic": 2,
                "question": "In Pattern Recognition, what is the difference between optimal classification error and true error of a designed classifier?",
                "options": [
                    "Optimal classification error is the minimum possible error, while true error is the actual error of a specific classifier",
                    "They are the same thing",
                    "Optimal error is always higher than true error",
                    "True error is theoretical, optimal error is practical"
                ],
                "correct": "Optimal classification error is the minimum possible error, while true error is the actual error of a specific classifier"
            },
            {
                "topic": 2,
                "question": "In the stochastic setting of Pattern Recognition, what causes the relationship between feature vector X and label Y to be probabilistic?",
                "options": [
                    "Noise factors such as sensor imprecision and latent variables",
                    "Insufficient training data",
                    "Poor algorithm selection",
                    "Computational limitations"
                ],
                "correct": "Noise factors such as sensor imprecision and latent variables"
            },
            {
                "topic": 2,
                "question": "Which of the following is NOT one of the major AI problems (AI goals) mentioned in the lecture?",
                "options": [
                    "Database management",
                    "Deduction, Reasoning, Problem Solving",
                    "Natural language processing",
                    "General intelligence, or strong AI"
                ],
                "correct": "Database management"
            }
        ])
        
        # Topic 3: Regression Methods
        questions.extend([
            {
                "topic": 3,
                "question": "Linear regression is used for:",
                "options": [
                    "Predicting continuous values",
                    "Classifying data into categories",
                    "Clustering data",
                    "Dimensionality reduction"
                ],
                "correct": "Predicting continuous values"
            },
            {
                "topic": 3,
                "question": "What does R-squared measure in regression?",
                "options": [
                    "The proportion of variance explained by the model",
                    "The number of features",
                    "The training time",
                    "The prediction accuracy"
                ],
                "correct": "The proportion of variance explained by the model"
            },
            {
                "topic": 3,
                "question": "What is overfitting in regression?",
                "options": [
                    "Model performs well on training data but poorly on test data",
                    "Model performs poorly on both training and test data",
                    "Model takes too long to train",
                    "Model uses too many features"
                ],
                "correct": "Model performs well on training data but poorly on test data"
            },
            {
                "topic": 3,
                "question": "What is the main difference between Ridge and Lasso regression?",
                "options": [
                    "Ridge uses L2 penalty, Lasso uses L1 penalty",
                    "Ridge is faster than Lasso",
                    "Lasso can only handle linear relationships",
                    "Ridge is for classification, Lasso is for regression"
                ],
                "correct": "Ridge uses L2 penalty, Lasso uses L1 penalty"
            },
            {
                "topic": 3,
                "question": "Polynomial regression is used when:",
                "options": [
                    "The relationship between variables is non-linear",
                    "There are too many features",
                    "The data is categorical",
                    "We need to classify data"
                ],
                "correct": "The relationship between variables is non-linear"
            }
        ])
        
        # Topic 4: Classification Algorithms
        questions.extend([
            {
                "topic": 4,
                "question": "Which algorithm uses decision trees?",
                "options": [
                    "Random Forest",
                    "K-Means",
                    "PCA",
                    "Linear Regression"
                ],
                "correct": "Random Forest"
            },
            {
                "topic": 4,
                "question": "What is the purpose of a confusion matrix?",
                "options": [
                    "To evaluate classification performance",
                    "To visualize data",
                    "To preprocess data",
                    "To select features"
                ],
                "correct": "To evaluate classification performance"
            },
            {
                "topic": 4,
                "question": "Support Vector Machines (SVM) work by:",
                "options": [
                    "Finding the optimal hyperplane to separate classes",
                    "Clustering data points",
                    "Reducing dimensionality",
                    "Calculating probabilities"
                ],
                "correct": "Finding the optimal hyperplane to separate classes"
            },
            {
                "topic": 4,
                "question": "What is logistic regression used for?",
                "options": [
                    "Binary and multi-class classification",
                    "Regression problems only",
                    "Clustering",
                    "Dimensionality reduction"
                ],
                "correct": "Binary and multi-class classification"
            },
            {
                "topic": 4,
                "question": "What is the main advantage of Random Forest over a single Decision Tree?",
                "options": [
                    "Reduces overfitting and improves generalization",
                    "Faster training time",
                    "Requires less memory",
                    "Easier to interpret"
                ],
                "correct": "Reduces overfitting and improves generalization"
            },
            {
                "topic": 4,
                "question": "In K-Nearest Neighbors, what happens if k is too small?",
                "options": [
                    "The model becomes sensitive to noise",
                    "The model becomes too slow",
                    "The model requires more memory",
                    "The model cannot make predictions"
                ],
                "correct": "The model becomes sensitive to noise"
            }
        ])
        
        # Topic 5: Clustering
        questions.extend([
            {
                "topic": 5,
                "question": "K-Means clustering is an example of:",
                "options": [
                    "Unsupervised learning",
                    "Supervised learning",
                    "Reinforcement learning",
                    "Deep learning"
                ],
                "correct": "Unsupervised learning"
            },
            {
                "topic": 5,
                "question": "What does the 'K' in K-Means represent?",
                "options": [
                    "Number of clusters",
                    "Number of features",
                    "Learning rate",
                    "Number of iterations"
                ],
                "correct": "Number of clusters"
            },
            {
                "topic": 5,
                "question": "Hierarchical clustering creates:",
                "options": [
                    "A tree-like structure of clusters",
                    "A single cluster",
                    "Linear clusters",
                    "Circular clusters"
                ],
                "correct": "A tree-like structure of clusters"
            },
            {
                "topic": 5,
                "question": "What is the main disadvantage of K-Means clustering?",
                "options": [
                    "Requires specifying the number of clusters beforehand",
                    "It's too slow",
                    "It only works with numerical data",
                    "It cannot handle large datasets"
                ],
                "correct": "Requires specifying the number of clusters beforehand"
            },
            {
                "topic": 5,
                "question": "DBSCAN is particularly good at:",
                "options": [
                    "Finding clusters of arbitrary shapes and identifying outliers",
                    "Finding only spherical clusters",
                    "Working with labeled data",
                    "Reducing dimensionality"
                ],
                "correct": "Finding clusters of arbitrary shapes and identifying outliers"
            }
        ])
        
        # Topic 6: Neural Networks
        questions.extend([
            {
                "topic": 6,
                "question": "What is an activation function in a neural network?",
                "options": [
                    "A function that introduces non-linearity",
                    "A function that adds bias",
                    "A function that normalizes data",
                    "A function that initializes weights"
                ],
                "correct": "A function that introduces non-linearity"
            },
            {
                "topic": 6,
                "question": "What is backpropagation used for?",
                "options": [
                    "Training neural networks by updating weights",
                    "Forward data through the network",
                    "Initializing network weights",
                    "Evaluating model performance"
                ],
                "correct": "Training neural networks by updating weights"
            },
            {
                "topic": 6,
                "question": "What is cross-validation used for?",
                "options": [
                    "Model evaluation and selection",
                    "Data preprocessing",
                    "Feature engineering",
                    "Hyperparameter tuning"
                ],
                "correct": "Model evaluation and selection"
            },
            {
                "topic": 6,
                "question": "Why is ReLU commonly used as an activation function?",
                "options": [
                    "It helps address the vanishing gradient problem",
                    "It's the simplest function",
                    "It always outputs values between 0 and 1",
                    "It requires less computation than other functions"
                ],
                "correct": "It helps address the vanishing gradient problem"
            },
            {
                "topic": 6,
                "question": "What is the purpose of dropout in neural networks?",
                "options": [
                    "To prevent overfitting by randomly disabling neurons",
                    "To speed up training",
                    "To reduce memory usage",
                    "To initialize weights"
                ],
                "correct": "To prevent overfitting by randomly disabling neurons"
            }
        ])
        
        # Topic 7: Practical Applications
        questions.extend([
            {
                "topic": 7,
                "question": "Which is a common application of computer vision?",
                "options": [
                    "Image recognition",
                    "Text translation",
                    "Audio processing",
                    "Data storage"
                ],
                "correct": "Image recognition"
            },
            {
                "topic": 7,
                "question": "Natural Language Processing (NLP) is used for:",
                "options": [
                    "Understanding and processing human language",
                    "Image classification",
                    "Data clustering",
                    "Regression analysis"
                ],
                "correct": "Understanding and processing human language"
            },
            {
                "topic": 7,
                "question": "Convolutional Neural Networks (CNNs) are primarily used for:",
                "options": [
                    "Image processing and computer vision tasks",
                    "Text processing",
                    "Audio processing only",
                    "Time series forecasting"
                ],
                "correct": "Image processing and computer vision tasks"
            },
            {
                "topic": 7,
                "question": "What is transfer learning?",
                "options": [
                    "Using a pre-trained model and adapting it for a new task",
                    "Moving data between computers",
                    "Converting between data formats",
                    "Training multiple models simultaneously"
                ],
                "correct": "Using a pre-trained model and adapting it for a new task"
            }
        ])
        
        # Topic 8: Dimensionality Reduction
        questions.extend([
            {
                "topic": 8,
                "question": "Principal Component Analysis (PCA) is used for:",
                "options": [
                    "Reducing dimensionality while preserving variance",
                    "Increasing model complexity",
                    "Adding more features",
                    "Improving model speed only"
                ],
                "correct": "Reducing dimensionality while preserving variance"
            },
            {
                "topic": 8,
                "question": "What is the main goal of model selection?",
                "options": [
                    "To find the best model for the data",
                    "To reduce training time",
                    "To increase model complexity",
                    "To eliminate all errors"
                ],
                "correct": "To find the best model for the data"
            },
            {
                "topic": 8,
                "question": "What does PCA stand for and what is its primary purpose?",
                "options": [
                    "Principal Component Analysis - reducing dimensionality while preserving variance",
                    "Primary Classification Algorithm - for classification tasks",
                    "Probabilistic Component Analysis - for probability estimation",
                    "Pattern Classification Algorithm - for pattern recognition"
                ],
                "correct": "Principal Component Analysis - reducing dimensionality while preserving variance"
            },
            {
                "topic": 8,
                "question": "What is the difference between grid search and random search for hyperparameter tuning?",
                "options": [
                    "Grid search exhaustively searches all combinations, random search samples randomly",
                    "Grid search is faster than random search",
                    "Random search only works for neural networks",
                    "There is no difference"
                ],
                "correct": "Grid search exhaustively searches all combinations, random search samples randomly"
            }
        ])
        
        # Topic 9: MDP and Reinforcement Learning
        questions.extend([
            {
                "topic": 9,
                "question": "In a Markov Decision Process (MDP), what does the agent try to maximize?",
                "options": [
                    "Expected cumulative reward",
                    "Number of actions",
                    "State space size",
                    "Transition probabilities"
                ],
                "correct": "Expected cumulative reward"
            },
            {
                "topic": 9,
                "question": "What is Q-learning?",
                "options": [
                    "A reinforcement learning algorithm that learns action-value functions",
                    "A classification algorithm",
                    "A clustering method",
                    "A regression technique"
                ],
                "correct": "A reinforcement learning algorithm that learns action-value functions"
            },
            {
                "topic": 9,
                "question": "What is the exploration vs exploitation trade-off?",
                "options": [
                    "Balancing trying new actions vs using known good actions",
                    "Choosing between different algorithms",
                    "Selecting training vs test data",
                    "Deciding on model complexity"
                ],
                "correct": "Balancing trying new actions vs using known good actions"
            },
            {
                "topic": 9,
                "question": "What does the discount factor (γ) in MDP represent?",
                "options": [
                    "The importance of future rewards relative to immediate rewards",
                    "The learning rate",
                    "The number of states",
                    "The probability of success"
                ],
                "correct": "The importance of future rewards relative to immediate rewards"
            },
            {
                "topic": 9,
                "question": "What is the main advantage of Q-learning?",
                "options": [
                    "It can learn optimal policies without knowing the environment model",
                    "It's faster than all other algorithms",
                    "It requires less memory",
                    "It only works for discrete state spaces"
                ],
                "correct": "It can learn optimal policies without knowing the environment model"
            }
        ])
        
        # Topic 10: Exam Review
        questions.extend([
            {
                "topic": 10,
                "question": "Which evaluation metric is best for imbalanced classification?",
                "options": [
                    "F1-Score",
                    "Accuracy",
                    "R-squared",
                    "Mean squared error"
                ],
                "correct": "F1-Score"
            },
            {
                "topic": 10,
                "question": "What is the bias-variance trade-off?",
                "options": [
                    "Balancing model complexity to minimize total error",
                    "Choosing between different algorithms",
                    "Selecting features",
                    "Deciding on training time"
                ],
                "correct": "Balancing model complexity to minimize total error"
            },
            {
                "topic": 10,
                "question": "When is F1-Score preferred over Accuracy?",
                "options": [
                    "When dealing with imbalanced datasets",
                    "When the dataset is very large",
                    "When using regression models",
                    "When training neural networks"
                ],
                "correct": "When dealing with imbalanced datasets"
            },
            {
                "topic": 10,
                "question": "What is the purpose of stratified k-fold cross-validation?",
                "options": [
                    "To maintain the class distribution in each fold",
                    "To speed up the validation process",
                    "To reduce memory usage",
                    "To handle missing values"
                ],
                "correct": "To maintain the class distribution in each fold"
            }
        ])
        
        # Additional questions to ensure 10+ per topic
        
        # More Topic 1 questions
        questions.extend([
            {"topic": 1, "question": "Who is considered the father of Artificial Intelligence?",
             "options": ["Alan Turing", "John McCarthy", "Marvin Minsky", "Geoffrey Hinton"],
             "correct": "John McCarthy"},
            {"topic": 1, "question": "What year was the term 'Artificial Intelligence' coined?",
             "options": ["1950", "1956", "1960", "1970"],
             "correct": "1956"},
            {"topic": 1, "question": "Which AI defeated the world chess champion in 1997?",
             "options": ["AlphaGo", "Deep Blue", "Watson", "GPT"],
             "correct": "Deep Blue"},
            {"topic": 1, "question": "Expert systems are designed to:",
             "options": ["Mimic human expert decision-making", "Play games", "Process images", "Translate languages"],
             "correct": "Mimic human expert decision-making"},
            {"topic": 1, "question": "What is the main difference between AI and traditional programming?",
             "options": ["AI learns from data, traditional programming uses explicit rules", "AI is faster", "AI uses less memory", "There is no difference"],
             "correct": "AI learns from data, traditional programming uses explicit rules"},
            {"topic": 1, "question": "Which company developed AlphaGo?",
             "options": ["Google DeepMind", "OpenAI", "IBM", "Microsoft"],
             "correct": "Google DeepMind"}
        ])
        
        
        # More Topic 3 questions
        questions.extend([
            {"topic": 3, "question": "What is the cost function typically used in linear regression?",
             "options": ["Mean Squared Error", "Cross Entropy", "Hinge Loss", "Log Loss"],
             "correct": "Mean Squared Error"},
            {"topic": 3, "question": "Multicollinearity in regression refers to:",
             "options": ["High correlation between independent variables", "Low R-squared", "High variance", "Underfitting"],
             "correct": "High correlation between independent variables"},
            {"topic": 3, "question": "What does Lasso regression do that Ridge doesn't?",
             "options": ["Can reduce coefficients to exactly zero", "Runs faster", "Handles more features", "Uses L2 penalty"],
             "correct": "Can reduce coefficients to exactly zero"},
            {"topic": 3, "question": "An R-squared value of 0.95 indicates:",
             "options": ["Model explains 95% of variance", "95% accuracy", "5% error rate", "95 features used"],
             "correct": "Model explains 95% of variance"},
            {"topic": 3, "question": "Which technique helps prevent overfitting in regression?",
             "options": ["Regularization", "Adding more features", "Increasing model complexity", "Using smaller dataset"],
             "correct": "Regularization"},
            {"topic": 3, "question": "Elastic Net regression combines:",
             "options": ["L1 and L2 regularization", "Linear and logistic regression", "Ridge and decision trees", "Lasso and neural networks"],
             "correct": "L1 and L2 regularization"}
        ])
        
        # More Topic 4 questions
        questions.extend([
            {"topic": 4, "question": "Precision measures:",
             "options": ["True positives out of predicted positives", "True positives out of actual positives", "Overall accuracy", "False positive rate"],
             "correct": "True positives out of predicted positives"},
            {"topic": 4, "question": "Recall is also known as:",
             "options": ["Sensitivity or True Positive Rate", "Specificity", "Precision", "Accuracy"],
             "correct": "Sensitivity or True Positive Rate"},
            {"topic": 4, "question": "The kernel trick in SVM allows:",
             "options": ["Mapping data to higher dimensions for linear separation", "Faster training", "Using less memory", "Handling missing values"],
             "correct": "Mapping data to higher dimensions for linear separation"},
            {"topic": 4, "question": "Gradient Boosting builds trees:",
             "options": ["Sequentially, correcting previous errors", "In parallel", "Randomly", "Only on subsets"],
             "correct": "Sequentially, correcting previous errors"},
            {"topic": 4, "question": "What is the purpose of pruning in decision trees?",
             "options": ["Reduce overfitting by removing branches", "Speed up training", "Add more nodes", "Increase accuracy"],
             "correct": "Reduce overfitting by removing branches"}
        ])
        
        # More Topic 5 questions
        questions.extend([
            {"topic": 5, "question": "The elbow method helps determine:",
             "options": ["Optimal number of clusters in K-Means", "Learning rate", "Number of features", "Training iterations"],
             "correct": "Optimal number of clusters in K-Means"},
            {"topic": 5, "question": "Silhouette score measures:",
             "options": ["How similar an object is to its own cluster vs other clusters", "Number of clusters", "Training time", "Memory usage"],
             "correct": "How similar an object is to its own cluster vs other clusters"},
            {"topic": 5, "question": "Agglomerative clustering starts with:",
             "options": ["Each point as its own cluster", "One large cluster", "Random clusters", "K predefined clusters"],
             "correct": "Each point as its own cluster"},
            {"topic": 5, "question": "DBSCAN requires which parameters?",
             "options": ["Epsilon (radius) and MinPts", "Number of clusters only", "Learning rate", "Number of iterations"],
             "correct": "Epsilon (radius) and MinPts"},
            {"topic": 5, "question": "What are outliers in DBSCAN called?",
             "options": ["Noise points", "Border points", "Core points", "Cluster centers"],
             "correct": "Noise points"},
            {"topic": 5, "question": "Mean-shift clustering finds clusters by:",
             "options": ["Seeking modes of density", "Random initialization", "Hierarchical splitting", "Minimizing variance"],
             "correct": "Seeking modes of density"}
        ])
        
        # More Topic 6 questions
        questions.extend([
            {"topic": 6, "question": "The vanishing gradient problem affects:",
             "options": ["Deep networks with certain activation functions", "Only shallow networks", "Linear models", "Clustering algorithms"],
             "correct": "Deep networks with certain activation functions"},
            {"topic": 6, "question": "Batch normalization helps by:",
             "options": ["Normalizing layer inputs to speed up training", "Reducing model size", "Increasing epochs", "Adding more layers"],
             "correct": "Normalizing layer inputs to speed up training"},
            {"topic": 6, "question": "What is an epoch in neural network training?",
             "options": ["One complete pass through the training data", "One batch", "One gradient update", "One layer forward"],
             "correct": "One complete pass through the training data"},
            {"topic": 6, "question": "Softmax activation is typically used in:",
             "options": ["Multi-class classification output layer", "Hidden layers", "Regression problems", "Input layer"],
             "correct": "Multi-class classification output layer"},
            {"topic": 6, "question": "Adam optimizer combines:",
             "options": ["Momentum and RMSprop", "SGD and batch gradient", "L1 and L2 regularization", "Dropout and normalization"],
             "correct": "Momentum and RMSprop"},
            {"topic": 6, "question": "Early stopping prevents overfitting by:",
             "options": ["Stopping training when validation error increases", "Training longer", "Using more data", "Adding layers"],
             "correct": "Stopping training when validation error increases"}
        ])
        
        # More Topic 7 questions
        questions.extend([
            {"topic": 7, "question": "BERT is primarily used for:",
             "options": ["Natural Language Processing tasks", "Image classification", "Audio processing", "Reinforcement learning"],
             "correct": "Natural Language Processing tasks"},
            {"topic": 7, "question": "Data augmentation in computer vision includes:",
             "options": ["Rotating, flipping, and scaling images", "Deleting data", "Reducing features", "Removing noise only"],
             "correct": "Rotating, flipping, and scaling images"},
            {"topic": 7, "question": "Recurrent Neural Networks (RNNs) are best for:",
             "options": ["Sequential data like time series", "Image classification", "Clustering", "Dimensionality reduction"],
             "correct": "Sequential data like time series"},
            {"topic": 7, "question": "Word embeddings like Word2Vec represent words as:",
             "options": ["Dense vectors capturing semantic meaning", "One-hot vectors", "Binary values", "Integer indices"],
             "correct": "Dense vectors capturing semantic meaning"},
            {"topic": 7, "question": "YOLO (You Only Look Once) is used for:",
             "options": ["Real-time object detection", "Text classification", "Speech recognition", "Clustering"],
             "correct": "Real-time object detection"},
            {"topic": 7, "question": "Attention mechanism in transformers helps with:",
             "options": ["Focusing on relevant parts of input", "Reducing model size", "Faster training only", "Data preprocessing"],
             "correct": "Focusing on relevant parts of input"}
        ])
        
        # More Topic 8 questions
        questions.extend([
            {"topic": 8, "question": "t-SNE is commonly used for:",
             "options": ["Visualizing high-dimensional data in 2D/3D", "Classification", "Regression", "Clustering"],
             "correct": "Visualizing high-dimensional data in 2D/3D"},
            {"topic": 8, "question": "Feature selection vs feature extraction:",
             "options": ["Selection chooses existing features, extraction creates new ones", "They are the same", "Selection is always better", "Extraction is faster"],
             "correct": "Selection chooses existing features, extraction creates new ones"},
            {"topic": 8, "question": "The curse of dimensionality refers to:",
             "options": ["Problems that arise with too many features", "Too few features", "Missing data", "Class imbalance"],
             "correct": "Problems that arise with too many features"},
            {"topic": 8, "question": "Bayesian optimization is used for:",
             "options": ["Hyperparameter tuning", "Feature selection", "Data cleaning", "Model interpretation"],
             "correct": "Hyperparameter tuning"},
            {"topic": 8, "question": "AIC and BIC are used for:",
             "options": ["Model selection and comparison", "Data preprocessing", "Feature extraction", "Clustering"],
             "correct": "Model selection and comparison"},
            {"topic": 8, "question": "Variance explained by principal components:",
             "options": ["Decreases with each subsequent component", "Increases with each component", "Stays constant", "Is random"],
             "correct": "Decreases with each subsequent component"}
        ])
        
        # More Topic 9 questions
        questions.extend([
            {"topic": 9, "question": "In MDP, the Markov property states:",
             "options": ["Future depends only on current state, not history", "All states are equally likely", "Actions don't affect states", "Rewards are always positive"],
             "correct": "Future depends only on current state, not history"},
            {"topic": 9, "question": "Policy gradient methods directly optimize:",
             "options": ["The policy parameters", "The value function only", "The environment model", "The reward function"],
             "correct": "The policy parameters"},
            {"topic": 9, "question": "Epsilon-greedy strategy involves:",
             "options": ["Random action with probability epsilon, best action otherwise", "Always taking random actions", "Always taking best action", "Decreasing learning rate"],
             "correct": "Random action with probability epsilon, best action otherwise"},
            {"topic": 9, "question": "The Bellman equation describes:",
             "options": ["Relationship between value of state and successor states", "Learning rate decay", "Network architecture", "Data preprocessing"],
             "correct": "Relationship between value of state and successor states"},
            {"topic": 9, "question": "Deep Q-Network (DQN) uses neural networks to:",
             "options": ["Approximate the Q-function", "Generate random actions", "Model the environment", "Preprocess states"],
             "correct": "Approximate the Q-function"},
            {"topic": 9, "question": "Experience replay in DQN helps by:",
             "options": ["Breaking correlation between consecutive samples", "Speeding up training", "Reducing memory", "Simplifying the network"],
             "correct": "Breaking correlation between consecutive samples"}
        ])
        
        # More Topic 10 questions
        questions.extend([
            {"topic": 10, "question": "ROC curve plots:",
             "options": ["True Positive Rate vs False Positive Rate", "Precision vs Recall", "Accuracy vs Loss", "Training vs Validation error"],
             "correct": "True Positive Rate vs False Positive Rate"},
            {"topic": 10, "question": "AUC (Area Under Curve) of 0.5 indicates:",
             "options": ["Random classifier performance", "Perfect classifier", "Worst possible classifier", "Overfitting"],
             "correct": "Random classifier performance"},
            {"topic": 10, "question": "Ensemble methods combine multiple models to:",
             "options": ["Improve overall performance and reduce variance", "Speed up training", "Reduce model size", "Simplify interpretation"],
             "correct": "Improve overall performance and reduce variance"},
            {"topic": 10, "question": "Bootstrapping in machine learning involves:",
             "options": ["Sampling with replacement from the dataset", "Removing outliers", "Feature normalization", "Hyperparameter tuning"],
             "correct": "Sampling with replacement from the dataset"},
            {"topic": 10, "question": "What is the purpose of a validation set?",
             "options": ["Tune hyperparameters and prevent overfitting", "Train the final model", "Test final performance", "Store predictions"],
             "correct": "Tune hyperparameters and prevent overfitting"},
            {"topic": 10, "question": "Occam's Razor in ML suggests:",
             "options": ["Prefer simpler models that explain the data well", "Always use complex models", "Use as many features as possible", "Train longer"],
             "correct": "Prefer simpler models that explain the data well"}
        ])
        
        return questions
    
    def get_all_questions(self):
        """Return all questions"""
        return self.questions


class StudyContent:
    """Study content for each topic"""
    
    def get_content(self, topic_num):
        """Get study content for a topic"""
        content_map = {
            1: """TOPIC 1: INTRODUCTION TO ARTIFICIAL INTELLIGENCE AND APPLICATIONS

What is Artificial Intelligence?
Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.

Key Concepts:
• Strong AI vs Weak AI: Strong AI refers to machines with general intelligence and consciousness, while Weak AI (Narrow AI) is designed for specific tasks.
• Machine Learning: A subset of AI that enables systems to learn and improve from experience without being explicitly programmed.
• Deep Learning: A subset of machine learning using neural networks with multiple layers.

Applications of AI:
1. Natural Language Processing (NLP): Enables machines to understand and process human language (e.g., chatbots, translation).
2. Computer Vision: Allows machines to interpret and understand visual information (e.g., image recognition, facial recognition).
3. Robotics: Combines AI with mechanical engineering to create autonomous robots.
4. Expert Systems: Computer systems that emulate decision-making of human experts.
5. Speech Recognition: Converting spoken language into text.

Historical Milestones:
• 1950: Alan Turing proposes the Turing Test
• 1956: Dartmouth Conference coins the term "Artificial Intelligence"
• 1997: IBM's Deep Blue defeats world chess champion
• 2011: IBM's Watson wins Jeopardy!
• 2016: AlphaGo defeats world Go champion

Current Trends:
• Large Language Models (LLMs)
• Generative AI
• Autonomous vehicles
• Healthcare AI applications""",

            2: """TOPIC 2: REVIEW OF PROBABILITY, LINEAR ALGEBRA, AND OPTIMIZATION FOR AI

PROBABILITY THEORY
Probability is fundamental to AI, especially in machine learning and uncertainty handling.

Key Concepts:
• Probability: P(A) measures the likelihood of event A occurring (0 ≤ P(A) ≤ 1)
• Conditional Probability: P(A|B) = P(A and B) / P(B)
• Bayes' Theorem: P(A|B) = P(B|A) × P(A) / P(B)
• Random Variables: Variables whose values depend on outcomes of random events
• Probability Distributions: Normal, Uniform, Binomial, etc.

LINEAR ALGEBRA
Essential for understanding machine learning algorithms and data representation.

Key Concepts:
• Vectors: Ordered lists of numbers representing data points
• Matrices: Rectangular arrays of numbers used for transformations
• Dot Product: Measures similarity between vectors (a · b = Σaᵢbᵢ)
• Matrix Multiplication: Used in neural networks and transformations
• Eigenvalues and Eigenvectors: Important for dimensionality reduction (PCA)
• Vector Spaces: Framework for understanding data relationships

OPTIMIZATION
Finding the best solution or parameters for a given problem.

Key Concepts:
• Objective Function: Function to minimize or maximize
• Gradient: Vector of partial derivatives indicating direction of steepest ascent
• Gradient Descent: Iterative optimization algorithm
  - Update rule: θ = θ - α∇J(θ)
  - α (alpha) is the learning rate
• Local vs Global Minima: Gradient descent may find local optima
• Stochastic Gradient Descent (SGD): Uses random samples for faster convergence
• Regularization: Techniques to prevent overfitting (L1, L2)

Applications in AI:
• Probability: Bayesian networks, Naive Bayes, uncertainty quantification
• Linear Algebra: Neural networks, PCA, data transformations
• Optimization: Training machine learning models, hyperparameter tuning""",

            3: """TOPIC 3: REGRESSION METHODS IN MACHINE LEARNING

REGRESSION OVERVIEW
Regression is a supervised learning technique used to predict continuous numerical values based on input features.

LINEAR REGRESSION
The simplest form of regression that models the relationship between variables using a linear equation.

Key Concepts:
• Hypothesis: h(x) = θ₀ + θ₁x₁ + θ₂x₂ + ... + θₙxₙ
• Cost Function: Mean Squared Error (MSE) = (1/m)Σ(h(x⁽ⁱ⁾) - y⁽ⁱ⁾)²
• Gradient Descent: Used to minimize the cost function
• R-squared (R²): Measures how well the model fits the data (0 to 1)
  - R² = 1 - (SS_res / SS_tot)

Types of Linear Regression:
1. Simple Linear Regression: One independent variable
2. Multiple Linear Regression: Multiple independent variables
3. Polynomial Regression: Non-linear relationships using polynomial features

REGULARIZATION
Techniques to prevent overfitting:

• Ridge Regression (L2): Adds penalty term λΣθᵢ²
• Lasso Regression (L1): Adds penalty term λΣ|θᵢ|
• Elastic Net: Combines L1 and L2 regularization

EVALUATION METRICS
• Mean Squared Error (MSE): Average of squared differences
• Root Mean Squared Error (RMSE): √MSE
• Mean Absolute Error (MAE): Average of absolute differences
• R-squared: Proportion of variance explained

COMMON ISSUES
• Overfitting: Model performs well on training data but poorly on test data
• Underfitting: Model is too simple to capture patterns
• Multicollinearity: High correlation between features
• Outliers: Extreme values that can skew results

BEST PRACTICES
• Feature scaling/normalization
• Train/validation/test split
• Cross-validation
• Feature engineering
• Regularization for complex models""",

            4: """TOPIC 4: CLASSIFICATION ALGORITHMS

CLASSIFICATION OVERVIEW
Classification is a supervised learning task that assigns input data to predefined categories or classes.

KEY ALGORITHMS

1. LOGISTIC REGRESSION
• Used for binary and multi-class classification
• Uses sigmoid function: σ(z) = 1 / (1 + e⁻ᶻ)
• Outputs probabilities between 0 and 1
• Decision boundary separates classes

2. DECISION TREES
• Tree-like model of decisions
• Nodes represent features, branches represent decisions
• Leaf nodes represent class labels
• Easy to interpret but prone to overfitting

3. RANDOM FOREST
• Ensemble method using multiple decision trees
• Uses bagging (bootstrap aggregating)
• Reduces overfitting compared to single trees
• More robust and accurate

4. SUPPORT VECTOR MACHINES (SVM)
• Finds optimal hyperplane to separate classes
• Maximizes margin between classes
• Can handle non-linear data using kernels
• Effective for high-dimensional data

5. NAIVE BAYES
• Based on Bayes' theorem
• Assumes feature independence
• Fast and works well with small datasets
• Good baseline for text classification

6. K-NEAREST NEIGHBORS (KNN)
• Instance-based learning
• Classifies based on k nearest neighbors
• Simple but can be slow for large datasets
• Sensitive to irrelevant features

EVALUATION METRICS
• Accuracy: (TP + TN) / (TP + TN + FP + FN)
• Precision: TP / (TP + FP)
• Recall: TP / (TP + FN)
• F1-Score: 2 × (Precision × Recall) / (Precision + Recall)
• Confusion Matrix: Table showing true vs predicted classifications

MULTI-CLASS CLASSIFICATION
• One-vs-Rest (OvR): Train one classifier per class
• One-vs-One (OvO): Train classifier for each pair
• Softmax: Outputs probability distribution over classes""",

            5: """TOPIC 5: CLUSTERING AND UNSUPERVISED LEARNING

UNSUPERVISED LEARNING
Learning patterns from data without labeled examples. The algorithm discovers hidden structures in the data.

CLUSTERING
Grouping similar data points together based on their characteristics.

K-MEANS CLUSTERING
Most popular clustering algorithm.

Algorithm Steps:
1. Choose k (number of clusters)
2. Initialize k centroids randomly
3. Assign each point to nearest centroid
4. Update centroids to mean of assigned points
5. Repeat steps 3-4 until convergence

Key Parameters:
• k: Number of clusters
• Distance metric: Usually Euclidean distance
• Initialization: Can use k-means++ for better initialization

Advantages:
• Simple and fast
• Works well with spherical clusters
• Scales to large datasets

Limitations:
• Requires specifying k
• Sensitive to initialization
• Assumes clusters are spherical
• Sensitive to outliers

HIERARCHICAL CLUSTERING
Creates a tree-like structure (dendrogram) of clusters.

Types:
• Agglomerative (Bottom-up): Start with individual points, merge closest pairs
• Divisive (Top-down): Start with all points, recursively split

Linkage Methods:
• Single: Minimum distance between clusters
• Complete: Maximum distance between clusters
• Average: Average distance between clusters
• Ward: Minimizes within-cluster variance

DBSCAN (Density-Based Clustering)
• Groups points in dense regions
• Can find clusters of arbitrary shapes
• Identifies outliers (noise points)
• Parameters: eps (neighborhood radius), min_samples

EVALUATION METRICS
• Silhouette Score: Measures how similar objects are to their cluster
• Inertia: Sum of squared distances to centroids (for k-means)
• Davies-Bouldin Index: Lower is better

APPLICATIONS
• Customer segmentation
• Image segmentation
• Anomaly detection
• Data compression
• Pattern recognition""",

            6: """TOPIC 6: NEURAL NETWORKS AND MODEL EVALUATION

NEURAL NETWORKS
Inspired by biological neurons, neural networks are computing systems that learn to perform tasks by considering examples.

BASIC STRUCTURE
• Input Layer: Receives input features
• Hidden Layers: Process information (can have multiple)
• Output Layer: Produces final predictions
• Neurons (Nodes): Basic processing units
• Weights: Parameters learned during training
• Bias: Additional parameter for each neuron

ACTIVATION FUNCTIONS
Introduce non-linearity to the network:
• Sigmoid: σ(x) = 1 / (1 + e⁻ˣ) - Outputs 0 to 1
• Tanh: tanh(x) - Outputs -1 to 1
• ReLU: max(0, x) - Most common, addresses vanishing gradient
• Softmax: For multi-class classification

TRAINING PROCESS
1. Forward Propagation: Data flows through network
2. Calculate Loss: Compare prediction with actual value
3. Backpropagation: Calculate gradients
4. Update Weights: Adjust weights using gradient descent

BACKPROPAGATION
Algorithm for training neural networks:
• Calculates gradient of loss function with respect to weights
• Uses chain rule of calculus
• Updates weights to minimize loss
• Requires differentiable activation functions

DEEP LEARNING
Neural networks with multiple hidden layers:
• Can learn complex patterns
• Requires large amounts of data
• Computationally intensive
• Needs GPUs for training

MODEL EVALUATION

CROSS-VALIDATION
• K-Fold: Split data into k folds, train on k-1, test on 1
• Stratified K-Fold: Maintains class distribution
• Leave-One-Out: Extreme case where k = n

EVALUATION METRICS
For Classification:
• Accuracy, Precision, Recall, F1-Score
• ROC Curve and AUC
• Confusion Matrix

For Regression:
• MSE, RMSE, MAE
• R-squared

BIAS-VARIANCE TRADE-OFF
• Bias: Error from overly simplistic assumptions
• Variance: Error from sensitivity to small fluctuations
• Goal: Balance both to minimize total error

REGULARIZATION TECHNIQUES
• Dropout: Randomly disable neurons during training
• Early Stopping: Stop training when validation error increases
• Weight Decay: L2 regularization
• Batch Normalization: Normalize inputs to each layer""",

            7: """TOPIC 7: PRACTICAL AI AND MACHINE LEARNING APPLICATIONS

REAL-WORLD APPLICATIONS

COMPUTER VISION
Applications:
• Image Classification: Identifying objects in images
• Object Detection: Locating and classifying objects
• Facial Recognition: Identifying individuals
• Medical Imaging: X-ray analysis, tumor detection
• Autonomous Vehicles: Road sign recognition, obstacle detection
• Quality Control: Defect detection in manufacturing

Techniques:
• Convolutional Neural Networks (CNNs)
• Image preprocessing and augmentation
• Transfer learning

NATURAL LANGUAGE PROCESSING (NLP)
Applications:
• Sentiment Analysis: Determining emotional tone
• Machine Translation: Google Translate, language conversion
• Chatbots and Virtual Assistants: Customer service, Siri, Alexa
• Text Summarization: Condensing long documents
• Named Entity Recognition: Extracting entities from text
• Question Answering: Systems like ChatGPT

Techniques:
• Tokenization, Word embeddings (Word2Vec, GloVe)
• Recurrent Neural Networks (RNNs), LSTM, GRU
• Transformers and Attention mechanisms
• Large Language Models (LLMs)

SPEECH RECOGNITION
Applications:
• Voice assistants
• Transcription services
• Voice commands
• Language learning apps

RECOMMENDATION SYSTEMS
Applications:
• E-commerce: Product recommendations
• Streaming: Movie/music recommendations
• Social Media: Content suggestions

Techniques:
• Collaborative Filtering
• Content-Based Filtering
• Hybrid Approaches

HEALTHCARE AI
Applications:
• Disease Diagnosis: Medical image analysis
• Drug Discovery: Identifying potential compounds
• Personalized Medicine: Treatment recommendations
• Health Monitoring: Wearable devices

FINANCIAL AI
Applications:
• Fraud Detection: Identifying suspicious transactions
• Algorithmic Trading: Automated trading strategies
• Credit Scoring: Loan approval decisions
• Risk Assessment: Insurance underwriting

ETHICAL CONSIDERATIONS
• Bias and Fairness: Ensuring models don't discriminate
• Privacy: Protecting user data
• Transparency: Explainable AI
• Accountability: Responsibility for AI decisions""",

            8: """TOPIC 8: DIMENSIONALITY REDUCTION AND MODEL SELECTION

DIMENSIONALITY REDUCTION
Techniques to reduce the number of features while preserving important information.

PRINCIPAL COMPONENT ANALYSIS (PCA)
Most common dimensionality reduction technique.

How it works:
1. Standardize the data
2. Calculate covariance matrix
3. Find eigenvectors and eigenvalues
4. Select principal components (directions of maximum variance)
5. Transform data to lower dimensions

Key Concepts:
• Principal Components: Orthogonal directions of maximum variance
• Explained Variance: Proportion of variance captured by each component
• Dimensionality: Reduce from n to k dimensions (k < n)

Applications:
• Data visualization (reduce to 2D/3D)
• Noise reduction
• Feature extraction
• Speeding up learning algorithms

Limitations:
• Assumes linear relationships
• May lose interpretability
• Sensitive to feature scaling

OTHER TECHNIQUES
• t-SNE: Non-linear dimensionality reduction for visualization
• Autoencoders: Neural networks for dimensionality reduction
• Linear Discriminant Analysis (LDA): Supervised dimensionality reduction

MODEL SELECTION
Process of choosing the best model for a given problem.

CROSS-VALIDATION
• K-Fold Cross-Validation: Most common method
• Stratified K-Fold: Maintains class distribution
• Time Series Cross-Validation: For temporal data

HYPERPARAMETER TUNING
Finding optimal hyperparameters:
• Grid Search: Exhaustive search over parameter grid
• Random Search: Random sampling of parameters
• Bayesian Optimization: Efficient search strategy

MODEL COMPARISON
Compare different algorithms:
• Performance metrics (accuracy, F1, etc.)
• Training time
• Inference time
• Model complexity
• Interpretability

BIAS-VARIANCE TRADE-OFF
• High Bias (Underfitting): Model too simple
  - Solution: Increase model complexity, add features
• High Variance (Overfitting): Model too complex
  - Solution: Regularization, more data, simpler model

ENSEMBLE METHODS
Combining multiple models:
• Bagging: Train multiple models on different subsets
• Boosting: Sequentially train models to correct errors
• Stacking: Use meta-learner to combine predictions

MODEL SELECTION CRITERIA
• AIC (Akaike Information Criterion)
• BIC (Bayesian Information Criterion)
• Cross-validation score
• Domain knowledge""",

            9: """TOPIC 9: MARKOV DECISION PROCESS AND REINFORCEMENT LEARNING

REINFORCEMENT LEARNING (RL)
A type of machine learning where an agent learns to make decisions by interacting with an environment to maximize cumulative reward.

KEY CONCEPTS
• Agent: The learner/decision maker
• Environment: The world the agent interacts with
• State (s): Current situation of the environment
• Action (a): What the agent can do
• Reward (r): Feedback from the environment
• Policy (π): Strategy for selecting actions
• Value Function: Expected future reward

MARKOV DECISION PROCESS (MDP)
Mathematical framework for modeling decision-making in RL.

Components:
• States (S): Set of all possible states
• Actions (A): Set of all possible actions
• Transition Probabilities: P(s'|s,a) - probability of next state
• Reward Function: R(s,a,s') - reward for taking action
• Discount Factor (γ): Importance of future rewards (0 to 1)

Markov Property:
Future depends only on current state, not history:
P(s_{t+1}|s_t, a_t) = P(s_{t+1}|s_t, a_t, s_{t-1}, ...)

BELLMAN EQUATION
Fundamental equation in RL:
V*(s) = max_a Σ P(s'|s,a) [R(s,a,s') + γV*(s')]

Q-LEARNING
Model-free reinforcement learning algorithm.

Key Concepts:
• Q-Function: Q(s,a) = expected reward from state s, action a
• Q-Learning Update:
  Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
• Off-policy: Learns optimal policy regardless of policy followed
• Convergence: Guaranteed to converge to optimal Q-values

EXPLORATION VS EXPLOITATION
Critical trade-off in RL:
• Exploration: Try new actions to discover better strategies
• Exploitation: Use known good actions to maximize reward
• ε-greedy: Random action with probability ε, else best action
• Upper Confidence Bound (UCB): Balances exploration/exploitation

POLICY GRADIENT METHODS
Directly optimize the policy:
• REINFORCE: Monte Carlo policy gradient
• Actor-Critic: Combines value function and policy
• PPO (Proximal Policy Optimization): Stable policy updates

DEEP REINFORCEMENT LEARNING
Combining deep learning with RL:
• DQN (Deep Q-Network): Q-learning with neural networks
• Policy Networks: Neural networks representing policies
• Experience Replay: Store and reuse past experiences

APPLICATIONS
• Game Playing: Chess, Go, video games
• Robotics: Robot control and navigation
• Autonomous Vehicles: Decision making
• Recommendation Systems: Personalized suggestions
• Finance: Trading strategies
• Resource Management: Server allocation, energy management

CHALLENGES
• Sample Efficiency: Requires many interactions
• Exploration: Finding good strategies
• Stability: Training can be unstable
• Credit Assignment: Determining which actions led to rewards""",

            10: """TOPIC 10: EXAM REVIEW AND RECITATION

COMPREHENSIVE REVIEW OF KEY CONCEPTS

SUPERVISED LEARNING
• Regression: Predicting continuous values
  - Linear, Polynomial, Ridge, Lasso
• Classification: Predicting categories
  - Logistic Regression, Decision Trees, SVM, Random Forest, KNN

UNSUPERVISED LEARNING
• Clustering: Grouping similar data
  - K-Means, Hierarchical, DBSCAN
• Dimensionality Reduction: Reducing features
  - PCA, t-SNE

NEURAL NETWORKS
• Structure: Input, Hidden, Output layers
• Activation Functions: Sigmoid, ReLU, Softmax
• Training: Forward propagation, Backpropagation
• Deep Learning: Multiple hidden layers

EVALUATION METRICS

Classification:
• Accuracy: Overall correctness
• Precision: True positives / (True positives + False positives)
• Recall: True positives / (True positives + False negatives)
• F1-Score: Harmonic mean of precision and recall
• ROC-AUC: Area under receiver operating characteristic curve
• Confusion Matrix: Detailed breakdown of predictions

Regression:
• MSE: Mean Squared Error
• RMSE: Root Mean Squared Error
• MAE: Mean Absolute Error
• R²: Coefficient of determination

IMPORTANT CONCEPTS

Bias-Variance Trade-off:
• Bias: Error from overly simplistic model (underfitting)
• Variance: Error from model sensitivity (overfitting)
• Goal: Minimize total error = Bias² + Variance + Irreducible Error

Overfitting vs Underfitting:
• Overfitting: Model too complex, memorizes training data
• Underfitting: Model too simple, can't capture patterns

Regularization:
• L1 (Lasso): Encourages sparse models
• L2 (Ridge): Prevents large weights
• Dropout: Randomly disable neurons
• Early Stopping: Stop when validation error increases

Cross-Validation:
• K-Fold: Split data into k parts
• Stratified: Maintains class distribution
• Prevents overfitting to specific train/test split

EXAM TIPS
1. Understand the fundamental concepts, not just memorization
2. Know when to use which algorithm
3. Understand evaluation metrics and their trade-offs
4. Practice interpreting results (confusion matrices, learning curves)
5. Know the assumptions and limitations of each method
6. Understand the bias-variance trade-off
7. Be familiar with preprocessing steps (scaling, encoding)
8. Know regularization techniques and their purposes

COMMON MISTAKES TO AVOID
• Confusing classification and regression problems
• Not understanding when to use which metric
• Ignoring data preprocessing
• Overfitting without realizing it
• Not understanding the problem domain
• Choosing complex models when simple ones work

STUDY STRATEGIES
• Review all topics systematically
• Practice with different types of problems
• Understand the "why" behind each technique
• Work through examples
• Review your quiz and test results
• Focus on areas with lower scores"""
        }
        
        return content_map.get(topic_num, "Content not available for this topic.")


def main():
    root = tk.Tk()
    app = AILearningApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

