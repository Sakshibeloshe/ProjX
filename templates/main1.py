import pymysql
import getpass
from datetime import datetime

class MovieTicketBookingSystem:
    def _init_(self):
        self.connection = None
        self.current_user = None

    def connect_to_database(self):
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',  # Add your MySQL password here if set
                database='movie_booking',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to MySQL database successfully!")
            return True
        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def customer_login(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")

        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM customers WHERE email = %s AND password = %s"
                cursor.execute(sql, (email, password))
                user = cursor.fetchone()

                if user:
                    self.current_user = user
                    print(f"\nWelcome back, {user['name']}!")
                    return True
                else:
                    print("\nInvalid email or password.")
                    return False
        except pymysql.Error as e:
            print(f"Error during login: {e}")
            return False

    def customer_signup(self):
        print("\nCreate a new account:")
        name = input("Full name: ")
        email = input("Email: ")
        phone = input("Phone number: ")
        password = getpass.getpass("Password: ")

        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO customers (name, email, phone, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, email, phone, password))
                self.connection.commit()
                print("\nAccount created successfully! Please login.")
                return True
        except pymysql.Error as e:
            print(f"\nError creating account: {e}")
            return False

    def show_movies(self):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM movies WHERE is_active = TRUE ORDER BY title"
                cursor.execute(sql)
                movies = cursor.fetchall()

                print("\nCurrently Showing Movies:")
                print("-" * 60)
                for movie in movies:
                    print(f"{movie['movie_id']}. {movie['title']} ({movie['language']})")
                    print(f"   Genre: {movie['genre']} | Duration: {movie['duration_min']} mins")
                    print(f"   Rating: {movie['rating']}/5 | Released: {movie['release_date']}")
                    print("-" * 60)
        except pymysql.Error as e:
            print(f"Error fetching movies: {e}")

    def show_screenings(self, movie_id=None):
        try:
            with self.connection.cursor() as cursor:
                if movie_id:
                    sql = """
                    SELECT s.*, m.title, c.name as cinema_name
                    FROM screenings s
                    JOIN movies m ON s.movie_id = m.movie_id
                    JOIN cinemas c ON s.cinema_id = c.cinema_id
                    WHERE s.movie_id = %s AND s.start_time > NOW()
                    ORDER BY s.start_time
                    """
                    cursor.execute(sql, (movie_id,))
                else:
                    sql = """
                    SELECT s.*, m.title, c.name as cinema_name
                    FROM screenings s
                    JOIN movies m ON s.movie_id = m.movie_id
                    JOIN cinemas c ON s.cinema_id = c.cinema_id
                    WHERE s.start_time > NOW()
                    ORDER BY s.start_time
                    LIMIT 20
                    """
                    cursor.execute(sql)

                screenings = cursor.fetchall()

                if not screenings:
                    print("\nNo screenings available.")
                    return

                print("\nAvailable Screenings:")
                print("-" * 80)
                for screening in screenings:
                    print(f"{screening['screening_id']}. {screening['title']}")
                    print(f"   Cinema: {screening['cinema_name']} | Screen: {screening['screen_number']}")
                    print(f"   Time: {screening['start_time']} | Price: ₹{screening['price']}")
                    print(f"   Available seats: {screening['available_seats']}")
                    print("-" * 80)
        except pymysql.Error as e:
            print(f"Error fetching screenings: {e}")

    def book_ticket(self):
        if not self.current_user:
            print("\nPlease login first.")
            return

        self.show_movies()
        movie_id = input("\nEnter movie ID to see screenings (or press Enter to see all): ")
       
        if movie_id:
            self.show_screenings(int(movie_id))
        else:
            self.show_screenings()

        screening_id = input("\nEnter screening ID to book tickets: ")
        num_tickets = int(input("Number of tickets: "))

        try:
            with self.connection.cursor() as cursor:
                # Check available seats
                sql = "SELECT available_seats, price FROM screenings WHERE screening_id = %s"
                cursor.execute(sql, (screening_id,))
                screening = cursor.fetchone()

                if not screening:
                    print("Invalid screening ID.")
                    return

                if screening['available_seats'] < num_tickets:
                    print(f"Only {screening['available_seats']} seats available.")
                    return

                # Calculate total amount
                total_amount = screening['price'] * num_tickets

                # Create booking
                sql = """
                INSERT INTO bookings (customer_id, screening_id, num_tickets, total_amount)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (self.current_user['customer_id'], screening_id, num_tickets, total_amount))

                # Update available seats
                sql = "UPDATE screenings SET available_seats = available_seats - %s WHERE screening_id = %s"
                cursor.execute(sql, (num_tickets, screening_id))

                self.connection.commit()
                print(f"\nBooking successful! Total amount: ₹{total_amount:.2f}")

        except pymysql.Error as e:
            print(f"Error during booking: {e}")

    def show_my_bookings(self):
        if not self.current_user:
            print("\nPlease login first.")
            return

        try:
            with self.connection.cursor() as cursor:
                sql = """
                SELECT b.*, m.title, c.name as cinema_name, s.start_time
                FROM bookings b
                JOIN screenings s ON b.screening_id = s.screening_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN cinemas c ON s.cinema_id = c.cinema_id
                WHERE b.customer_id = %s
                ORDER BY b.booking_date DESC
                """
                cursor.execute(sql, (self.current_user['customer_id'],))
                bookings = cursor.fetchall()

                if not bookings:
                    print("\nYou have no bookings yet.")
                    return

                print("\nYour Bookings:")
                print("-" * 80)
                for booking in bookings:
                    print(f"Booking ID: {booking['booking_id']}")
                    print(f"Movie: {booking['title']} | Cinema: {booking['cinema_name']}")
                    print(f"Showtime: {booking['start_time']} | Tickets: {booking['num_tickets']}")
                    print(f"Amount: ₹{booking['total_amount']:.2f} | Status: {booking['payment_status']}")
                    print("-" * 80)
        except pymysql.Error as e:
            print(f"Error fetching bookings: {e}")

    def main_menu(self):
        while True:
            print("\nMovie Ticket Booking System")
            print("1. Login")
            print("2. Sign Up")
            print("3. View Movies")
            print("4. View Screenings")
            print("5. Book Tickets")
            print("6. My Bookings")
            print("7. Exit")

            choice = input("\nEnter your choice: ")

            if choice == '1':
                if self.customer_login():
                    continue
            elif choice == '2':
                self.customer_signup()
            elif choice == '3':
                self.show_movies()
            elif choice == '4':
                self.show_screenings()
            elif choice == '5':
                self.book_ticket()
            elif choice == '6':
                self.show_my_bookings()
            elif choice == '7':
                print("\nThank you for using our Movie Ticket Booking System!")
                break
            else:
                print("\nInvalid choice. Please try again.")

if _name_ == "_main_":
    system = MovieTicketBookingSystem()
    if system.connect_to_database():
        system.main_menu()
    if system.connection:
        system.connection.close()