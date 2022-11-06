from crypt import methods
import email
from re import search, template
from flask import Flask, render_template, redirect, url_for, request, flash, session
import sqlite3
from datetime import datetime, timedelta
#from flask_mysqldb import MySQL
#import MySQLdb.cursors

logged = "false"

app = Flask(__name__)

app.secret_key = 'hWmZq4t7w!z%C*F-JaNdRgUjXn2r5u8x'


def get_db_connection():
    conn = sqlite3.connect('mydb.sdb')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def direct():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
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
            logged = "true"
            return redirect(url_for('library', info = title))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)





@app.route('/search', methods=['GET','POST'])
def main():
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
    if request.method == 'POST':
        conn = get_db_connection()
        title = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
        conn.close()
        return render_template('library.html', info = title)
    elif request.method == 'GET':
        conn = get_db_connection()
        title = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
        conn.close()
        return render_template('library.html', info = title)
@app.route('/addbook',methods=['GET','POST'])
def addbook():
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
            else:
                return render_template('alreadyinlibrary.html')
    return render_template('library.html')
    
@app.route('/borrowbook/<int:idbooks>', methods=['GET','POST'])
def borrowbook(idbooks):
    if request.method == 'GET':
        #connecting to the db
        conn = get_db_connection()
        borrowers = conn.execute('SELECT * FROM borrowers').fetchall()
        title = conn.execute('SELECT * FROM books WHERE idbooks=?',(idbooks,)).fetchall()
        print(len(title))
        conn.close()
        return render_template('borrower.html', title=title, borrowers=borrowers, idbooks=idbooks)

@app.route('/borrowbook/borrowers2/<idbooks>', methods=['GET','POST'])
def borrowers2(idbooks,idborrowers):
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
            conn = get_db_connection()
            #borrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchall()
            #Selecting the profile of the borrower from the table 
            idborrowers = conn.execute('SELECT idborrowers FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(form_fname, form_lname)).fetchone()
            conn.commit()
            if type(idborrowers) is int:
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
    return render_template('successful.html')

#@app.route('/returnbooks', methods=['GET','POST'])
#def aboutme():
    return render_template('aboutme.html')


@app.route('/aboutme', methods=['GET','POST'])
def aboutme():
    return render_template('aboutme.html')


#@app.route('/createaccount', methods=['GET','POST'])
#def createaccount():
    return render_template('createaccount.html')

@app.route('/weirdo', methods=['GET','POST'])
def weirdo():
        return render_template('error.html')

#@app.route('/create', methods=['GET','POST'])
#def create():
    #if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
        email = request.form['email']

        if not username:
            flash('Username is REQUIRED!')
        elif not password:
            flash('Password is REQUIRED!')
        elif not email:
            flash('Email is REQUIRED!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO user (username, password, email) VALUES (?, ?, ?)',(username, password, email))
            conn.commit()
            conn.close()
        return redirect(url_for('main'))
    #return render_template('spare.html')


@app.route('/borrowers', methods=['GET','POST'])
def borrowers():
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
    return render_template('spare.html')


@app.route('/loan', methods=['GET','POST'])
def loan():
    return render_template('spare.html')

@app.route('/insertbook',methods=['GET','POST'])
def insertbook():
    return render_template('insertbook.html')

@app.route('/borrowerspage',methods=['GET','POST'])
def borrowerspage():
    conn = get_db_connection()
    borrowers = conn.execute('SELECT * FROM borrowers').fetchall()
    conn.close()
    return render_template('borrowerspage.html', borrowers = borrowers)

@app.route('/lendedbooks',methods=['GET','POST'])
def lendedbooks():
    conn = get_db_connection()
    books_borrowed = conn.execute('SELECT borrowed_books.idloan, books.author, books.title, borrowed_books.borrowers_idborrowers1, books.idbooks, borrowers.fname, borrowers.lname, borrowed_books.borrowed_date, borrowed_books.due_date FROM borrowed_books JOIN books ON borrowed_books.books_idbooks1=books.idbooks JOIN borrowers ON borrowed_books.borrowers_idborrowers1=borrowers.idborrowers',).fetchall()
    conn.close()
    return render_template('lendedbooks.html', books_borrowed = books_borrowed)

@app.route('/removed/<int:idbooks>', methods=['GET','POST'])
def removebook(idbooks):

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
