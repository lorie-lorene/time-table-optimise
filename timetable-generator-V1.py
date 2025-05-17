"""
Timetable Generator using Google OR-Tools for Computer Science Department

Specifications:
1. No class can be scheduled in multiple classrooms with different courses/teachers at the same time
2. All courses for a class should be scheduled exactly once per week
3. A class should not be scheduled to take a course not in its curriculum
4. Maximize the number of schedules before noon (lower period weights have higher priority)

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
        
        # Constraint 2: All courses for a class should be scheduled exactly once per week
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
                
                # Ensure exactly one assignment is made
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
        
        # Objective: Maximize the number of schedules before noon (minimize the sum of period weights)
        objective_terms = []
        
        for var_key, var in self.assignment_vars.items():
            _, _, _, _, period_idx = var_key
            weight = self.period_weights[period_idx]
            objective_terms.append(weight * var)
        
        # Minimize the sum of weights
        self.model.Minimize(sum(objective_terms))
    
    def solve_model(self):
        # Create a solver and solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300  # Limit solving time to 5 minutes
        
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Solution found with status {status}")
            
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
    
    def generate_html_timetable(self, class_id):
        """Generate HTML for a specific class timetable"""
        
        if class_id not in self.timetable:
            return f"<p>No timetable found for {class_id}</p>"
            
        # Extract level and semester from class_id
        level, semester = class_id.split('-')[1], class_id.split('-')[2]
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emploi du Temps - Niveau {level} - Semestre {semester}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    color: #003366;
                    margin-bottom: 5px;
                }}
                .header h2 {{
                    color: #005599;
                    margin-top: 0;
                    margin-bottom: 5px;
                }}
                .header h3 {{
                    color: #0077cc;
                    margin-top: 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                th {{
                    background-color: #003366;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .time-col {{
                    width: 15%;
                    background-color: #e6e6e6;
                    font-weight: bold;
                }}
                .course-name {{
                    font-weight: bold;
                    color: #003366;
                }}
                .instructor {{
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
                .room {{
                    font-size: 0.85em;
                    color: #666;
                    margin-top: 3px;
                }}
                .empty-cell {{
                    background-color: #f9f9f9;
                }}
                @media print {{
                    body {{
                        padding: 0;
                        font-size: 12px;
                    }}
                    table {{
                        page-break-inside: avoid;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Emploi du Temps - Niveau {level} - Semestre {semester}</h1>
                <h2>Département d'Informatique</h2>
                <h3>Année académique 2024-2025</h3>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th class="time-col">Horaire</th>
        """
        
        # Add day headers
        for day in self.days[:5]:  # Excluding Saturday
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
            for day_idx in range(5):  # Excluding Saturday
                cell = self.timetable[class_id][day_idx][period_idx]
                
                if cell:
                    html += f"""
                        <td>
                            <div class="course-name">{cell['course_code']}</div>
                            <div class="instructor">{cell['teacher']}</div>
                            <div class="room">{cell['building']} {cell['room']}</div>
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
            
            <div style="margin-top: 30px;">
                <h3 style="color: #003366; border-bottom: 1px solid #ddd; padding-bottom: 5px;">Légende des Cours</h3>
        """
        
        # Add course legend
        for course in self.all_courses[class_id]:
            html += f"""
                <div style="margin-bottom: 5px;">
                    <span style="font-weight: bold; color: #003366;">{course['code']}</span>: {course['name']}
                </div>
            """
            
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_all_timetables(self):
        """Generate HTML timetables for all classes"""
        
        html_timetables = {}
        
        for class_id in self.classes:
            html_timetables[class_id] = self.generate_html_timetable(class_id)
            
        return html_timetables
        
    def generate_combined_html_timetable(self):
        """Generate a single HTML file containing all timetables with navigation"""
        
        # Start HTML document
        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Emplois du Temps - Département d'Informatique</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .header h1 {
                    color: #003366;
                    margin-bottom: 5px;
                }
                .header h2 {
                    color: #005599;
                    margin-top: 0;
                    margin-bottom: 5px;
                }
                .header h3 {
                    color: #0077cc;
                    margin-top: 0;
                }
                .nav-container {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                }
                .nav-button {
                    padding: 10px 15px;
                    margin: 5px;
                    background-color: #003366;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                }
                .nav-button:hover {
                    background-color: #004a8f;
                }
                .nav-button.active {
                    background-color: #0077cc;
                }
                .timetable-container {
                    display: none;
                }
                .timetable-container.active {
                    display: block;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }
                th {
                    background-color: #003366;
                    color: white;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                .time-col {
                    width: 15%;
                    background-color: #e6e6e6;
                    font-weight: bold;
                }
                .course-name {
                    font-weight: bold;
                    color: #003366;
                }
                .instructor {
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .room {
                    font-size: 0.85em;
                    color: #666;
                    margin-top: 3px;
                }
                .empty-cell {
                    background-color: #f9f9f9;
                }
                .legend {
                    margin-top: 30px;
                }
                .legend h3 {
                    color: #003366;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                .legend-item {
                    margin-bottom: 5px;
                }
                .legend-code {
                    font-weight: bold;
                    color: #003366;
                }
                .print-button {
                    display: block;
                    margin: 20px auto;
                    padding: 10px 20px;
                    background-color: #003366;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .print-button:hover {
                    background-color: #004a8f;
                }
                @media print {
                    .nav-container, .print-button {
                        display: none;
                    }
                    .timetable-container {
                        display: block;
                        page-break-after: always;
                    }
                    body {
                        padding: 0;
                        font-size: 12px;
                    }
                    table {
                        page-break-inside: avoid;
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
                <h2>Niveau {level} - Semestre {semester}</h2>
                <table>
                    <thead>
                        <tr>
                            <th class="time-col">Horaire</th>
            """
            
            # Add day headers - INCLUDE ALL 6 DAYS
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
                
                # Add cells for each day - INCLUDE ALL 6 DAYS
                for day_idx in range(6):  # Including Saturday
                    cell = self.timetable[class_id][day_idx][period_idx]
                    
                    if cell:
                        html += f"""
                            <td>
                                <div class="course-name">{cell['course_code']}</div>
                                <div class="instructor">{cell['teacher']}</div>
                                <div class="room">{cell['building']} {cell['room']}</div>
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
            """
            
        # Add JavaScript for navigation
        html += """
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
