#

import csv

from cs50 import SQL

# Open database
db = SQL("sqlite:///roster.db")

# Read csv
with open("students.csv","r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        id = int(row["id"])
        name = row["student_name"]
        house = row["house"]
        head = row["head"]

        db.execute("INSERT INTO new_students (student_name) VALUES (?)", name)
        db.execute("INSERT INTO houses (house, head) VALUES (?, ?)", house, head)
        db.execute("INSERT INTO relationships (student_name, house) VALUES (?, ?)", name, house)
