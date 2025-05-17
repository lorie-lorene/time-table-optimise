
import json
import pandas as pd
from ortools.sat.python import cp_model
import random
import numpy as np

class TimeTableGenerator:
    def __init__(self, rooms_file, courses_file):
        # Load data from JSON files
        self.load_data(rooms_file, courses_file)
        
        # Define constants
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.periods = ['7:00am - 9:55am', '10:05am - 12:55pm', '1:05pm - 3:55pm', 
                       '4:05pm - 6:55pm', '7:05pm - 9:55pm']
        self.period_weights = [1, 2, 3, 4, 5]  # Lower weights have higher priority
        
        # Initialize the model
        self.model = cp_model.CpModel()
        
    def load_data(self, rooms_file, courses_file):
        # Load rooms data
        with open(rooms_file, 'r') as f:
            rooms_data = json.load(f)
        
        # Extract all rooms
        self.rooms = []
        for faculty in rooms_data:
            for room in rooms_data[faculty]:
                self.rooms.append({
                    'num': room['num'],
                    'capacity': int(room['capacite']),
                    'building': room['batiment'],
                    'filiere': room['filier']
                })
        
        # Load courses data
        with open(courses_file, 'r') as f:
            self.courses_data = json.load(f)
            
        # Extract all levels and their courses
        self.all_courses = {}
        self.classes = []
        
        for level, semesters in self.courses_data['niveau'].items():
            for semester, data in semesters.items():
                class_id = f"Level-{level}-{semester}"
                self.classes.append(class_id)
                
                self.all_courses[class_id] = []
                for subject in data.get('subjects', []):
                    # Skip subjects without a name or code
                    if not isinstance(subject.get('name', ''), str) or not subject.get('code', ''):
                        continue
                        
                    # Get teacher names
                    teachers = []
                    if subject.get('Course Lecturer') and isinstance(subject['Course Lecturer'], list):
                        teachers.extend([t for t in subject['Course Lecturer'] if t and isinstance(t, str)])
                    
                    if not teachers:
                        teacher = "TBD"
                    else:
                        teacher = ", ".join(teachers)
                    
                    course_info = {
                        'name': subject.get('name', 'Unnamed Course'),
                        'code': subject.get('code', ''),
                        'teacher': teacher,
                        'credits': subject.get('credit', 0)
                    }
                    
                    self.all_courses[class_id].append(course_info)
        
    def build_model(self):
        # Create variables
        self.assignment_vars = {}
        
        # For each class, course, room, day, and period, create a binary variable
        for class_id in self.classes:
            for course_idx, course in enumerate(self.all_courses[class_id]):
                for room_idx, room in enumerate(self.rooms):
                    for day_idx, day in enumerate(self.days):
                        for period_idx, period in enumerate(self.periods):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            self.assignment_vars[var_key] = self.model.NewBoolVar(f"assign_{var_key}")
        
        # Constraint 1: No class can be scheduled in multiple rooms with different courses at the same time
        for class_id in self.classes:
            for day_idx in range(len(self.days)):
                for period_idx in range(len(self.periods)):
                    # List all possible assignments for this class at this time
                    assignments = []
                    for course_idx in range(len(self.all_courses[class_id])):
                        for room_idx in range(len(self.rooms)):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            if var_key in self.assignment_vars:
                                assignments.append(self.assignment_vars[var_key])
                    
                    # Ensure at most one assignment is made
                    if assignments:
                        self.model.Add(sum(assignments) <= 1)
        
        # Constraint 2: All courses for a class should be scheduled exactly once per week (CRITICAL)
        for class_id in self.classes:
            for course_idx in range(len(self.all_courses[class_id])):
                # List all possible assignments for this course
                assignments = []
                for room_idx in range(len(self.rooms)):
                    for day_idx in range(len(self.days)):
                        for period_idx in range(len(self.periods)):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            if var_key in self.assignment_vars:
                                assignments.append(self.assignment_vars[var_key])
                
                # Ensure exactly one assignment is made - HARD CONSTRAINT
                if assignments:
                    self.model.Add(sum(assignments) == 1)
        
        # Constraint 3: A class should not be scheduled to take a course not in its curriculum
        # (This is implicitly handled by how we created the variables)
        
        # Constraint 4: No room can be used by multiple classes at the same time
        for room_idx in range(len(self.rooms)):
            for day_idx in range(len(self.days)):
                for period_idx in range(len(self.periods)):
                    # List all possible assignments for this room at this time
                    assignments = []
                    for class_id in self.classes:
                        for course_idx in range(len(self.all_courses[class_id])):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            if var_key in self.assignment_vars:
                                assignments.append(self.assignment_vars[var_key])
                    
                    # Ensure at most one assignment is made
                    if assignments:
                        self.model.Add(sum(assignments) <= 1)
        
        # Constraint 5: No teacher can teach multiple classes at the same time
        # First, get all teachers
        teachers = set()
        teacher_courses = {}
        
        for class_id in self.classes:
            for course_idx, course in enumerate(self.all_courses[class_id]):
                teacher = course['teacher']
                teachers.add(teacher)
                
                if teacher not in teacher_courses:
                    teacher_courses[teacher] = []
                
                teacher_courses[teacher].append((class_id, course_idx))
        
        # Now add the constraints
        for teacher in teachers:
            for day_idx in range(len(self.days)):
                for period_idx in range(len(self.periods)):
                    # List all possible assignments for this teacher at this time
                    assignments = []
                    for class_id, course_idx in teacher_courses.get(teacher, []):
                        for room_idx in range(len(self.rooms)):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            if var_key in self.assignment_vars:
                                assignments.append(self.assignment_vars[var_key])
                    
                    # Ensure at most one assignment is made
                    if assignments:
                        self.model.Add(sum(assignments) <= 1)
        
        # NEW: adding Constraint 6 - Encourage progression to later periods if morning is full just for have all cours schedul
        # Add preference variables to prefer earlier time slots
        self.period_preference_vars = {}
        
        for class_id in self.classes:
            for course_idx in range(len(self.all_courses[class_id])):
                # Create a preference variable for this course
                for period_idx in range(len(self.periods)):
                    pref_key = (class_id, course_idx, period_idx)
                    self.period_preference_vars[pref_key] = self.model.NewBoolVar(f"pref_{pref_key}")
                    
                    # Link this preference to any assignment at this period
                    assignments_in_period = []
                    for room_idx in range(len(self.rooms)):
                        for day_idx in range(len(self.days)):
                            var_key = (class_id, course_idx, room_idx, day_idx, period_idx)
                            if var_key in self.assignment_vars:
                                assignments_in_period.append(self.assignment_vars[var_key])
                    
                    if assignments_in_period:
                        # pref = (assignment1 OR assignment2 OR ...)
                        self.model.AddBoolOr(assignments_in_period).OnlyEnforceIf(self.period_preference_vars[pref_key])
                        self.model.AddBoolAnd([v.Not() for v in assignments_in_period]).OnlyEnforceIf(self.period_preference_vars[pref_key].Not())
        
        # Objective: Minimize the sum of period weights
        objective_terms = []
        
        for pref_key, var in self.period_preference_vars.items():
            _, _, period_idx = pref_key
            weight = self.period_weights[period_idx]
            objective_terms.append(weight * var)
        
        # Minimize the sum of weights
        self.model.Minimize(sum(objective_terms))
    
    def solve_model(self):
        # Create a solver and solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300  # Limit solving time to 5 minutes
        
        # Enable intermediate solutions to get partial results if time limit is reached
        solver.parameters.enumerate_all_solutions = False
        solver.parameters.linearization_level = 0
        
        # Print progress
        print("Solving the model. This may take several minutes...")
        status = solver.Solve(self.model)
        
        print(f"Solver status: {status}")
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution found with status {status}")
            
            # Check if all courses are scheduled
            scheduled_count = 0
            for var_key, var in self.assignment_vars.items():
                if solver.Value(var) == 1:
                    scheduled_count += 1
            
            total_courses = sum(len(courses) for courses in self.all_courses.values())
            print(f"Scheduled {scheduled_count} out of {total_courses} courses")
            
            # Process the solution
            self.timetable = self.process_solution(solver)
            return True
        else:
            print(f"No solution found. Status: {status}")
            return False
    
    def process_solution(self, solver):
        # Create empty timetable
        timetable = {}
        
        for class_id in self.classes:
            timetable[class_id] = [[None for _ in range(len(self.periods))] for _ in range(len(self.days))]
        
        # Fill in the timetable based on the solution
        for var_key, var in self.assignment_vars.items():
            if solver.Value(var) == 1:
                class_id, course_idx, room_idx, day_idx, period_idx = var_key
                
                course = self.all_courses[class_id][course_idx]
                room = self.rooms[room_idx]
                
                # Store the assignment
                timetable[class_id][day_idx][period_idx] = {
                    'course_code': course['code'],
                    'course_name': course['name'],
                    'teacher': course['teacher'],
                    'room': room['num'],
                    'building': room['building']
                }
        
        return timetable
    
    def generate_combined_html_timetable(self):
        """Generate a single HTML file containing all timetables with navigation"""
        
        # Start HTML visualisation
        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emplois du Temps - Département d'Informatique</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap');
                
                :root {
                    --primary-color: #1a237e;
                    --primary-light: #534bae;
                    --primary-dark: #000051;
                    --accent-color: #ff6f00;
                    --text-on-primary: #ffffff;
                    --text-primary: #212121;
                    --text-secondary: #757575;
                    --background-color: #f5f5f5;
                    --card-color: #ffffff;
                    --border-color: #e0e0e0;
                    --highlight-color: #e3f2fd;
                }

                body {
                    font-family: 'Roboto', sans-serif;
                    margin: 0;
                    padding: 0;
                    color: var(--text-primary);
                    background-color: var(--background-color);
                    line-height: 1.6;
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .header {
                    background-color: var(--primary-color);
                    color: var(--text-on-primary);
                    padding: 20px 0;
                    text-align: center;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }

                .header h1 {
                    font-family: 'Montserrat', sans-serif;
                    font-size: 2.5rem;
                    margin-bottom: 5px;
                    font-weight: 700;
                }

                .header h2 {
                    font-size: 1.8rem;
                    margin-top: 0;
                    margin-bottom: 5px;
                    font-weight: 500;
                }

                .header h3 {
                    font-size: 1.2rem;
                    margin-top: 0;
                    font-weight: 400;
                    opacity: 0.9;
                }

                .nav-container {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                    gap: 10px;
                }

                .nav-button {
                    padding: 12px 20px;
                    background-color: var(--primary-color);
                    color: var(--text-on-primary);
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }

                .nav-button:hover {
                    background-color: var(--primary-light);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }

                .nav-button.active {
                    background-color: var(--accent-color);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }

                .timetable-container {
                    display: none;
                    background: var(--card-color);
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }

                .timetable-container.active {
                    display: block;
                    animation: fadeIn 0.5s ease;
                }

                .timetable-title {
                    color: var(--primary-color);
                    border-bottom: 2px solid var(--primary-light);
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 600;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    border-radius: 8px;
                    overflow: hidden;
                }

                th, td {
                    border: 1px solid var(--border-color);
                    padding: 12px;
                    text-align: center;
                    font-size: 0.9rem;
                }

                th {
                    background-color: var(--primary-color);
                    color: var(--text-on-primary);
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                tr:nth-child(even) {
                    background-color: rgba(0,0,0,0.02);
                }

                .time-col {
                    width: 15%;
                    background-color: var(--primary-dark);
                    color: var(--text-on-primary);
                    font-weight: 500;
                }

                .course-container {
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #e8eaf6;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                    height: 100%;
                }

                .course-container:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }

               .course-name {
		            font-weight: 700;
                    color: var(--primary-color);
                    margin-bottom: 5px;
                    font-size: 0.85rem;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
}
                .course-code {
                    display: inline-block;
                    background-color: var(--primary-color);
                    color: white;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.85rem;
                    margin-bottom: 8px;
                }

                .instructor {
                    font-size: 0.9em;
                    margin-top: 5px;
                    color: var(--text-secondary);
                }

                .room {
                    font-size: 0.85em;
                    color: var(--text-secondary);
                    margin-top: 3px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .room::before {
                    content: '📍';
                    margin-right: 5px;
                }

                .empty-cell {
                    background-color: #fafafa;
                }

                .legend {
                    margin-top: 30px;
                    background-color: var(--card-color);
                    border-radius: 8px;
                    padding: 15px 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }

                .legend h3 {
                    color: var(--primary-color);
                    border-bottom: 2px solid var(--primary-light);
                    padding-bottom: 10px;
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 600;
                }

                .legend-items {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }

                .legend-item {
                    flex: 1 0 30%;
                    margin-bottom: 10px;
                    padding: 8px 12px;
                    border-radius: 6px;
                    background-color: #f5f5f5;
                    transition: all 0.2s ease;
                }

                .legend-item:hover {
                    background-color: var(--highlight-color);
                    transform: translateY(-2px);
                }

                .legend-code {
                    font-weight: 700;
                    color: var(--primary-color);
                    display: inline-block;
                    margin-right: 5px;
                }

                .print-button {
                    display: block;
                    margin: 20px auto;
                    padding: 12px 25px;
                    background-color: var(--accent-color);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }

                .print-button:hover {
                    background-color: #ff8f00;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }

                .footer {
                    text-align: center;
                    padding: 20px;
                    margin-top: 50px;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                    border-top: 1px solid var(--border-color);
                }

                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @media print {
                    .nav-container, .print-button, .footer {
                        display: none;
                    }
                    .timetable-container {
                        display: block;
                        page-break-after: always;
                        box-shadow: none;
                        margin: 0;
                        padding: 0;
                    }
                    body {
                        padding: 0;
                        font-size: 12px;
                        background-color: white;
                    }
                    .header {
                        box-shadow: none;
                        padding: 10px 0;
                    }
                    table {
                        page-break-inside: avoid;
                        box-shadow: none;
                    }
                    .course-container {
                        box-shadow: none;
                    }
                    .legend {
                        box-shadow: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Emplois du Temps</h1>
                <h2>Département d'Informatique</h2>
                <h3>Année académique 2024-2025</h3>
            </div>
            
            <div class="container">
                <div class="nav-container">
        """
        
        # Add navigation buttons
        for class_id in sorted(self.classes):
            level, semester = class_id.split('-')[1], class_id.split('-')[2]
            html += f"""
                    <button class="nav-button" onclick="showTimetable('{class_id}')">Niveau {level} - Semestre {semester}</button>
            """
            
        html += """
                </div>
                
                <button class="print-button" onclick="window.print()">Imprimer tous les emplois du temps</button>
        """
        
        # Add timetable containers
        for class_id in sorted(self.classes):
            level, semester = class_id.split('-')[1], class_id.split('-')[2]
            
            html += f"""
                <div id="{class_id}" class="timetable-container">
                    <h2 class="timetable-title">Niveau {level} - Semestre {semester}</h2>
                    <table>
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>
            """
            
            # Add day headers
            for day in self.days:  # Including Saturday
                html += f"<th>{day}</th>"
                
            html += """
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add rows for each period
            for period_idx, period in enumerate(self.periods):
                html += f"""
                            <tr>
                                <td class="time-col">{period}</td>
                """
                
                # Add cells for each day
                for day_idx in range(len(self.days)):
                    cell = self.timetable[class_id][day_idx][period_idx]
                    
                    if cell:
                        html += f"""
                                <td>
                                    <div class="course-container">
                                        <div class="course-code">{cell['course_code']}</div>
                                        <div class="instructor">{cell['teacher']}</div>
                                        <div class="room">{cell['building']} {cell['room']}</div>
                                    </div>
                                </td>
                        """
                    else:
                        html += '<td class="empty-cell"></td>'
                
                html += """
                            </tr>
                """
                
            html += """
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
                        <div class="legend-items">
            """
            
            # Add course legend
            for course in self.all_courses[class_id]:
                html += f"""
                            <div class="legend-item">
                                <span class="legend-code">{course['code']}</span>: {course['name']}
                            </div>
                """
                
            html += """
                        </div>
                    </div>
                </div>
            """
            
        # Add JavaScript for navigation
        html += """
                <div class="footer">
                    © 2025 Département d'Informatique - Tous droits réservés(Spring_Shogun🍃🍃)
                </div>
            </div>
            
            <script>
                // Show the first timetable by default
                document.addEventListener('DOMContentLoaded', function() {
                    const firstButton = document.querySelector('.nav-button');
                    const firstTimetable = document.querySelector('.timetable-container');
                    
                    if (firstButton && firstTimetable) {
                        firstButton.classList.add('active');
                        firstTimetable.classList.add('active');
                    }
                });
                
                // Function to show the selected timetable
                function showTimetable(id) {
                    // Hide all timetables
                    const timetables = document.querySelectorAll('.timetable-container');
                    timetables.forEach(timetable => {
                        timetable.classList.remove('active');
                    });
                    
                    // Remove active class from all buttons
                    const buttons = document.querySelectorAll('.nav-button');
                    buttons.forEach(button => {
                        button.classList.remove('active');
                    });
                    
                    // Show the selected timetable
                    const selectedTimetable = document.getElementById(id);
                    if (selectedTimetable) {
                        selectedTimetable.classList.add('active');
                    }
                    
                    // Add active class to the clicked button
                    const buttonSelector = `.nav-button[onclick="showTimetable('${id}')"]`;
                    const selectedButton = document.querySelector(buttonSelector);
                    if (selectedButton) {
                        selectedButton.classList.add('active');
                    }
                }
            </script>
        </body>
        </html>
        """
        
        return html
    
    def generate_markdown_timetable(self, class_id):
        """Generate Markdown for a specific class timetable"""
        
        if class_id not in self.timetable:
            return f"No timetable found for {class_id}"
            
        # Extract level and semester from class_id
        level, semester = class_id.split('-')[1], class_id.split('-')[2]
        
        markdown = f"""# Emploi du Temps - Niveau {level} - Semestre {semester}
## Département d'Informatique
### Année académique 2024-2025

| Horaire | Lundi | Mardi | Mercredi | Jeudi | Vendredi | Samedi |
|---------|-------|-------|----------|-------|----------|--------|
"""
        
        # Add rows for each period
        for period_idx, period in enumerate(self.periods):
            row = f"| {period} | "
            
            # Add cells for each day - ALL 6 DAYS INCLUDING SATURDAY
            for day_idx in range(6):
                cell = self.timetable[class_id][day_idx][period_idx]
                
                if cell:
                    row += f"**{cell['course_code']}** ({cell['teacher']})<br>{cell['building']} {cell['room']} | "
                else:
                    row += " | "
            
            markdown += row + "\n"
            
        markdown += """
## Légende
"""
        
        # Add course legend
        for course in self.all_courses[class_id]:
            markdown += f"- **{course['code']}**: {course['name']}\n"
            
        return markdown

def main():
    # Create the timetable generator
    generator = TimeTableGenerator('data_salles.json', 'data_cours.json')
    
    # Build the model
    print("Building the constraint model...")
    generator.build_model()
    
    # Solve the model
    print("Solving the model (this may take a few minutes)...")
    if generator.solve_model():
        print("Model solved successfully!")
        
        # Generate combined HTML timetable with all schedules
        print("Generating combined timetable...")
        combined_html = generator.generate_combined_html_timetable()
        
        # Save combined HTML timetable
        with open("all_timetables.html", 'w', encoding='utf-8') as f:
            f.write(combined_html)
        print("Saved all_timetables.html")
        
        # Also save individual markdown versions if needed
        for class_id in generator.classes:
            markdown = generator.generate_markdown_timetable(class_id)
            filename = f"timetable_{class_id.replace('-', '_')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Saved {filename}")
            
        print("All timetables generated successfully!")
    else:
        print("Failed to find a feasible solution. Try relaxing some constraints.")

if __name__ == "__main__":
    main()
