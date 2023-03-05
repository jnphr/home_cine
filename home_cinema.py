"""
This program forms part of a home entertainment system,
making use of NLP and SQLite to interact with a database of movies.
"""

# To begin, import the relevant modules and libraries for the program.
import spacy

import sqlite3

import csv

import textwrap

# Use the advanced language model cf. spaCy.
nlp = spacy.load("en_core_web_md")

# Create a file to store the database, and a cursor item to interact with the same.
db = sqlite3.connect('movies.db')
cursor = db.cursor()

# Create the table and assign a primary key.
cursor.execute('''CREATE TABLE IF NOT EXISTS movies(
                    id VARCHAR(4) NOT NULL PRIMARY KEY, 
                    Title VARCHAR(225), 
                    Director VARCHAR(225), 
                    Year INT,
                    Description VARCHAR,
                    Genre VARCHAR(225),
                    Tags VARCHAR)
                ''')
db.commit()

# Populate the table with data stored in a .csv file.
with open("moviedb.csv") as file:
    data = csv.reader(file)
    cursor.executemany('''INSERT OR REPLACE INTO movies VALUES(?,?,?,?,?,?,?)''', data)
    db.commit()


# Create a class with data attributes for each movie object to be stored in the program.
# Create a display method relevant to this class.
class Movie:
    def __init__(self, title, director, year, description, genre, tags):
        self.title = title
        self.director = director
        self.year = year
        self.description = description
        self.genre = genre
        self.tags = tags

    def __str__(self):
        return f"{self.title} ({self.year})\nDirected by {self.director}"


# Define the functions that will make up the menu items of the program.
def search():
    search_by = input("Search: ").title()
    search_by = search_by.replace(" ", "%")
    search_by = f"%{search_by}%"
    cursor.execute('''SELECT * FROM movies WHERE Title LIKE ? OR Director LIKE ? OR Tags LIKE ?''',
                   (search_by, search_by, search_by,))
    entry = cursor.fetchall()
    if not entry:
        print("Your search returned 0 results.\n")
    else:
        print(f"Your search returned {len(entry)} result(s):")
        select(entry)


def play(movie):
    comparison = nlp(movie.tags)
    movie_score = {}
    cursor.execute('''SELECT * FROM movies WHERE Title != ?''', (movie.title,))
    entry = cursor.fetchall()
    for result in entry:
        similarity = nlp(result[6]).similarity(comparison)
        movie_score[result[1]] = [similarity, result[1], result[2], result[3], result[4], result[5], result[6]]
    sorted_movie_score = sorted(movie_score.items(), key=lambda x: x[1])
    recommended = sorted_movie_score[-3:]
    print()
    print(f"Did you enjoy {movie.title}? You might also like:")
    entry = []
    for result in recommended:
        entry.append(result[1])
    select_play(entry)


def browse():
    print("Press 1 to browse by genre, 2 to browse by director or 3 to browse new releases")
    entry = ""
    browse_by = int(input())
    if browse_by == 1:
        print("Browse by genre\n")
        cursor.execute('''SELECT * FROM movies ORDER BY Genre''')
        entry = cursor.fetchall()
    elif browse_by == 2:
        print("Browse by director\n")
        cursor.execute('''SELECT * FROM movies ORDER BY SUBSTR(Director, INSTR(Director, " "), LENGTH(Director))''')
        entry = cursor.fetchall()
    elif browse_by == 3:
        print("Browse new releases\n")
        cursor.execute('''SELECT * FROM movies ORDER BY Year DESC LIMIT 10''')
        entry = cursor.fetchall()
    if entry and browse_by != 2:
        select(entry)
    elif entry and browse_by == 2:
        select_director(entry)


def select(choice):
    while True:
        temp_list = []
        for count, result in enumerate(choice, 1):
            print(f"{count} {result[1]} ({result[3]})\n"
                  f"{result[5]}\n")
            temp_list.append(result)
        print("Enter movie number to view details or 0 to return to the main menu")
        selection = int(input())-1
        if selection in range(len(choice)):
            movie_data = temp_list[selection]
            movie = Movie(movie_data[1], movie_data[2], movie_data[3], movie_data[4], movie_data[5],
                          f"{movie_data[2]} {movie_data[4]} {movie_data[5]}")
            print(f"{movie}\n"
                  f"{textwrap.fill(movie.description)}\n")
            print("Press 1 to play movie, -1 to go back or 0 to return to the main menu")
            play_choice = int(input())
            if play_choice == 1:
                play(movie)
            elif play_choice == -1:
                continue
            elif play_choice == 0:
                break
            else:
                print("Error\n")
                break
        elif selection == -1:
            break
        else:
            print("Error\n")
            break


def select_director(choice):
    while True:
        temp_list = []
        for count, result in enumerate(choice, 1):
            print(f"{count} {result[1]} ({result[3]})\n"
                  f"{result[2]}\n")
            temp_list.append(result)
        print("Enter movie number to view details or 0 to return to the main menu")
        selection = int(input())-1
        if selection in range(len(choice)):
            movie_data = temp_list[selection]
            movie = Movie(movie_data[1], movie_data[2], movie_data[3], movie_data[4], movie_data[5],
                          f"{movie_data[2]} {movie_data[4]} {movie_data[5]}")
            print(f"{movie}\n"
                  f"{textwrap.fill(movie.description)}\n")
            print("Press 1 to play movie, -1 to go back or 0 to return to the main menu")
            play_choice = int(input())
            if play_choice == 1:
                play(movie)
            elif play_choice == -1:
                continue
            elif play_choice == 0:
                break
            else:
                print("Error\n")
                break
        elif selection == -1:
            break
        else:
            print("Error\n")
            break


def select_play(choice):
    while True:
        temp_list = []
        for count, result in enumerate(choice, 1):
            print(f"{count} {result[1]} ({result[3]})\n"
                  f"{result[5]}\n")
            temp_list.append(result)
        print("Enter movie number to view details or -1 to go back")
        selection = int(input())-1
        if selection in range(len(choice)):
            movie_data = temp_list[selection]
            movie = Movie(movie_data[1], movie_data[2], movie_data[3], movie_data[4], movie_data[5],
                          f"{movie_data[2]} {movie_data[4]} {movie_data[5]}")
            print(f"{movie}\n"
                  f"{textwrap.fill(movie.description)}\n")
            print("Press 1 to play movie or -1 to go back")
            play_choice = int(input())
            if play_choice == 1:
                play(movie)
            elif play_choice == -1:
                continue
            else:
                print("Error\n")
        elif selection == -2:
            break
        else:
            print("Error\n")
            continue


# Set up the program.
print("Home Cinema")
while True:
    try:
        menu = int(input("""Choose from the menu options below:
1. Browse movies
2. Search movies
0. Exit
"""))
        if menu == 1:
            browse()
        elif menu == 2:
            search()
        elif menu == 0:
            print("You have been logged out.")
            db.close()
            break
        else:
            print("Invalid menu selection.\n")
    except ValueError:
        print("Invalid menu selection.\n")
    except (sqlite3.ProgrammingError, sqlite3.DatabaseError):
        print("Unable to load movie catalogue.\n")
