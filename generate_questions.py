"""
Script to generate questions.json for JEE Exam Simulator
Run this to create/update your question bank
"""

import json

def create_questions():
    questions = []
    
    # PHYSICS (1-25)
    physics = [
        {
            "id": 1, "subject": "Physics", "type": "mcq",
            "question": r"In order to convert a milliammeter of range 1.0 mA and resistance 1.0 $\Omega$ into a voltmeter of range 10 V, a resistance of how many ohms should be connected with it and in what manner?",
            "options": ["999 $\Omega$ in series", "999 $\Omega$ in parallel", "9,999 $\Omega$ in series", "9,999 $\Omega$ in parallel"],
            "correct": 2,
            "solution": r"To convert milliammeter to voltmeter, we need high resistance in series. $V = I(r + R)$, $10 = 10^{-3}(1 + R)$, $R = 9999 \Omega$",
            "is_latex": False
        },
        {
            "id": 2, "subject": "Physics", "type": "mcq",
            "question": r"The electron emitted in $\beta$-radiation originates from:",
            "options": ["inner orbits of atoms", "free electrons existing in nuclei", "decay of a neutron in a nucleus", "photon escaping from the nucleus"],
            "correct": 2,
            "solution": r"$\beta$-radiation occurs when a neutron decays into a proton and an electron. The electron is then emitted.",
            "is_latex": False
        },
        {
            "id": 3, "subject": "Physics", "type": "mcq",
            "question": r"A conducting wheel is rolling on the ground in a uniform magnetic field $B_0$. The emf induced between points A and B; $V_A - V_B$ will be:",
            "options": [r"$2B_0\omega(\sqrt{3}R)$", r"$\frac{3B_0\omega R^2}{2}$", r"$2B_0\omega(2R)$", r"$\frac{5B_0\omega R^2}{2}$"],
            "correct": 1,
            "solution": r"Using motional emf formula: $\epsilon = \frac{B_0\omega R^2}{2}(\sqrt{3})^2 = \frac{3B_0\omega R^2}{2}$",
            "is_latex": False
        },
        {
            "id": 4, "subject": "Physics", "type": "mcq",
            "question": r"Forces acting on a particle moving in a straight line varies with the velocity of the particle as $F = \alpha v$ where $\alpha$ is constant. The work done by this force in time interval $t$ is:",
            "options": [r"$\alpha t$", r"$\frac{\alpha t^2}{2}$", r"$\alpha^2 t$", r"$\alpha^2 t^2$"],
            "correct": 0,
            "solution": r"$W = \int F \cdot v \, dt = \int \alpha v \cdot v \, dt$. Since $F = \alpha v$, work done is $\alpha t$",
            "is_latex": False
        },
        {
            "id": 5, "subject": "Physics", "type": "mcq",
            "question": r"In the circuit with diodes $D_1$ and $D_2$, 20V supply and 5$\Omega$ resistor, choose the correct answer:",
            "options": ["Voltage across $D_2$ is 20 Volt", "Voltage across $D_1$ is 20 Volt", "Current through diode $D_1$ is 4A", "Current through diode $D_1$ is 0 A"],
            "correct": 2,
            "solution": r"$D_1$ acts as short circuit, $D_2$ acts as open circuit. Current through $D_1 = \frac{20}{5} = 4A$",
            "is_latex": False
        },
        {
            "id": 6, "subject": "Physics", "type": "mcq",
            "question": r"A ferromagnetic substance when heated beyond Curie temperature becomes:",
            "options": ["diamagnetic", "ferromagnetic", "nonmagnetic", "paramagnetic"],
            "correct": 3,
            "solution": "Above Curie temperature, ferromagnetic materials lose their permanent magnetic properties and become paramagnetic.",
            "is_latex": False
        },
        {
            "id": 7, "subject": "Physics", "type": "mcq",
            "question": r"The resultant of $\vec{A}$ and $\vec{B}$ is perpendicular to $\vec{A}$. What is the angle between $\vec{A}$ and $\vec{B}$?",
            "options": [r"$\cos^{-1}\left(\frac{A}{B}\right)$", r"$\cos^{-1}\left(-\frac{A}{B}\right)$", r"$\sin^{-1}\left(\frac{A}{B}\right)$", r"$\sin^{-1}\left(-\frac{A}{B}\right)$"],
            "correct": 1,
            "solution": r"When resultant is perpendicular to $\vec{A}$: $\cos(180° - \theta) = \frac{A}{B}$, so $\theta = \cos^{-1}\left(-\frac{A}{B}\right)$",
            "is_latex": False
        },
        {
            "id": 8, "subject": "Physics", "type": "mcq",
            "question": r"In a radioactive reaction an unstable nucleus A disintegrates into a stable nucleus B. But A is generated at a constant rate of $q$ nucleus per second. At steady state number of nucleus of A will be:",
            "options": ["$q$", r"$\frac{q}{\lambda}$", r"$q - \lambda$", r"$\frac{q}{q-\lambda}$"],
            "correct": 1,
            "solution": r"At steady state: Rate of generation = Rate of decay. $q = \lambda N_A$, therefore $N_A = \frac{q}{\lambda}$",
            "is_latex": False
        },
        {
            "id": 9, "subject": "Physics", "type": "mcq",
            "question": r"A block slides down an inclined plane of inclination $\theta$ with constant velocity. It is then projected up the plane with an initial speed $u$. How far up the incline will it move before coming to rest?",
            "options": [r"$\frac{u^2}{4g\sin\theta}$", r"$\frac{u^2}{g\sin\theta}$", r"$\frac{u^2}{2g\sin\theta}$", r"$\frac{u^2}{4g}$"],
            "correct": 0,
            "solution": r"Since block slides with constant velocity, friction $= mg\sin\theta$. When going up: deceleration $= 2g\sin\theta$. Distance $= \frac{u^2}{4g\sin\theta}$",
            "is_latex": False
        },
        {
            "id": 10, "subject": "Physics", "type": "mcq",
            "question": r"Three conductors 1, 2, and 3 each carrying the same current $I$ are placed in a uniform magnetic field $B$. The forces experienced by conductors 1, 2 and 3 are $F_1$, $F_2$ and $F_3$, respectively:",
            "options": [r"$F_3 > F_2 > F_1$", r"$F_1 \neq 0$; $F_2 \neq 0$; $F_3 = 0$", r"$F_1$ acts upwards, $F_2$ acts downwards; $F_3 = 0$", "All experience the same force in same direction"],
            "correct": 3,
            "solution": r"Force $F = I(\vec{L} \times \vec{B})$. All conductors have same effective length and current, so all experience same force.",
            "is_latex": False
        },
    ]
    
    # Add more physics questions (11-25)
    for i in range(11, 26):
        physics.append({
            "id": i, "subject": "Physics", "type": "mcq" if i <= 20 else ("numerical" if i <= 22 else "decimal"),
            "question": f"Physics Question {i} (Add your question here with proper LaTeX formatting)",
            "options": ["Option A", "Option B", "Option C", "Option D"] if i <= 20 else None,
            "correct": 0 if i <= 20 else (0 if i <= 22 else 0.0),
            "solution": f"Solution for question {i}",
            "is_latex": False
        })
    
    questions.extend(physics)
    
    # CHEMISTRY (26-50)
    chemistry = []
    for i in range(26, 51):
        chemistry.append({
            "id": i, "subject": "Chemistry", "type": "mcq" if i <= 45 else ("numerical" if i <= 47 else "decimal"),
            "question": f"Chemistry Question {i} (Add your question here with proper LaTeX formatting)",
            "options": ["Option A", "Option B", "Option C", "Option D"] if i <= 45 else None,
            "correct": 0 if i <= 45 else (0 if i <= 47 else 0.0),
            "solution": f"Solution for question {i}",
            "is_latex": False
        })
    questions.extend(chemistry)
    
    # MATHEMATICS (51-75)
    mathematics = [
        {
            "id": 51, "subject": "Mathematics", "type": "mcq",
            "question": r"Let $a \neq 1$ be a real number and $f(x) = \log_a(x^2)$ for $x > 0$. If $f^{-1}$ is the inverse function of $f$ and $b$ and $c$ are real numbers then $f^{-1}(b + c)$ is equal to:",
            "options": [r"$f^{-1}(b) \cdot f^{-1}(c)$", r"$f^{-1}(b) + f^{-1}(c)$", r"$f^{-1}(bc)$", r"$\frac{1}{f^{-1}(b) \cdot f^{-1}(c)}$"],
            "correct": 0,
            "solution": r"$f(x) = 2\log_a(x)$, $f^{-1}(y) = a^{y/2}$. $f^{-1}(b+c) = a^{(b+c)/2} = a^{b/2} \cdot a^{c/2} = f^{-1}(b) \cdot f^{-1}(c)$",
            "is_latex": False
        },
        {
            "id": 52, "subject": "Mathematics", "type": "mcq",
            "question": r"The function $f(x) = \frac{\ln(e + x)}{\ln(e - x)}$ $(x \neq 0)$ is:",
            "options": [r"increasing in $[0, \infty)$", r"decreasing in $[0, \infty)$", r"increasing in $[0, e)$ and decreasing in $(e, \infty)$", r"decreasing in $[0, e)$ and increasing in $(e, \infty)$"],
            "correct": 1,
            "solution": r"Taking derivative and analyzing: $f'(x) < 0$ for all $x > 0$, hence decreasing in $[0, \infty)$",
            "is_latex": False
        },
        {
            "id": 53, "subject": "Mathematics", "type": "mcq",
            "question": r"Locus of all points $P(x, y)$ satisfying $x^3 + y^3 = 3xy + 1$ consists of union of:",
            "options": ["a line and an isolated point", "a line pair and an isolated point", "a line and a circle", "a circle and an isolated point"],
            "correct": 0,
            "solution": r"$(x + y - 1)(x^2 + y^2 - xy + x + y + 1) = 0$. This gives line $x + y = 1$ and an isolated point.",
            "is_latex": False
        },
    ]
    
    # Add more math questions
    for i in range(54, 76):
        mathematics.append({
            "id": i, "subject": "Mathematics", "type": "mcq" if i <= 70 else ("numerical" if i <= 72 else "decimal"),
            "question": f"Mathematics Question {i} (Add your question here with proper LaTeX formatting)",
            "options": ["Option A", "Option B", "Option C", "Option D"] if i <= 70 else None,
            "correct": 0 if i <= 70 else (0 if i <= 72 else 0.0),
            "solution": f"Solution for question {i}",
            "is_latex": False
        })
    questions.extend(mathematics)
    
    return questions

def main():
    print("=" * 60)
    print("JEE EXAM SIMULATOR - Question Bank Generator")
    print("=" * 60)
    print("\nGenerating questions.json...")
    
    questions = create_questions()
    
    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully created questions.json with {len(questions)} questions")
    print("\n📝 Note: This is a template with sample questions.")
    print("   Please edit questions.json to add your complete question bank.")
    print("   Use LaTeX formatting (e.g., $x^2$, $\\frac{1}{2}$) for math expressions")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
