from crypt import methods
import email
from re import search, template
import re
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_session import Session
import sqlite3
from datetime import datetime, timedelta
#from flask_mysqldb import MySQL
#import MySQLdb.cursors

logged = False

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = 'hWmZq4t7w!z%C*F-JaNdRgUjXn2r5u8x'


def get_db_connection():
    """
    Connect to database.
    """
    conn = sqlite3.connect('mydb.sdb')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def direct():
    """
    This def directs immediately to the Login page
    """
    global logged
    logged = False
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This def is used for the Librarian to log into the Library. 
    The librarian has one login that will only let them in via sysop - system operator. 
    This will prevent others from logging in and lending false books.
    """

    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        
        #AB cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password,))
        account = cur.fetchone()
        #AB cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password,))
        # Fetch one record and return result
        #AB account = cursor.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['username']
            session['password'] = account['password']
            # Redirect to home page
            conn = get_db_connection()
            title = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
            conn.close()
            global logged
            logged = True
            return redirect(url_for('library', info = title))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)





@app.route('/search', methods=['GET','POST'])
def main():
    """
    This def is not being used in the website, i used it in prior tests and found out that i dont need it but havent gotten round to removing it
    """

    if request.method == "POST":
        author = request.form['author']
        title = request.form['title']
        
        if not author:
            flash('Author is REQUIRED')
        elif not title:
            flash('Title is REQUIRED')
        else:
            conn = get_db_connection()
            search = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ?',(title,author)).fetchall()
            conn.close()
            return render_template('two.html', info = search)
    return render_template('main.html')

@app.route('/library', methods=['GET','POST'])
def library():
    """
    This is an important def because this is what loads the library page with all the books
    """
    if logged == True:
        if request.method == 'POST':
            conn = get_db_connection()
            title = conn.execute('SELECT * FROM books ORDER BY author').fetchall()
            conn.close()
            return render_template('library.html', info = title)
        elif request.method == 'GET':
            conn = get_db_connection()
            title = conn.execute('SELECT * FROM books ORDER BY author').fetchall()
            conn.close()
            return render_template('library.html', info = title)
    else:
        return redirect(url_for('direct'))
@app.route('/addbook',methods=['GET','POST'])
def addbook():
    """
    This def is used in the website to add a book into the database.
    First it will check if the book is in the database and if it is it will not insert.
    If the book isnt in the database then it will insert it into it
    """
    if request.method == 'POST':
        author = request.form['author1']
        title = request.form['title1']
        
        if not author:
            flash('Author is REQUIRED')
        elif not title:
            flash('Title is REQUIRED')
        else:
            conn = get_db_connection()
            book = conn.execute('SELECT * FROM books WHERE author LIKE ? AND title LIKE ?',(author, title)).fetchall()
            rows = len(book)
            conn.commit()
            conn.close()

            if rows == 0:
                conn = get_db_connection()
                conn.execute('INSERT INTO books (title, author) VALUES (?, ?)',(title, author))
                conn.commit()
                conn.close()
                return render_template('succesfullyadded.html')
            else:
                return render_template('alreadyinlibrary.html')
    return render_template('succesfullyadded.html')
    
@app.route('/borrowbook/<int:idbooks>', methods=['GET','POST'])
def borrowbook(idbooks):
    """
    This def is used 
    """
    if request.method == 'GET':
        #connecting to the db
        conn = get_db_connection()
        ifbooks = conn.execute('SELECT * FROM borrowed_books WHERE books_idbooks1=?', (idbooks,)).fetchall()
        row = len(ifbooks)
        if row == 0:
            borrowers = conn.execute('SELECT * FROM borrowers').fetchall()
            title = conn.execute('SELECT * FROM books WHERE idbooks=?',(idbooks,)).fetchall()
            print(len(title))
            conn.close()
            return render_template('borrower.html', title=title, borrowers=borrowers, idbooks=idbooks)
        else:
            return render_template('bookisborrowed.html')

@app.route('/borrowbook/borrowers2/<idbooks>', methods=['GET','POST'])
def borrowers2(idbooks,idborrowers):
    """
    This def was going to be used for borrowing books but it was getting too messy so I wrote a new cleaner def below
    Therefore this def is not being used
    I originally had it taking information from the borrowers user and using that but i had trouble getting in that information.
    """
    conn = get_db_connection()
    due_date_set = timedelta(weeks = 2)
    due_date = datetime.utcnow() + due_date_set
    book = conn.execute('SELECT * FROM books WHERE idbooks=?', (idbooks, )).fetchall()
    borrowers = conn.execute('SELECT * FROM borrowers WHERE idborrowers=?', (idborrowers,)).fetchall()
    execute = conn.execute('INSERT INTO borrowed_books(books_idbooks1, borrowed_date, due_date) VALUES (?, CURRENT_TIMESTAMP, ?)', (idbooks,due_date)).fetchall()
    print(borrowers)
    
    #SELECT idbooks FROM books WHERE idbooks=?
    #INSERT INTO borrowed_books SELECT * FROM books WHERE title=?'(title)).fetchall()
    #conn.execute('INSERT INTO borrowed_books (borrowed_date) SELECT idbooks FROM books WHERE ')
    conn.close()
    return render_template('successful.html', book=book, execute=execute, idbooks=idbooks)

#@app.route('/successful/<idbooks>', methods=['GET','POST'])
@app.route('/successful/', methods=['GET','POST'])
def borrowers3():   ##idbooks
    """
    This is the new and improved def for the borrow_book
    This def takes information of the borrower and the idbook and inserts it into the database only if the book isnt already borrowed.
    It also tells when the book is due (always two weeks)
    """
    idbooks = request.form['idbooks']

    form_fname = request.form['fname']
    form_lname = request.form['lname']
    form_phone = request.form.get('phonenum')
    form_address1 = request.form['address1']
    form_city = request.form['city']
    form_email = request.form['email']


    if not form_fname:
        flash('First Name is Required!')
    elif not form_lname:
        flash('Last Name is Required!')
    elif not form_phone:
        flash('Phone Number is Required!')
    elif not form_address1:
        flash('Address is Required!')
    elif not form_city:
        flash('City is Required!')
    elif not form_email:
        flash('Email is Required!')

    else:
        conn = get_db_connection()
        borrower = conn.execute('SELECT * FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchall()
        rows = len(borrower)
        conn.commit()
        conn.close()

        if rows == 0:
            #insert users details into the database
            #return to next page
            form_fname = request.form['fname']
            form_lname = request.form['lname']
            form_phone = request.form.get('phonenum')
            form_address1 = request.form['address1']
            form_city = request.form['city']
            form_email = request.form['email']


            if not form_fname:
                flash('First Name is Required!')
            elif not form_lname:
                flash('Last Name is Required!')
            elif not form_phone:
                flash('Phone Number is Required!')
            elif not form_address1:
                flash('Address is Required!')
            elif not form_city:
                flash('City is Required!')
            elif not form_email:
                flash('Email is Required!')
            

            else:
                conn = get_db_connection()
                conn.execute('INSERT INTO borrowers (fname, lname, phone, address1, city, email) VALUES (?, ?, ?, ?, ?, ?)',(form_fname, form_lname, form_phone, form_address1, form_city, form_email))
                borrower = conn.execute('SELECT * FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchall()
                conn.commit()
                conn = get_db_connection()
                #borrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchall()
                #Selecting the profile of the borrower from the table 
                idborrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchone()
                conn.commit()
                if type(idborrowers) is int:
                    ifbooks = conn.execute('SELECT * FROM borrowed_books WHERE books_idbooks1=?', (idbooks,)).fetchall()
                    row = len(ifbooks)
                    if row == 0:
                        #setting the due date with python math algorithms
                        due_date_set = timedelta(days = 14)
                        due_date = datetime.utcnow() + due_date_set
                        borrowed_date = datetime.utcnow()
                        #date = conn.execute('SELECT CURRENT_DATE')
                        book = conn.execute('SELECT * FROM books WHERE idbooks=?', (idbooks,)).fetchall()
                        conn.commit()
                        #executing it all
                        insert = conn.execute('INSERT INTO borrowed_books(books_idbooks1, borrowed_date, due_date, borrowers_idborrowers1) VALUES (?, ?, ?, ?)', (idbooks, borrowed_date, due_date, idborrowers)).fetchall()
                        #no2execute = conn.execute('INSERT INTO ')
                        conn.commit()
                        conn.close()
                    else:
                        return render_template('bookisborrowed.html')
                else:
                    ifbooks = conn.execute('SELECT * FROM borrowed_books WHERE books_idbooks1=?', (idbooks,)).fetchall()
                    row = len(ifbooks)
                    if row == 0:

                        idborrowers2 = idborrowers[0]
                        idborrowersint = int(idborrowers2)
                        #setting the due date with python math algorithms
                        due_date_set = timedelta(days = 14)
                        due_date = datetime.utcnow() + due_date_set
                        borrowed_date = datetime.utcnow()
                        #date = conn.execute('SELECT CURRENT_DATE')
                        book = conn.execute('SELECT * FROM books WHERE idbooks=?', (idbooks,)).fetchall()
                        conn.commit()
                        #executing it all
                        insert = conn.execute('INSERT INTO borrowed_books(books_idbooks1, borrowed_date, due_date, borrowers_idborrowers1) VALUES (?, ?, ?, ?)', (idbooks, borrowed_date, due_date, idborrowersint)).fetchall()
                        #no2execute = conn.execute('INSERT INTO ')
                        conn.commit()
                        conn.close()
                    else:
                        return render_template('bookisborrowed.html')
                
        else:
            conn = get_db_connection()
            #borrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchall()
            #Selecting the profile of the borrower from the table 
            idborrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchone()
            conn.commit()
            if type(idborrowers) is int:
                ifbooks = conn.execute('SELECT * FROM borrowed_books WHERE books_idbooks1=?', (idbooks,)).fetchall()
                row = len(ifbooks)
                if row == 0:
                    #setting the due date with python math algorithms
                    due_date_set = timedelta(days = 14)
                    due_date = datetime.utcnow() + due_date_set
                    borrowed_date = datetime.utcnow()
                    #date = conn.execute('SELECT CURRENT_DATE')
                    book = conn.execute('SELECT * FROM books WHERE idbooks=?', (idbooks,)).fetchall()
                    conn.commit()
                    #executing it all
                    insert = conn.execute('INSERT INTO borrowed_books(books_idbooks1, borrowed_date, due_date, borrowers_idborrowers1) VALUES (?, ?, ?, ?)', (idbooks, borrowed_date, due_date, idborrowers)).fetchall()
                    #no2execute = conn.execute('INSERT INTO ')
                    conn.commit()
                    conn.close()
                else:
                    return render_template('bookisborrowed.html')
            else:
                ifbooks = conn.execute('SELECT * FROM borrowed_books WHERE books_idbooks1=?', (idbooks,)).fetchall()
                row = len(ifbooks)
                if row == 0:
                    idborrowers2 = idborrowers[0]
                    idborrowersint = int(idborrowers2)
                    #setting the due date with python math algorithms
                    due_date_set = timedelta(days = 14)
                    due_date = datetime.utcnow() + due_date_set
                    borrowed_date = datetime.utcnow()
                    #date = conn.execute('SELECT CURRENT_DATE')
                    book = conn.execute('SELECT * FROM books WHERE idbooks=?', (idbooks,)).fetchall()
                    conn.commit()
                    #executing it all
                    insert = conn.execute('INSERT INTO borrowed_books(books_idbooks1, borrowed_date, due_date, borrowers_idborrowers1) VALUES (?, ?, ?, ?)', (idbooks, borrowed_date, due_date, idborrowersint)).fetchall()
                    #no2execute = conn.execute('INSERT INTO ')
                    conn.commit()
                    conn.close()
                else:
                    return render_template('bookisborrowed.html')
    return render_template('successful.html')

#@app.route('/returnbooks', methods=['GET','POST'])
#def aboutme():
    return render_template('aboutme.html')


@app.route('/aboutme', methods=['GET','POST'])
def aboutme():
    """
    This def redirects to the page where my information is held
    """
    if logged == False:
        return redirect(url_for('direct'))
    elif logged == True:
        return render_template('aboutme.html')
    else:
        return redirect(url_for('weirdo'))


#@app.route('/createaccount', methods=['GET','POST'])
#def createaccount():
    return render_template('createaccount.html')

@app.route('/weirdo', methods=['GET','POST'])
def weirdo():
    """
    This def will redirect the librarian to an error page if an error occurs
    """
    return render_template('error.html')

@app.route('/borrowers', methods=['GET','POST'])
def borrowers():
    """
    This def inserts the borrower information that is put into the form into the database.
    """
    if logged == True:
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form.get('phonenum')
        address1 = request.form['address1']
        city = request.form['city']
        email = request.form['email']

        if not fname:
            flash('First Name is Required!')
        elif not lname:
            flash('Last Name is Required!')
        elif not phone:
            flash('Phone Number is Required!')
        elif not address1:
            flash('Address is Required!')
        elif not city:
            flash('City is Required!')
        elif not email:
            flash('Email is Required!')
        else:
            conn = get_db_connection()
            search = conn.execute('SELECT * FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(fname, lname)).fetchall()
            rows = len(search)

            if rows > 0:
                #insert users details into the database
                #return to next page
                return render_template('aboutme.html')
            else:
                fname = request.form['fname']
                lname = request.form['lname']
                phone = request.form.get('phonenum')
                address1 = request.form['address1']
                city = request.form['city']
                email = request.form['email']


                if not fname:
                    flash('First Name is Required!')
                elif not lname:
                    flash('Last Name is Required!')
                elif not phone:
                    flash('Phone Number is Required!')
                elif not address1:
                    flash('Address is Required!')
                elif not city:
                    flash('City is Required!')
                elif not email:
                    flash('Email is Required!')

                else:
                    conn = get_db_connection()
                    conn.execute('INSERT INTO borrowers (fname, lname, phone, address1, city, email) VALUES (?, ?, ?, ?, ?, ?)',(fname, lname, phone, address1, city, email))
                    conn.commit()
                    conn.close()

                return render_template('main.html')
    else:
        return redirect(url_for('direct'))


@app.route('/loan', methods=['GET','POST'])
def loan():
    """
    This def was used for testing. If i nneded to see if something went through all the code and worked,
    I would do a 'return redirect({{url_for['loan']}})'.
    """
    return render_template('spare.html')

@app.route('/insertbook',methods=['GET','POST'])
def insertbook():
    """
    This def is used alongside a button to redirect the user to a new page.
    """
    if logged == True:
        return render_template('insertbook.html')
    else:
        return redirect(url_for('direct'))

@app.route('/borrowerspage',methods=['GET','POST'])
def borrowerspage():
    """
    This def Selects all the data from inside the borrowers table 
    and displays it onto the borrowers page
    """
    if logged == True:
        conn = get_db_connection()
        borrowers = conn.execute('SELECT * FROM borrowers').fetchall()
        conn.close()
        return render_template('borrowerspage.html', borrowers = borrowers)
    else:
        return redirect(url_for('direct'))

@app.route('/lendedbooks',methods=['GET','POST'])
def lendedbooks():
    """
    This was by far the hardest def to do even though it is small.
    This uses a join to show the names of the book being borrowed and the name of the person borrowing it,
    even though the borrowed_books table only includes the id's of the book and borrower.
    """
    if logged == True:
        conn = get_db_connection()
        books_borrowed = conn.execute('SELECT borrowed_books.idloan, books.author, books.title, borrowed_books.borrowers_idborrowers1, books.idbooks, borrowers.fname, borrowers.lname, borrowed_books.borrowed_date, borrowed_books.due_date FROM borrowed_books JOIN books ON borrowed_books.books_idbooks1=books.idbooks JOIN borrowers ON borrowed_books.borrowers_idborrowers1=borrowers.idborrowers',).fetchall()
        conn.close()
        return render_template('lendedbooks.html', books_borrowed = books_borrowed)
    else:
        return redirect(url_for('direct'))

@app.route('/removed/<int:idbooks>', methods=['GET','POST'])
def removebook(idbooks):
    """
    This def is used for returning a book to the library. 
    This takes the id of the book thats being borrowed and deletes it from the borrowed_books table.
    """
    idbooksint = int(idbooks) 
    print(type(idbooks))
    conn = get_db_connection()
    conn.execute('DELETE FROM borrowed_books WHERE books_idbooks1=?',(idbooksint,))
    conn.commit()
    conn.close
    return render_template('bookreturned.html')
    #idborrowersint = int(idborrowers)
    #conn = get_db_connection()
    #conn.execute('DELETE FROM borrowed_books WHERE books_idbooks1=?',(idborrowersint))
    #conn.commit()
    #conn.close
    #return render_template('error.html')


        #if lname in search or fname in search:
            #return render_template('spare.html', info = search)
        #else:
            #return render_template('main.html')


#@app.route('/search/<term>')
#def search(term):
    #conn = get_db_connection()

#getting rid of port 5000 in the url           
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)


#conn.execute('INSERT INTO borrowed_books (books_idbooks,borrowers_idborrowers1) VALUES (?,?),(books_idbooks,borrowers_idborrowers)')
