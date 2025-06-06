"""
Timetable Generator using Google OR-Tools for Computer Science Department

Specifications:
1. No class can be scheduled in multiple classrooms with different courses/teachers at the same time
2. All courses for a class should be scheduled exactly once per week
3. A class should not be scheduled to take a course not in its curriculum
4. If a course can't be scheduled in the morning, schedule it in the next available period
5. ALL courses MUST be scheduled - this is a hard constraint

Periods:
- p1: 7:00am - 9:55am (weight 1)
- p2: 10:05am - 12:55pm (weight 2)
- p3: 1:05pm - 3:55pm (weight 3)
- p4: 4:05pm - 6:55pm (weight 4)
- p5: 7:05pm - 9:55pm (weight 5)
"""

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
        
        # NEW: Constraint 6 - Encourage progression to later periods if morning is full
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
        
        # Start HTML document
        html = '''
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emplois du Temps - Département d\'Informatique</title>
            <style>
                @import url(\'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap\');
                @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap\');
                
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
                    font-family: \'Roboto\', sans-serif;
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
                    font-family: \'Montserrat\', sans-serif;
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
                    font-family: \'Montserrat\', sans-serif;
                    font-weight: 600;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    border-radius: 8px;
                    overflow: hidden;
                    table-layout: fixed;
                }

                th, td {
                    border: 1px solid var(--border-color);
                    padding: 10px 8px;
                    text-align: center;
                    font-size: 0.85rem;
                    height: 120px;
                    vertical-align: top;
                    overflow: hidden;
                }

                th {
                    background-color: var(--primary-color);
                    color: var(--text-on-primary);
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    height: auto;
                    vertical-align: middle;
                }

                tr:nth-child(even) {
                    background-color: rgba(0,0,0,0.02);
                }

                .time-col {
                    width: 12%;
                    background-color: var(--primary-dark);
                    color: var(--text-on-primary);
                    font-weight: 500;
                    vertical-align: middle;
                }

                .course-container {
                    border-radius: 6px;
                    padding: 8px;
                    background-color: #e8eaf6;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                    height: 100%;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
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
                    padding: 3px 6px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    margin-bottom: 5px;
                }

                .instructor {
                    font-size: 0.75em;
                    margin-top: 3px;
                    color: var(--text-secondary);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .room {
                    font-size: 0.75em;
                    color: var(--text-secondary);
                    margin-top: 3px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .room::before {
                    content: \'📍\';
                    margin-right: 3px;
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
                    font-family: \'Montserrat\', sans-serif;
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
                    font-size: 0.9rem;
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
                
                /* Stats section */
                .stats-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .stat-card {
                    flex: 1;
                    min-width: 200px;
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    text-align: center;
                    transition: all 0.3s ease;
                }
                
                .stat-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                
                .stat-value {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--primary-color);
                    margin: 10px 0;
                }
                
                .stat-label {
                    color: var(--text-secondary);
                    font-size: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                /* Filter controls */
                .filter-controls {
                    background-color: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }
                
                .filter-title {
                    font-weight: 600;
                    color: var(--primary-color);
                    margin-bottom: 10px;
                }
                
                .filter-options {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }
                
                .filter-option {
                    padding: 8px 15px;
                    background-color: #e8eaf6;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    transition: all 0.2s ease;
                }
                
                .filter-option:hover {
                    background-color: var(--primary-light);
                    color: white;
                }
                
                .filter-option.active {
                    background-color: var(--primary-color);
                    color: white;
                }

                @media print {
                    .nav-container, .print-button, .footer, .stats-container, .filter-controls {
                        display: none !important;
                    }
                    .timetable-container {
                        display: block !important;
                        page-break-after: always;
                        box-shadow: none;
                        margin: 0;
                        padding: 0;
                        border-radius: 0;
                    }
                    .header {
                        box-shadow: none;
                        padding: 10px 0;
                        margin-bottom: 10px;
                    }
                    .header h1 {
                        font-size: 20px;
                        margin-bottom: 2px;
                    }
                    .header h2 {
                        font-size: 16px;
                        margin-bottom: 2px;
                    }
                    .header h3 {
                        font-size: 14px;
                    }
                    .timetable-title {
                        font-size: 18px;
                        margin-bottom: 10px;
                    }
                    body {
                        padding: 0;
                        font-size: 10px;
                        background-color: white;
                    }
                    table {
                        page-break-inside: avoid;
                        box-shadow: none;
                        width: 100%;
                    }
                    th, td {
                        padding: 6px 4px;
                        font-size: 9px;
                        height: 80px;
                    }
                    .course-container {
                        box-shadow: none;
                        padding: 4px;
                    }
                    .course-name {
                        font-size: 9px;
                        margin-bottom: 2px;
                    }
                    .course-code {
                        font-size: 8px;
                        padding: 2px 4px;
                        margin-bottom: 2px;
                    }
                    .instructor, .room {
                        font-size: 7px;
                        margin-top: 1px;
                    }
                    .legend {
                        box-shadow: none;
                        padding: 10px;
                    }
                    .legend h3 {
                        font-size: 14px;
                    }
                    .legend-item {
                        font-size: 9px;
                        padding: 4px 6px;
                    }
                    .container {
                        padding: 0;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Emplois du Temps</h1>
                <h2>Département d\'Informatique</h2>
                <h3>Année académique 2024-2025</h3>
            </div>
            
            <div class="container">
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-label">Nombre de Cours</div>
                        <div class="stat-value">"TOTAL_COURSES"</div>
                        <div>Programmés cette semaine</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Salles Utilisées</div>
                        <div class="stat-value">"ROOMS_USED"</div>
                        <div>Sur "TOTAL_ROOMS" disponibles</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Taux d\'Occupation</div>
                        <div class="stat-value">"OCCUPANCY_RATE"%</div>
                        <div>Des heures disponibles</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Cours en Matinée</div>
                        <div class="stat-value">"MORNING_PERCENTAGE"%</div>
                        <div>Des cours programmés</div>
                    </div>
                </div>
                
                <div class="filter-controls">
                    <div class="filter-title">Filtrer par:</div>
                    <div class="filter-options">
                        <div class="filter-option active" onclick="filterTimetables(\'all\')">Tous</div>
                        <div class="filter-option" onclick="filterTimetables(\'morning\')">Matinée uniquement</div>
                        <div class="filter-option" onclick="filterTimetables(\'afternoon\')">Après-midi uniquement</div>
                        <div class="filter-option" onclick="filterTimetables(\'amphi\')">Grand Amphi</div>
                        <div class="filter-option" onclick="filterTimetables(\'tdtp\')">TD et TP</div>
                    </div>
                </div>
                
                <div class="nav-container">'''
        # Add navigation buttons
        for class_id in sorted(self.classes):
            level, semester = class_id.split('-')[1], class_id.split('-')[2]
            html += f'''
                    <button class="nav-button" onclick="showTimetable(\'{class_id}\')">Niveau {level} - Semestre {semester}</button>'''
            
        html += '''
                </div>
                
                <button class="print-button" onclick="window.print()">Imprimer tous les emplois du temps</button>'''
        
        # Add timetable containers
        for class_id in sorted(self.classes):
            level, semester = class_id.split('-')[1], class_id.split('-')[2]
            
            html += f'''
                <div id="{class_id}" class="timetable-container">
                    <h2 class="timetable-title">Niveau {level} - Semestre {semester}</h2>
                    <table>
                        <thead>
                            <tr>
                                <th class="time-col">Horaire</th>'''
            
            # Add day headers
            for day in self.days:  # Including Saturday
                html += f'''<th>{day}</th>'''
                
            html += '''
                            </tr>
                        </thead>
                        <tbody>'''
            
            # Add rows for each period
            for period_idx, period in enumerate(self.periods):
                html += f'''
                            <tr class="period-row {'morning-row' if period_idx < 2 else 'afternoon-row'}">
                                <td class="time-col">{period}</td>'''
                
                # Add cells for each day
                for day_idx in range(len(self.days)):
                    cell = self.timetable[class_id][day_idx][period_idx]
                    
                    if cell:
                        # Determine if amphi or td/tp based on room
                        room_class = "amphi-cell" if "AMPHI" in cell['building'] else "tdtp-cell"
                        
                        html += f'''
                                <td class="course-cell {room_class}">
                                    <div class="course-container">
                                        <div class="course-code">{cell['course_code']}</div>
                                        <div class="course-name">{cell['course_name']}</div>
                                        <div class="instructor">{cell['teacher']}</div>
                                        <div class="room">{cell['building']} {cell['room']}</div>
                                    </div>
                                </td>'''
                    else:
                        html += '''<td class="empty-cell"></td>'''
                
                html += '''
                            </tr>'''
                
            html += '''
                        </tbody>
                    </table>
                    
                    <div class="legend">
                        <h3>Légende des Cours</h3>
                        <div class="legend-items">'''
            
            # Add course legend
            for course in self.all_courses[class_id]:
                html += f'''
                            <div class="legend-item">
                                <span class="legend-code">{course['code']}</span>: {course['name']}
                            </div>'''
                
            html += '''
                        </div>
                    </div>
                </div>'''
            
        # Add JavaScript for navigation and filtering
        html += '''
                <div class="footer">
                    © 2025 Département d\'Informatique - Tous droits réservés
                </div>
            </div>
            
            <script>
                // Show the first timetable by default
                document.addEventListener(\'DOMContentLoaded\', function() {
                    const firstButton = document.querySelector(\'.nav-button\');
                    const firstTimetable = document.querySelector(\'.timetable-container\');
                    
                    if (firstButton && firstTimetable) {
                        firstButton.classList.add(\'active\');
                        firstTimetable.classList.add(\'active\');
                    }
                });
                
                // Function to show the selected timetable
                function showTimetable(id) {
                    // Hide all timetables
                    const timetables = document.querySelectorAll(\'.timetable-container\');
                    timetables.forEach(timetable => {
                        timetable.classList.remove(\'active\');
                    });
                    
                    // Remove active class from all buttons
                    const buttons = document.querySelectorAll(\'.nav-button\');
                    buttons.forEach(button => {
                        button.classList.remove(\'active\');
                    });
                    
                    // Show the selected timetable
                    const selectedTimetable = document.getElementById(id);
                    if (selectedTimetable) {
                        selectedTimetable.classList.add(\'active\');
                    }
                    
                    // Add active class to the clicked button
                    const buttonSelector = `.nav-button[onclick="showTimetable(\'${id}\')"]`;
                    const selectedButton = document.querySelector(buttonSelector);
                    if (selectedButton) {
                        selectedButton.classList.add(\'active\');
                    }
                    
                    // Reapply any active filters
                    const activeFilter = document.querySelector(\'.filter-option.active\');
                    if (activeFilter) {
                        const filterType = activeFilter.getAttribute(\'onclick\').match(/\'([^\']+)\'/)[1];
                        applyFilter(filterType);
                    }
                }
                
                // Function to filter timetables
                function filterTimetables(filterType) {
                    // Remove active class from all filter options
                    document.querySelectorAll(\'.filter-option\').forEach(option => {
                        option.classList.remove(\'active\');
                    });
                    
                    // Add active class to clicked filter option
                    document.querySelector(`.filter-option[onclick="filterTimetables(\'${filterType}\')"]`).classList.add(\'active\');
                    
                    // Apply the filter
                    applyFilter(filterType);
                }
                
                // Apply the selected filter
                function applyFilter(filterType) {
                    // Get the active timetable
                    const activeTimetable = document.querySelector(\'.timetable-container.active\');
                    if (!activeTimetable) return;
                    
                    // Show all cells initially
                    activeTimetable.querySelectorAll(\'.course-cell\').forEach(cell => {
                        cell.style.display = \'\';
                    });
                    
                    // Apply filter based on type
                    switch(filterType) {
                        case \'morning\':
                            // Hide non-morning cells
                            activeTimetable.querySelectorAll(\'tr:not(.morning-row) .course-cell\').forEach(cell => {
                                cell.style.opacity = \'0.3\';
                            });
                            break;
                        case \'afternoon\':
                            // Hide non-afternoon cells
                            activeTimetable.querySelectorAll(\'tr:not(.afternoon-row) .course-cell\').forEach(cell => {
                                cell.style.opacity = \'0.3\';
                            });
                            break;
                        case \'amphi\':
                            // Hide non-amphi cells
                            activeTimetable.querySelectorAll(\'.course-cell:not(.amphi-cell)\').forEach(cell => {
                                cell.style.opacity = \'0.3\';
                            });
                            break;
                        case \'tdtp\':
                            // Hide non-tdtp cells
                            activeTimetable.querySelectorAll(\'.course-cell:not(.tdtp-cell)\').forEach(cell => {
                                cell.style.opacity = \'0.3\';
                            });
                            break;
                        default:
                            // Show all cells (no filter)
                            activeTimetable.querySelectorAll(\'.course-cell\').forEach(cell => {
                                cell.style.opacity = \'1\';
                            });
                    }
                }
            </script>
        </body>
        </html>'''
        
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
        
        # Calculate stats for the timetable
        total_courses = 0
        morning_courses = 0
        rooms_used = set()
        
        for class_id in generator.classes:
            for day_idx in range(len(generator.days)):
                for period_idx in range(len(generator.periods)):
                    cell = generator.timetable[class_id][day_idx][period_idx]
                    if cell:
                        total_courses += 1
                        rooms_used.add(cell['room'])
                        if period_idx < 2:  # Morning periods (0-1)
                            morning_courses += 1
        
        # Calculate percentages
        if total_courses > 0:
            morning_percentage = int((morning_courses / total_courses) * 100)
        else:
            morning_percentage = 0
            
        # Calculate occupancy rate
        total_slots = len(generator.classes) * len(generator.days) * len(generator.periods)
        if total_slots > 0:
            occupancy_rate = int((total_courses / total_slots) * 100)
        else:
            occupancy_rate = 0
        
        print(f"Stats: {total_courses} courses, {len(rooms_used)} rooms used, {morning_percentage}% in morning, {occupancy_rate}% occupancy rate")
        
        # Update the HTML with actual stats
        combined_html = combined_html.replace('"TOTAL_COURSES"', str(total_courses))
        combined_html = combined_html.replace('"ROOMS_USED"', str(len(rooms_used)))
        combined_html = combined_html.replace('"TOTAL_ROOMS"', str(len(generator.rooms)))
        combined_html = combined_html.replace('"OCCUPANCY_RATE"', str(occupancy_rate))
        combined_html = combined_html.replace('"MORNING_PERCENTAGE"', str(morning_percentage))

        
        # Save combined HTML timetable
        with open("all_timetables.html", 'w', encoding='utf-8') as f:
            f.write(combined_html)
        print("Saved all_timetables.html")
        
        print("All timetables generated successfully!")
    else:
        print("Failed to find a feasible solution. Try relaxing some constraints.")

if __name__ == "__main__":
    main()
    
    