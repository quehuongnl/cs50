#

import csv

from cs50 import SQL

def create_students(name, students):
    students.append({"student_name": name})


def create_houses(house, head, houses):
    count = 0
    for h in houses:
        if h["house"] == house:
            count +=1
    if count == 0:
        houses.append({"house": house, "head": head})


def create_relationships(name, house, relationships):
    relationships.append({"student_name": name, "house": house})


# Open database
db = SQL("sqlite:///roster.db")

students = []
houses = []
relationships = []

# Read csv
with open("students.csv","r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        id = int(row["id"])
        name = row["student_name"]
        house = row["house"]
        head = row["head"]

        create_students(name, students)
        create_houses(house, head, houses)
        create_relationships(name, house, relationships)

for s in students:
    db.execute("INSERT INTO new_students (student_name) VALUES (?)", s["student_name"])

for h in houses:
    db.execute("INSERT INTO houses (house, head) VALUES (?, ?)", h["house"], h["head"])

for rel in relationships:
    db.execute("INSERT INTO relationships (student_name, house) VALUES (?, ?)", rel["student_name"], rel["house"])
