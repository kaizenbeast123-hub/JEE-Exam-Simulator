import streamlit as st
import json
import time
from datetime import datetime, timedelta
import os

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="JEE Main Exam Simulator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    
    .question-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 20px;
    }
    
    [data-theme="dark"] .question-card {
        background-color: #2d2d2d;
    }
    
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
    
    .score-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 10px;
    }
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_question = 0
        st.session_state.answers = [None] * 75
        st.session_state.question_status = ['not-visited'] * 75
        st.session_state.marked_for_review = [False] * 75
        st.session_state.exam_started = False
        st.session_state.exam_submitted = False
        st.session_state.start_time = None
        st.session_state.time_remaining = 3 * 60 * 60
        st.session_state.dark_mode = False
        st.session_state.questions = []

# Load questions
def load_questions():
    json_path = 'questions.json'
    
    if not os.path.exists(json_path):
        st.error(f"❌ questions.json not found!")
        st.info(f"📁 Looking in: {os.getcwd()}")
        st.info("💡 Make sure questions.json is in the same folder as this app.")
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            
        if not questions or len(questions) == 0:
            st.error("❌ questions.json is empty!")
            return None
            
        return questions
        
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Error: {e}")
        st.info("Check that your JSON file is properly formatted.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Helper functions
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_palette_color(index):
    if st.session_state.marked_for_review[index]:
        return "#9c27b0"
    elif st.session_state.question_status[index] == 'answered':
        return "#4caf50"
    elif st.session_state.question_status[index] == 'not-answered':
        return "#f44336"
    else:
        return "#9e9e9e"

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

def calculate_results(questions):
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
                if i % 25 < 20:
                    total_score -= 1
                    subject_stats[subject]['score'] -= 1
    
    return total_score, correct, incorrect, unattempted, subject_stats

def display_results(questions):
    st.markdown("# 🎉 Test Completed!")
    st.markdown("### Here's your performance analysis")
    
    total_score, correct, incorrect, unattempted, subject_stats = calculate_results(questions)
    
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
    **Color Guide:**
    - 🟢 Green = Correct
    - 🔴 Red = Incorrect  
    - 🟠 Orange = Unattempted
    """)
    
    for i, q in enumerate(questions):
        user_answer = st.session_state.answers[i]
        
        if user_answer is None:
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
                status_emoji = '🟢'
                marks = 4
            else:
                status_emoji = '🔴'
                marks = -1 if i % 25 < 20 else 0
        
        with st.expander(f"{status_emoji} Q{i+1} ({q['subject']}) - {'+' if marks > 0 else ''}{marks} marks"):
            st.markdown(f"**Question:**")
            st.markdown(q['question'])
            
            if q['type'] == 'mcq':
                st.markdown("**Options:**")
                for idx, option in enumerate(q['options']):
                    if idx == q['correct']:
                        st.success(f"✅ {chr(65+idx)}. {option}")
                    elif user_answer == idx:
                        st.error(f"❌ {chr(65+idx)}. {option} (Your Answer)")
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
                    st.markdown(f"**Correct:** :green[{chr(65 + q['correct'])}]")
                else:
                    st.markdown(f"**Correct:** :green[{q['correct']}]")
            
            st.markdown("---")
            st.markdown("**💡 Solution:**")
            st.markdown(f"<div class='solution-box'>{q['solution']}</div>", unsafe_allow_html=True)
    
    if st.button("🔄 Take Another Test", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main app
def main():
    # Initialize
    init_session_state()
    
    # Load questions only once
    if not st.session_state.questions:
        questions = load_questions()
        if questions is None:
            st.stop()
        st.session_state.questions = questions
    
    questions = st.session_state.questions
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("📚 JEE (Main) - 2020")
        st.caption("FIITJEE All India Test Series - Full Test IV")
    
    with col2:
        if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"):
            st.session_state.dark_mode = not st.session_state.dark_mode
    
    with col3:
        if st.session_state.exam_started and not st.session_state.exam_submitted:
            elapsed = time.time() - st.session_state.start_time
            st.session_state.time_remaining = max(0, 3 * 60 * 60 - int(elapsed))
            
            timer_class = "timer warning" if st.session_state.time_remaining <= 300 else "timer"
            st.markdown(f'<div class="{timer_class}">{format_time(st.session_state.time_remaining)}</div>', 
                       unsafe_allow_html=True)
            
            if st.session_state.time_remaining == 0:
                st.session_state.exam_submitted = True
                st.rerun()
    
    st.markdown("---")
    
    # Start screen
    if not st.session_state.exam_started:
        st.markdown("## 📋 Instructions")
        st.markdown("""
        - **Total Questions:** 75
        - **Duration:** 3 hours
        - **Marking:** +4 for correct, -1 for incorrect (Section A only)
        
        **Color Legend:**
        - 🟢 Green = Answered
        - 🔴 Red = Not Answered
        - ⚫ Grey = Not Visited
        - 🟣 Purple = Marked for Review
        """)
        
        if st.button("🚀 Start Exam", type="primary", use_container_width=True):
            st.session_state.exam_started = True
            st.session_state.start_time = time.time()
            st.rerun()
    
    # Exam interface
    elif st.session_state.exam_started and not st.session_state.exam_submitted:
        col_q, col_p = st.columns([2, 1])
        
        with col_q:
            current = st.session_state.current_question
            q = questions[current]
            
            st.markdown(f"### :blue[{q['subject']} - Question {current + 1}/75]")
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"**Question {current + 1}:**")
            st.markdown(q['question'])
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Answer input
            if q['type'] == 'mcq':
                selected = st.radio(
                    "Your answer:",
                    range(len(q['options'])),
                    format_func=lambda x: f"{chr(65+x)}. {q['options'][x]}",
                    key=f"q_{current}",
                    index=st.session_state.answers[current] if st.session_state.answers[current] is not None else None
                )
                if selected is not None:
                    st.session_state.answers[current] = selected
            
            elif q['type'] == 'numerical':
                answer = st.number_input(
                    "Enter digit (0-9):",
                    min_value=0, max_value=9, step=1,
                    value=st.session_state.answers[current] if st.session_state.answers[current] else 0,
                    key=f"q_{current}"
                )
                st.session_state.answers[current] = answer
            
            else:  # decimal
                answer = st.number_input(
                    "Enter answer:",
                    format="%.2f",
                    value=float(st.session_state.answers[current]) if st.session_state.answers[current] else 0.0,
                    key=f"q_{current}"
                )
                st.session_state.answers[current] = answer
            
            # Control buttons
            st.markdown("---")
            b1, b2, b3, b4 = st.columns(4)
            
            with b1:
                if st.button("⬅️ Previous", disabled=current == 0):
                    save_answer()
                    navigate_to_question(current - 1)
                    st.rerun()
            
            with b2:
                if st.button("🗑️ Clear"):
                    clear_answer()
                    st.rerun()
            
            with b3:
                if st.button("🔖 Mark"):
                    mark_for_review()
                    if current < 74:
                        navigate_to_question(current + 1)
                    st.rerun()
            
            with b4:
                if st.button("💾 Save ➡️", type="primary"):
                    save_answer()
                    if current < 74:
                        navigate_to_question(current + 1)
                    st.rerun()
        
        with col_p:
            st.markdown("### 🎯 Palette")
            st.markdown("**Physics**")
            cols = st.columns(5)
            for i in range(25):
                with cols[i % 5]:
                    if st.button(str(i + 1), key=f"p{i}"):
                        save_answer()
                        navigate_to_question(i)
                        st.rerun()
            
            st.markdown("**Chemistry**")
            cols = st.columns(5)
            for i in range(25, 50):
                with cols[(i - 25) % 5]:
                    if st.button(str(i + 1), key=f"c{i}"):
                        save_answer()
                        navigate_to_question(i)
                        st.rerun()
            
            st.markdown("**Maths**")
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
            
            if st.button("✅ Submit", type="primary", use_container_width=True):
                st.session_state.exam_submitted = True
                st.rerun()
    
    # Results
    else:
        display_results(questions)

# Run
main()
