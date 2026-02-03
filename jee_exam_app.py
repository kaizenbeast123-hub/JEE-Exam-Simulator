import streamlit as st
import json
import time
from datetime import datetime, timedelta
import pandas as pd

# Page config
st.set_page_config(
    page_title="JEE Main Exam Simulator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Question card */
    .question-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 20px;
    }
    
    /* Dark mode question card */
    [data-theme="dark"] .question-card {
        background-color: #2d2d2d;
    }
    
    /* Timer */
    .timer {
        font-size: 24px;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    
    .timer.warning {
        background: #ff6b6b;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Option buttons */
    .stButton > button {
        width: 100%;
        text-align: left;
        padding: 15px;
        margin: 5px 0;
    }
    
    /* Palette button styling */
    div[data-testid="stHorizontalBlock"] button {
        min-width: 50px;
        height: 50px;
        margin: 2px;
    }
    
    /* Score cards */
    .score-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 10px;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Solution box */
    .solution-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
    
    [data-theme="dark"] .solution-box {
        background-color: #1a3a4a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_question = 0
    st.session_state.answers = [None] * 75
    st.session_state.question_status = ['not-visited'] * 75
    st.session_state.marked_for_review = [False] * 75
    st.session_state.exam_started = False
    st.session_state.exam_submitted = False
    st.session_state.start_time = None
    st.session_state.time_remaining = 3 * 60 * 60  # 3 hours in seconds
    st.session_state.dark_mode = False

# Load questions from JSON file
@st.cache_data
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("questions.json file not found! Please ensure it exists in the same directory.")
        return []

questions = load_questions()

# Helper functions
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_palette_color(index):
    if st.session_state.marked_for_review[index]:
        return "#9c27b0"  # Purple
    elif st.session_state.question_status[index] == 'answered':
        return "#4caf50"  # Green
    elif st.session_state.question_status[index] == 'not-answered':
        return "#f44336"  # Red
    else:
        return "#9e9e9e"  # Grey

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
    st.session_state.marked_for_review[current] = False

def mark_for_review():
    current = st.session_state.current_question
    st.session_state.marked_for_review[current] = True
    st.session_state.question_status[current] = 'marked'

def calculate_results():
    total_score = 0
    correct = 0
    incorrect = 0
    unattempted = 0
    
    subject_stats = {
        'Physics': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'score': 0},
        'Chemistry': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'score': 0},
        'Mathematics': {'correct': 0, 'incorrect': 0, 'unattempted': 0, 'score': 0}
    }
    
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
                # Negative marking only for Section A (first 20 questions of each subject)
                if i % 25 < 20:
                    total_score -= 1
                    subject_stats[subject]['score'] -= 1
    
    return total_score, correct, incorrect, unattempted, subject_stats

# Main App
def main():
    if not questions:
        st.error("No questions loaded. Please check your questions.json file.")
        return
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("📚 JEE (Main) - 2020")
        st.caption("FIITJEE All India Test Series - Full Test IV")
    
    with col2:
        if st.button("🌙 Toggle Dark Mode" if not st.session_state.dark_mode else "☀️ Toggle Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    with col3:
        if st.session_state.exam_started and not st.session_state.exam_submitted:
            # Update timer
            elapsed = time.time() - st.session_state.start_time
            st.session_state.time_remaining = max(0, 3 * 60 * 60 - int(elapsed))
            
            timer_class = "timer warning" if st.session_state.time_remaining <= 300 else "timer"
            st.markdown(f'<div class="{timer_class}">{format_time(st.session_state.time_remaining)}</div>', 
                       unsafe_allow_html=True)
            
            if st.session_state.time_remaining == 0:
                st.session_state.exam_submitted = True
                st.rerun()
    
    st.markdown("---")
    
    # Start exam screen
    if not st.session_state.exam_started:
        st.markdown("## 📋 Instructions")
        st.markdown("""
        - **Total Questions:** 75 (Physics: 25, Chemistry: 25, Mathematics: 25)
        - **Total Marks:** 300
        - **Duration:** 3 hours
        - **Section A (Q1-20, Q26-45, Q51-70):** +4 for correct, -1 for incorrect
        - **Section B (Q21-22, Q46-47, Q71-72):** +4 for correct, No negative marking
        - **Section C (Q23-25, Q48-50, Q73-75):** +4 for correct, No negative marking
        
        ### Question Palette Colors:
        - 🟢 **Green:** Answered
        - 🔴 **Red:** Not Answered (Visited but not answered)
        - ⚫ **Grey:** Not Visited
        - 🟣 **Purple:** Marked for Review
        """)
        
        if st.button("🚀 Start Exam", type="primary", use_container_width=True):
            st.session_state.exam_started = True
            st.session_state.start_time = time.time()
            st.rerun()
    
    # Exam interface
    elif st.session_state.exam_started and not st.session_state.exam_submitted:
        # Main layout
        col_question, col_palette = st.columns([2, 1])
        
        with col_question:
            current = st.session_state.current_question
            q = questions[current]
            
            # Subject header
            subject_colors = {
                'Physics': '#667eea',
                'Chemistry': '#f093fb',
                'Mathematics': '#4facfe'
            }
            st.markdown(f"### :blue[{q['subject']} - Question {current + 1}/75]")
            
            # Question
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            
            # Render question with LaTeX support
            st.markdown(f"**Question {current + 1}:**")
            st.latex(q['question']) if q.get('is_latex', False) else st.markdown(q['question'])
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Answer options
            if q['type'] == 'mcq':
                options = q['options']
                
                # Create radio button with custom styling
                selected = st.radio(
                    "Select your answer:",
                    range(len(options)),
                    format_func=lambda x: f"{chr(65+x)}. {options[x]}",
                    key=f"q_{current}",
                    index=st.session_state.answers[current] if st.session_state.answers[current] is not None else None
                )
                
                if selected is not None:
                    st.session_state.answers[current] = selected
            
            elif q['type'] in ['numerical', 'decimal']:
                if q['type'] == 'numerical':
                    answer = st.number_input(
                        "Enter single digit (0-9):",
                        min_value=0,
                        max_value=9,
                        step=1,
                        value=st.session_state.answers[current] if st.session_state.answers[current] is not None else 0,
                        key=f"q_{current}"
                    )
                else:
                    answer = st.number_input(
                        "Enter answer (format: XXXXX.XX):",
                        format="%.2f",
                        value=float(st.session_state.answers[current]) if st.session_state.answers[current] is not None else 0.0,
                        key=f"q_{current}"
                    )
                
                st.session_state.answers[current] = answer
            
            # Control buttons
            st.markdown("---")
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            
            with btn_col1:
                if st.button("⬅️ Previous", use_container_width=True, disabled=current == 0):
                    save_answer()
                    navigate_to_question(current - 1)
                    st.rerun()
            
            with btn_col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    clear_answer()
                    st.rerun()
            
            with btn_col3:
                if st.button("🔖 Mark & Next", use_container_width=True):
                    mark_for_review()
                    if current < 74:
                        navigate_to_question(current + 1)
                    st.rerun()
            
            with btn_col4:
                if st.button("💾 Save & Next ➡️", use_container_width=True, type="primary"):
                    save_answer()
                    if current < 74:
                        navigate_to_question(current + 1)
                    st.rerun()
        
        with col_palette:
            st.markdown("### 🎯 Question Palette")
            
            # Legend
            st.markdown("""
            <div style='background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
                <small>
                🟢 Answered &nbsp;&nbsp; 🔴 Not Answered<br>
                ⚫ Not Visited &nbsp;&nbsp; 🟣 Marked
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            # Physics
            st.markdown("**Physics (1-25)**")
            cols = st.columns(5)
            for i in range(25):
                with cols[i % 5]:
                    color = get_palette_color(i)
                    border = "3px solid #333" if i == current else "1px solid #ddd"
                    if st.button(
                        str(i + 1),
                        key=f"phy_{i}",
                        use_container_width=True
                    ):
                        save_answer()
                        navigate_to_question(i)
                        st.rerun()
            
            # Chemistry
            st.markdown("**Chemistry (26-50)**")
            cols = st.columns(5)
            for i in range(25, 50):
                with cols[(i - 25) % 5]:
                    color = get_palette_color(i)
                    if st.button(
                        str(i + 1),
                        key=f"chem_{i}",
                        use_container_width=True
                    ):
                        save_answer()
                        navigate_to_question(i)
                        st.rerun()
            
            # Mathematics
            st.markdown("**Mathematics (51-75)**")
            cols = st.columns(5)
            for i in range(50, 75):
                with cols[(i - 50) % 5]:
                    color = get_palette_color(i)
                    if st.button(
                        str(i + 1),
                        key=f"math_{i}",
                        use_container_width=True
                    ):
                        save_answer()
                        navigate_to_question(i)
                        st.rerun()
            
            # Submit button
            st.markdown("---")
            unanswered_count = sum(1 for status in st.session_state.question_status if status != 'answered')
            st.warning(f"⚠️ {unanswered_count} questions unanswered")
            
            if st.button("✅ Submit Test", type="primary", use_container_width=True):
                st.session_state.exam_submitted = True
                st.rerun()
    
    # Results screen
    elif st.session_state.exam_submitted:
        display_results()

def display_results():
    st.markdown("# 🎉 Test Completed!")
    st.markdown("### Here's your performance analysis")
    
    total_score, correct, incorrect, unattempted, subject_stats = calculate_results()
    
    # Score cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='score-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
            <h3>Total Score</h3>
            <h1>{total_score}/300</h1>
            <p>{(total_score/300*100):.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='score-card' style='background: #4caf50;'>
            <h3>Correct</h3>
            <h1>{correct}</h1>
            <p>{correct}/75 questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='score-card' style='background: #f44336;'>
            <h3>Incorrect</h3>
            <h1>{incorrect}</h1>
            <p>{incorrect}/75 questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='score-card' style='background: #ff9800;'>
            <h3>Unattempted</h3>
            <h1>{unattempted}</h1>
            <p>{unattempted}/75 questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Subject-wise analysis
    st.markdown("## 📊 Subject-wise Performance")
    
    for subject in ['Physics', 'Chemistry', 'Mathematics']:
        stats = subject_stats[subject]
        percentage = (stats['score'] / 100 * 100)
        accuracy = (stats['correct'] / (stats['correct'] + stats['incorrect']) * 100) if (stats['correct'] + stats['incorrect']) > 0 else 0
        
        with st.expander(f"### {subject} - {stats['score']}/100 ({percentage:.1f}%)", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            col1.metric("Score", f"{stats['score']}/100")
            col2.metric("Correct", f"{stats['correct']}/25")
            col3.metric("Incorrect", f"{stats['incorrect']}/25")
            col4.metric("Unattempted", f"{stats['unattempted']}/25")
            col5.metric("Accuracy", f"{accuracy:.1f}%")
    
    st.markdown("---")
    
    # Detailed solutions
    st.markdown("## 📝 Detailed Solutions")
    
    st.info("""
    **How to read this section:**
    - 🟢 Green = Correct answer
    - 🔴 Red = Your incorrect answer
    - 🟠 Orange = Unattempted
    """)
    
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers[i]
        
        # Determine status
        if user_answer is None:
            status = 'unattempted'
            status_emoji = '🟠'
            marks = 0
        else:
            is_correct = False
            if q['type'] == 'mcq':
                is_correct = user_answer == q['correct']
            elif q['type'] == 'numerical':
                is_correct = user_answer == q['correct']
            elif q['type'] == 'decimal':
                is_correct = abs(float(user_answer) - float(q['correct'])) < 0.01
            
            if is_correct:
                status = 'correct'
                status_emoji = '🟢'
                marks = 4
            else:
                status = 'incorrect'
                status_emoji = '🔴'
                marks = -1 if i % 25 < 20 else 0
        
        # Display solution
        with st.expander(f"{status_emoji} Question {i+1} ({q['subject']}) - {'+' if marks > 0 else ''}{marks} marks", expanded=False):
            st.markdown(f"**Question:**")
            st.latex(q['question']) if q.get('is_latex', False) else st.markdown(q['question'])
            
            if q['type'] == 'mcq':
                st.markdown("**Options:**")
                for idx, option in enumerate(q['options']):
                    prefix = ""
                    if idx == q['correct']:
                        prefix = "✅ "
                        st.success(f"{prefix}{chr(65+idx)}. {option}")
                    elif user_answer == idx and idx != q['correct']:
                        prefix = "❌ "
                        st.error(f"{prefix}{chr(65+idx)}. {option} (Your Answer)")
                    else:
                        st.markdown(f"{chr(65+idx)}. {option}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if user_answer is not None:
                    if q['type'] == 'mcq':
                        st.markdown(f"**Your Answer:** {chr(65 + user_answer)}")
                    else:
                        st.markdown(f"**Your Answer:** {user_answer}")
                else:
                    st.markdown("**Your Answer:** Not answered")
            
            with col2:
                if q['type'] == 'mcq':
                    st.markdown(f"**Correct Answer:** :green[{chr(65 + q['correct'])}]")
                else:
                    st.markdown(f"**Correct Answer:** :green[{q['correct']}]")
            
            st.markdown("---")
            st.markdown("**Solution:**")
            st.markdown(f"<div class='solution-box'>{q['solution']}</div>", unsafe_allow_html=True)
    
    # Restart option
    if st.button("🔄 Take Another Test", type="primary"):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()