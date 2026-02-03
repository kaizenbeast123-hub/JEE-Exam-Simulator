"""
JEE Main Exam Simulator - Multi-Test Version
Supports multiple mock tests without code changes!
"""

import streamlit as st
import json
import time
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="JEE Main Mock Tests",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get available tests
def get_available_tests():
    """Find all question JSON files in the directory"""
    tests = []
    for file in Path('.').glob('questions_*.json'):
        # Extract test name from filename
        # questions_test1.json -> Test 1
        # questions_fiitjee_2020.json -> FIITJEE 2020
        test_name = file.stem.replace('questions_', '').replace('_', ' ').title()
        tests.append({
            'name': test_name,
            'file': str(file),
            'display': f"📝 {test_name}"
        })
    
    # Also check for default questions.json
    if Path('questions.json').exists():
        tests.insert(0, {
            'name': 'Default Test',
            'file': 'questions.json',
            'display': '📝 Default Test'
        })
    
    return tests

# Load CSS based on theme
def apply_theme():
    if st.session_state.get('dark_mode', False):
        st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: #e0e0e0; }
    .main { background-color: #1a1a1a; }
    .question-card { background-color: #2d2d2d !important; color: #e0e0e0; border-left: 4px solid #667eea; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .solution-box { background-color: #1a3a4a !important; color: #e0e0e0; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3; margin: 10px 0; }
    .stRadio > label { background-color: #2d2d2d; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .timer { font-size: 24px; font-weight: bold; padding: 10px 20px; border-radius: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
    .timer.warning { background: #ff6b6b; animation: pulse 1s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #333333; }
    .main { background-color: #ffffff; }
    .question-card { background-color: #f8f9fa !important; color: #333333; border-left: 4px solid #667eea; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .solution-box { background-color: #e8f4f8 !important; color: #333333; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3; margin: 10px 0; }
    .stRadio > label { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .timer { font-size: 24px; font-weight: bold; padding: 10px 20px; border-radius: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
    .timer.warning { background: #ff6b6b; animation: pulse 1s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_test = None
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.question_status = []
        st.session_state.marked_for_review = []
        st.session_state.exam_started = False
        st.session_state.exam_submitted = False
        st.session_state.start_time = None
        st.session_state.time_remaining = 3 * 60 * 60
        st.session_state.dark_mode = False
        st.session_state.questions = []

def reset_exam_state():
    """Reset state when switching tests"""
    st.session_state.current_question = 0
    st.session_state.answers = [None] * 75
    st.session_state.question_status = ['not-visited'] * 75
    st.session_state.marked_for_review = [False] * 75
    st.session_state.exam_started = False
    st.session_state.exam_submitted = False
    st.session_state.start_time = None
    st.session_state.time_remaining = 3 * 60 * 60
    st.session_state.questions = []

def load_questions(filename):
    """Load questions from a specific file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        if not questions:
            st.error(f"❌ {filename} is empty!")
            return None
        return questions
    except Exception as e:
        st.error(f"❌ Error loading {filename}: {e}")
        return None

# Helper functions (same as before)
def format_time(seconds):
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_palette_color(index):
    if st.session_state.marked_for_review[index]: return "#9c27b0"
    elif st.session_state.question_status[index] == 'answered': return "#4caf50"
    elif st.session_state.question_status[index] == 'not-answered': return "#f44336"
    else: return "#9e9e9e"

def navigate_to_question(index):
    st.session_state.current_question = index
    if st.session_state.question_status[index] == 'not-visited':
        st.session_state.question_status[index] = 'not-answered'

def save_answer():
    current = st.session_state.current_question
    if st.session_state.answers[current] is not None:
        st.session_state.question_status[current] = 'answered'
        st.session_state.marked_for_review[current] = False

def clear_answer():
    current = st.session_state.current_question
    st.session_state.answers[current] = None
    st.session_state.question_status[current] = 'not-answered'

def mark_for_review():
    st.session_state.marked_for_review[st.session_state.current_question] = True

def calculate_results(questions):
    total_score, correct, incorrect, unattempted = 0, 0, 0, 0
    subject_stats = {s: {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'score': 0} 
                    for s in ['Physics', 'Chemistry', 'Mathematics']}
    
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers[i]
        subject = q['subject']
        
        if user_answer is None:
            unattempted += 1
            subject_stats[subject]['unattempted'] += 1
        else:
            is_correct = False
            if q['type'] == 'mcq':
                is_correct = user_answer == q['correct']
            elif q['type'] == 'numerical':
                is_correct = user_answer == q['correct']
            elif q['type'] == 'decimal':
                is_correct = abs(float(user_answer) - float(q['correct'])) < 0.01
            
            if is_correct:
                correct += 1
                subject_stats[subject]['correct'] += 1
                total_score += 4
                subject_stats[subject]['score'] += 4
            else:
                incorrect += 1
                subject_stats[subject]['incorrect'] += 1
                if i % 25 < 20:  # Negative marking only for Section A
                    total_score -= 1
                    subject_stats[subject]['score'] -= 1
    
    return total_score, correct, incorrect, unattempted, subject_stats

def display_results(questions):
    st.markdown("# 🎉 Test Completed!")
    total_score, correct, incorrect, unattempted, subject_stats = calculate_results(questions)
    
    # Score cards
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        (col1, "Total Score", f"{total_score}/300", f"{total_score/3:.2f}%", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
        (col2, "Correct", str(correct), f"{correct}/75", "#4caf50"),
        (col3, "Incorrect", str(incorrect), f"{incorrect}/75", "#f44336"),
        (col4, "Unattempted", str(unattempted), f"{unattempted}/75", "#ff9800")
    ]
    
    for col, title, value, subtitle, bg in cards:
        with col:
            st.markdown(f"""
            <div style='padding:20px; border-radius:10px; text-align:center; color:white; background:{bg};'>
                <h3>{title}</h3><h1>{value}</h1><p>{subtitle}</p>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 📊 Subject-wise Performance")
    
    for subject in ['Physics', 'Chemistry', 'Mathematics']:
        stats = subject_stats[subject]
        acc = (stats['correct'] / (stats['correct'] + stats['incorrect']) * 100) if (stats['correct'] + stats['incorrect']) > 0 else 0
        
        with st.expander(f"{subject} - {stats['score']}/100 ({stats['score']}%)", expanded=True):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Score", f"{stats['score']}/100")
            c2.metric("Correct", f"{stats['correct']}/25")
            c3.metric("Incorrect", f"{stats['incorrect']}/25")
            c4.metric("Unattempted", f"{stats['unattempted']}/25")
            c5.metric("Accuracy", f"{acc:.1f}%")
    
    st.markdown("---")
    st.markdown("## 📝 Solutions")
    
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers[i]
        
        if user_answer is None:
            emoji, marks = '🟠', 0
        else:
            is_correct = False
            if q['type'] == 'mcq': is_correct = user_answer == q['correct']
            elif q['type'] == 'numerical': is_correct = user_answer == q['correct']
            elif q['type'] == 'decimal': is_correct = abs(float(user_answer) - float(q['correct'])) < 0.01
            
            emoji = '🟢' if is_correct else '🔴'
            marks = 4 if is_correct else (-1 if i % 25 < 20 else 0)
        
        with st.expander(f"{emoji} Q{i+1} ({q['subject']}) - {'+' if marks > 0 else ''}{marks} marks"):
            st.markdown(f"**Question:** {q['question']}")
            
            if q['type'] == 'mcq':
                for idx, opt in enumerate(q['options']):
                    if idx == q['correct']:
                        st.success(f"✅ {chr(65+idx)}. {opt}")
                    elif user_answer == idx:
                        st.error(f"❌ {chr(65+idx)}. {opt} (Your Answer)")
                    else:
                        st.markdown(f"{chr(65+idx)}. {opt}")
            
            col1, col2 = st.columns(2)
            with col1:
                ans_text = f"{chr(65 + user_answer)}" if q['type'] == 'mcq' and user_answer is not None else str(user_answer) if user_answer is not None else "Not answered"
                st.markdown(f"**Your Answer:** {ans_text}")
            with col2:
                correct_text = f"{chr(65 + q['correct'])}" if q['type'] == 'mcq' else str(q['correct'])
                st.markdown(f"**Correct:** :green[{correct_text}]")
            
            st.markdown("---")
            st.markdown(f"<div class='solution-box'>💡 **Solution:** {q['solution']}</div>", unsafe_allow_html=True)
    
    if st.button("🔄 Take Another Test", type="primary"):
        reset_exam_state()
        st.rerun()

# Main app
def main():
    init_session_state()
    apply_theme()
    
    # Get available tests
    available_tests = get_available_tests()
    
    if not available_tests:
        st.error("❌ No test files found!")
        st.info("Create question files like: questions_test1.json, questions_test2.json, etc.")
        st.stop()
    
    # Test selector (shown before exam starts or in sidebar during exam)
    if not st.session_state.exam_started:
        st.title("📚 JEE Main Mock Test Simulator")
        st.markdown("### Select a Test to Begin")
        
        # Display available tests
        cols = st.columns(min(3, len(available_tests)))
        for idx, test in enumerate(available_tests):
            with cols[idx % 3]:
                if st.button(test['display'], use_container_width=True, type="primary"):
                    st.session_state.current_test = test
                    reset_exam_state()
                    questions = load_questions(test['file'])
                    if questions:
                        st.session_state.questions = questions
                        st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        - **75 Questions** (Physics: 25, Chemistry: 25, Math: 25)
        - **Duration:** 3 hours
        - **Marking:** +4 correct, -1 incorrect (Section A only)
        
        **Colors:** 🟢 Answered | 🔴 Not Answered | ⚫ Not Visited | 🟣 Marked
        """)
        
        # Dark mode toggle
        if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        return
    
    # Load test if selected
    if not st.session_state.questions and st.session_state.current_test:
        questions = load_questions(st.session_state.current_test['file'])
        if not questions:
            st.error("Failed to load test")
            st.session_state.exam_started = False
            st.rerun()
        st.session_state.questions = questions
    
    questions = st.session_state.questions
    
    # Exam header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        test_name = st.session_state.current_test['name'] if st.session_state.current_test else "Mock Test"
        st.title(f"📚 {test_name}")
    with col2:
        if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with col3:
        if not st.session_state.exam_submitted:
            elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0
            st.session_state.time_remaining = max(0, 3 * 60 * 60 - int(elapsed))
            timer_class = "timer warning" if st.session_state.time_remaining <= 300 else "timer"
            st.markdown(f'<div class="{timer_class}">{format_time(st.session_state.time_remaining)}</div>', unsafe_allow_html=True)
            if st.session_state.time_remaining == 0:
                st.session_state.exam_submitted = True
                st.rerun()
    
    st.markdown("---")
    
    # Start exam or show interface
    if not st.session_state.start_time:
        if st.button("🚀 Start Exam", type="primary", use_container_width=True):
            st.session_state.start_time = time.time()
            st.rerun()
        return
    
    if st.session_state.exam_submitted:
        display_results(questions)
        return
    
    # Exam interface
    col_q, col_p = st.columns([2, 1])
    
    with col_q:
        current = st.session_state.current_question
        q = questions[current]
        
        st.markdown(f"### :blue[{q['subject']} - Question {current + 1}/75]")
        st.markdown(f"<div class='question-card'><b>Q{current + 1}:</b> {q['question']}</div>", unsafe_allow_html=True)
        
        # Answer input
        if q['type'] == 'mcq':
            selected = st.radio("Your answer:", range(len(q['options'])),
                              format_func=lambda x: f"{chr(65+x)}. {q['options'][x]}",
                              key=f"q_{current}",
                              index=st.session_state.answers[current] if st.session_state.answers[current] is not None else None)
            if selected is not None:
                st.session_state.answers[current] = selected
        elif q['type'] == 'numerical':
            ans = st.number_input("Enter (0-9):", 0, 9, st.session_state.answers[current] or 0, key=f"q_{current}")
            st.session_state.answers[current] = ans
        else:
            ans = st.number_input("Enter answer:", format="%.2f", value=float(st.session_state.answers[current] or 0), key=f"q_{current}")
            st.session_state.answers[current] = ans
        
        # Controls
        st.markdown("---")
        b1, b2, b3, b4 = st.columns(4)
        if b1.button("⬅️ Previous", disabled=current == 0):
            save_answer()
            navigate_to_question(current - 1)
            st.rerun()
        if b2.button("🗑️ Clear"):
            clear_answer()
            st.rerun()
        if b3.button("🔖 Mark"):
            mark_for_review()
            if current < 74:
                navigate_to_question(current + 1)
            st.rerun()
        if b4.button("💾 Save ➡️", type="primary"):
            save_answer()
            if current < 74:
                navigate_to_question(current + 1)
            st.rerun()
    
    with col_p:
        st.markdown("### 🎯 Palette")
        
        # Physics
        st.markdown("**Physics**")
        cols = st.columns(5)
        for i in range(25):
            with cols[i % 5]:
                if st.button(str(i + 1), key=f"p{i}"):
                    save_answer()
                    navigate_to_question(i)
                    st.rerun()
        
        # Chemistry
        st.markdown("**Chemistry**")
        cols = st.columns(5)
        for i in range(25, 50):
            with cols[(i - 25) % 5]:
                if st.button(str(i + 1), key=f"c{i}"):
                    save_answer()
                    navigate_to_question(i)
                    st.rerun()
        
        # Math
        st.markdown("**Math**")
        cols = st.columns(5)
        for i in range(50, 75):
            with cols[(i - 50) % 5]:
                if st.button(str(i + 1), key=f"m{i}"):
                    save_answer()
                    navigate_to_question(i)
                    st.rerun()
        
        st.markdown("---")
        unanswered = sum(1 for s in st.session_state.question_status if s != 'answered')
        st.warning(f"⚠️ {unanswered} unanswered")
        
        if st.button("✅ Submit Test", type="primary", use_container_width=True):
            st.session_state.exam_submitted = True
            st.rerun()

main()
