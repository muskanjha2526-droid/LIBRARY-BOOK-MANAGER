import json
import os
from datetime import date, timedelta

# ---------- DATA STORAGE ----------

FILE_NAME = "library_data.json"
FINE_PER_DAY = 5
TOTAL_SEATS = 20

books = {}
history = []
active_issues = []
waiting_list = {}
seat_bookings = {i: None for i in range(1, TOTAL_SEATS + 1)}


def load_records():
    global books, history, active_issues, waiting_list, seat_bookings

    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                data = json.load(file)

            books = data.get("books", {})
            history = data.get("history", [])
            active_issues = data.get("active_issues", [])
            waiting_list = data.get("waiting_list", {})
            saved_seats = data.get("seat_bookings", {})

            seat_bookings = {
                i: saved_seats.get(str(i))
                for i in range(1, TOTAL_SEATS + 1)
            }

        except (json.JSONDecodeError, OSError):
            print("Could not load saved records. Starting fresh.")


def save_records():
    data = {
        "books": books,
        "history": history,
        "active_issues": active_issues,
        "waiting_list": waiting_list,
        "seat_bookings": seat_bookings
    }

    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

    print("Records saved successfully!")


# ---------- 1. ADD BOOK ----------

def add_book():
    book_id = input("Enter Book ID: ")

    if book_id in books:
        print("Book ID already exists!")
        return

    title = input("Enter book name: ")
    author = input("Enter author name: ")
    category = input("Enter category: ")
    shelf = input("Enter shelf number: ")

    try:
        quantity = int(input("Enter number of copies: "))
        if quantity <= 0:
            print("Quantity must be positive.")
            return
    except ValueError:
        print("Enter a valid quantity.")
        return

    books[book_id] = {
        "title": title,
        "author": author,
        "category": category,
        "shelf": shelf,
        "total": quantity,
        "available": quantity,
        "reserved_by": None
    }

    print("Book added successfully!")


# ---------- 2. VIEW ALL BOOKS ----------

def view_books():
    if not books:
        print("No books available.")
        return

    for book_id, book in books.items():
        print("\nBook ID:", book_id)
        print("Name:", book["title"])
        print("Author:", book["author"])
        print("Category:", book["category"])
        print("Shelf:", book["shelf"])
        print("Available copies:", book["available"])
        print("Total copies:", book["total"])


# ---------- 3. SEARCH BOOK ----------

def search_book():
    name = input("Enter book name to search: ").lower()

    found = False

    for book_id, book in books.items():
        if name in book["title"].lower():
            print("\nBook ID:", book_id)
            print("Name:", book["title"])
            print("Author:", book["author"])
            print("Available:", book["available"])
            found = True

    if not found:
        print("Book not found.")


# ---------- 4. BORROW BOOK ----------

def borrow_book():
    book_id = input("Enter Book ID: ")
    student = input("Enter student name: ")

    if book_id not in books:
        print("Book does not exist.")
        return

    book = books[book_id]

    if any(x["student"] == student and x["book_id"] == book_id
           for x in active_issues):
        print("You have already borrowed this book.")
        return

    if book["available"] <= 0:
        print("Book is not available.")
        print("Please join the waiting list.")
        return

    if book["reserved_by"] and book["reserved_by"] != student:
        print("This book is reserved by another student.")
        return

    book["available"] -= 1
    book["reserved_by"] = None

    issue_date = date.today()
    due_date = issue_date + timedelta(days=14)

    issue = {
        "student": student,
        "book_id": book_id,
        "book_name": book["title"],
        "issue_date": str(issue_date),
        "due_date": str(due_date)
    }

    active_issues.append(issue)
    history.append({
        **issue,
        "return_date": None,
        "fine": 0
    })

    print("Book borrowed successfully!")
    print("Issue date:", issue_date)
    print("Return before:", due_date)


# ---------- 5. RETURN BOOK ----------

def return_book():
    book_id = input("Enter Book ID: ")
    student = input("Enter student name: ")

    for issue in active_issues:
        if issue["book_id"] == book_id and issue["student"] == student:

            return_date = date.today()
            due_date = date.fromisoformat(issue["due_date"])

            late_days = max(0, (return_date - due_date).days)
            fine = late_days * FINE_PER_DAY

            books[book_id]["available"] += 1

            for record in reversed(history):
                if (record["book_id"] == book_id
                        and record["student"] == student
                        and record["return_date"] is None):
                    record["return_date"] = str(return_date)
                    record["fine"] = fine
                    break

            active_issues.remove(issue)

            print("Book returned successfully!")
            print("Late days:", late_days)
            print("Fine: Rs.", fine)

            if waiting_list.get(book_id):
                next_student = waiting_list[book_id].pop(0)
                books[book_id]["reserved_by"] = next_student
                print("Book reserved for next student:", next_student)

            return

    print("No matching borrowed book found.")


# ---------- 6. RESERVE BOOK ----------

def reserve_book():
    book_id = input("Enter Book ID: ")
    student = input("Enter student name: ")

    if book_id not in books:
        print("Book not found.")
        return

    book = books[book_id]

    if book["available"] <= 0:
        print("Book is currently unavailable.")
        print("Use option 12 to join the waiting list.")
        return

    if book["reserved_by"]:
        print("Book is already reserved.")
        return

    book["reserved_by"] = student
    print("Book reserved successfully for", student)


# ---------- 7. FIND SHELF LOCATION ----------

def find_shelf():
    book_id = input("Enter Book ID: ")

    if book_id in books:
        print("Book:", books[book_id]["title"])
        print("Shelf Number:", books[book_id]["shelf"])
    else:
        print("Book not found.")


# ---------- 8. CHECK SEAT AVAILABILITY ----------

def check_seats():
    available = 0
    occupied = 0

    print("\n----- STUDY SEATS -----")

    for seat, student in seat_bookings.items():
        if student is None:
            print("Seat", seat, "- Available")
            available += 1
        else:
            print("Seat", seat, "- Booked by", student)
            occupied += 1

    print("\nAvailable seats:", available)
    print("Occupied seats:", occupied)


# ---------- 9. BOOK A STUDY SEAT ----------

def book_seat():
    try:
        seat = int(input("Enter seat number (1-20): "))
    except ValueError:
        print("Enter a valid seat number.")
        return

    if seat not in seat_bookings:
        print("Invalid seat number.")
        return

    if seat_bookings[seat] is not None:
        print("This seat is already booked.")
        return

    student = input("Enter student name: ")
    seat_bookings[seat] = student

    print("Seat", seat, "booked successfully!")


# ---------- 10. CALCULATE LATE FINE ----------

def calculate_fine():
    student = input("Enter student name: ")

    found = False

    for issue in active_issues:
        if issue["student"] == student:
            due = date.fromisoformat(issue["due_date"])
            late_days = max(0, (date.today() - due).days)
            fine = late_days * FINE_PER_DAY

            print("\nBook:", issue["book_name"])
            print("Due date:", issue["due_date"])
            print("Late days:", late_days)
            print("Fine: Rs.", fine)

            found = True

    if not found:
        print("No active borrowed books found for this student.")


# ---------- 11. BORROWING HISTORY ----------

def borrowing_history():
    student = input("Enter student name: ").lower()

    found = False

    for record in history:
        if record["student"].lower() == student:
            print("\nBook:", record["book_name"])
            print("Issue date:", record["issue_date"])
            print("Due date:", record["due_date"])
            print("Return date:", record["return_date"] or "Not returned")
            print("Fine: Rs.", record["fine"])
            found = True

    if not found:
        print("No borrowing history found.")


# ---------- 12. JOIN WAITING LIST ----------

def join_waiting_list():
    book_id = input("Enter Book ID: ")
    student = input("Enter student name: ")

    if book_id not in books:
        print("Book not found.")
        return

    if books[book_id]["available"] > 0:
        print("Book is currently available. You can borrow it.")
        return

    if book_id not in waiting_list:
        waiting_list[book_id] = []

    if student in waiting_list[book_id]:
        print("You are already in the waiting list.")
        return

    waiting_list[book_id].append(student)

    print("Added to waiting list successfully!")
    print("Your position:", len(waiting_list[book_id]))


# ---------- 13. SEARCH BY CATEGORY ----------

def search_category():
    category = input("Enter category: ").lower()

    found = False

    for book_id, book in books.items():
        if book["category"].lower() == category:
            print("\nBook ID:", book_id)
            print("Name:", book["title"])
            print("Author:", book["author"])
            print("Available:", book["available"])
            found = True

    if not found:
        print("No books found in this category.")


# ---------- 14. RECOMMEND A BOOK ----------

def recommend_book():
    category = input("Enter your favourite category: ").lower()

    matches = []

    for book_id, book in books.items():
        if book["category"].lower() == category:
            if book["available"] > 0:
                matches.append(book)

    if matches:
        print("\nRecommended books for you:")

        for book in matches:
            print("-", book["title"], "by", book["author"])
    else:
        print("No available books in this category.")


# ---------- 15. LIBRARY SUMMARY ----------

def library_summary():
    total_books = sum(b["total"] for b in books.values())
    available = sum(b["available"] for b in books.values())
    borrowed = total_books - available

    print("\n----- LIBRARY SUMMARY -----")
    print("Different book titles:", len(books))
    print("Total book copies:", total_books)
    print("Available copies:", available)
    print("Borrowed copies:", borrowed)
    print("Active issues:", len(active_issues))
    print("Total students in waiting lists:",
          sum(len(q) for q in waiting_list.values()))


# ---------- MAIN MENU ----------

load_records()

while True:

    print("\n===== LIBRARY BOOK MANAGER =====")
    print("1. Add Book")
    print("2. View All Books")
    print("3. Search Book")
    print("4. Borrow Book")
    print("5. Return Book")
    print("6. Reserve Book")
    print("7. Find Book Shelf Location")
    print("8. Check Study Seat Availability")
    print("9. Book a Study Seat")
    print("10. Calculate Late Fine")
    print("11. View Borrowing History")
    print("12. Join Book Waiting List")
    print("13. Search by Category")
    print("14. Recommend a Book")
    print("15. Library Summary")
    print("16. Save Records")
    print("17. Exit")

    choice = input("\nEnter your choice (1-17): ")

    if choice == "1":
        add_book()
    elif choice == "2":
        view_books()
    elif choice == "3":
        search_book()
    elif choice == "4":
        borrow_book()
    elif choice == "5":
        return_book()
    elif choice == "6":
        reserve_book()
    elif choice == "7":
        find_shelf()
    elif choice == "8":
        check_seats()
    elif choice == "9":
        book_seat()
    elif choice == "10":
        calculate_fine()
    elif choice == "11":
        borrowing_history()
    elif choice == "12":
        join_waiting_list()
    elif choice == "13":
        search_category()
    elif choice == "14":
        recommend_book()
    elif choice == "15":
        library_summary()
    elif choice == "16":
        save_records()
    elif choice == "17":
        save_records()
        print("Thank you for using Library Book Manager!")
        break
    else:
        print("Invalid choice! Please enter 1 to 17.")
