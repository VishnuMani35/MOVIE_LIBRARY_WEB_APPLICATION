from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import pymysql
import bcrypt
import datetime
import requests

app = Flask(__name__)
app.secret_key = 'top_secret'
mydb = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "M@ni1234",
    database = "fasal"
)

cur = mydb.cursor()
if mydb.open:
    print("Connected")
    cur = mydb.cursor()
    cur.execute("create database if not exists fasal;")
    cur.execute("use fasal")
    cur.execute("CREATE TABLE IF NOT EXISTS users ( S_no INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(1000), password VARCHAR(1000) );")
else:
    print("Falied to connect")
    
apikey = '8e52cc67'
    
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

@app.route('/', methods=['POST','GET'])
def index():
    return render_template("index.html")

@app.route('/<typer>', methods=['POST', 'GET'])
def add(typer):
    query = 'SELECT username, email, password FROM users'
    cur.execute(query)
    list_of_users = cur.fetchall()
    # print(list_of_users)
    if request.method == 'POST' and typer == 'signin':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password = hash_password(password)
        for items in list_of_users:
            if items[0] == name or items[1] == email:
                return render_template("login.html", err="User already exists", new=typer)
        query = f'insert into users (username, email, password) values ("{name}", "{email}", "{password}")'
        cmd = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cur.execute(cmd, (name, email, password))
        query = f'CREATE Table {name} (S_no INT PRIMARY KEY AUTO_INCREMENT, movies LONGTEXT, watchlist_name VARCHAR(1000));'
        print(query)
        # cur.execute(query)
        mydb.commit()
        session['username'] = name
        return redirect(url_for('home'))
    elif request.method == 'POST' and typer == 'login':
        email = request.form.get('email')
        password = request.form.get('password')
        query = 'SELECT username FROM users WHERE email = %s'
        cur.execute(query, (email,))
        name = cur.fetchone()
        if name == None:
            return render_template("login.html", err="User not found", new=typer)
        for items in list_of_users:
            if items[1] == email:
                if bcrypt.checkpw(password.encode('utf-8'), items[2].encode('utf-8')):
                    session['username'] = name[0]
                    return redirect(url_for('home'))
        return render_template("login.html", err="Incorrect username / password", new=typer)
    elif typer != 'login' and typer != 'signin' and typer != 'favicon.ico':
        if 'username' not in session:
            return redirect(url_for('index'))
        typer = typer.replace("+", " ")
        print(typer)
        if typer[0:4] == '!@$%':
            print(1, typer)
            typer = typer[4:]
            print(typer)
            url = f'http://www.omdbapi.com/?s=${typer}&apikey={apikey}'
            response = requests.get(url)
            if response.status_code == 200:
                info = response.json()
                print(info)
            else:
                print(f'Error: {response.status_code}')
                return redirect(url_for('home'))
            info = info['Search']
            movie_names = []
            tv_shows = []
            postersM = []
            postersT = []
            length1 = 0
            length2 = 0
            for i in range(len(info)):
                if info[i]['Type'] == 'movie':
                    movie_names.append(info[i]['Title'])
                    postersM.append(info[i]['Poster'])
                    length1 = length1 + 1
                else :
                    tv_shows.append(info[i]['Title'])
                    postersT.append(info[i]['Poster'])
                    length2 = length2 + 1
            stylesList = ['', '', '', '', '', 'last', '', '', '', '', '', 'last', '', '', '', '', '', 'last', '', '', '', '', '', 'last']
            while length1 % 6 != 0:
                movie_names.append(' ')
                postersM.append('https://wallpapers.com/images/hd/pure-black-oled-9etgj73d7owi4s0g.jpg')
                length1 = length1 + 1
            return render_template('results.html', movie_names=movie_names, tv_shows=tv_shows, postersT=postersT, postersM=postersM, lengthOfArray1=length1, lengthOfArray2=length2, stylesList=stylesList)
        else:
            print(2, typer)
            url = f'http://www.omdbapi.com/?t=${typer}&apikey={apikey}'
            response = requests.get(url)
            if response.status_code == 200:
                info = response.json()
                print(info)
            else:
                print(f'Error: {response.status_code}')
                return redirect(url_for('home'))
            ratings = ["-", "-", "-"]
            if 'Ratings' in info:
                for dicts in info['Ratings']:
                    if dicts['Source'] == 'Internet Movie Database':
                        ratings[0] = dicts['Value']
                    elif dicts['Source'] == 'Rotten Tomatoes':
                        ratings[1] = dicts['Value']
                    elif dicts['Source'] == 'Metacritic':
                        ratings[2] = dicts['Value']
            info['Ratings'] = ratings
            username = session['username']
            query = f'SELECT watchlist_name FROM {username}'
            print(query)
            cur.execute(query)
            lists = cur.fetchall()
            lists = [x[0] for x in lists]
            print(lists)
            return render_template('movie.html', movies=info, lists=lists)
    mydb.commit()
    return render_template("login.html", new=typer)

@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    movie_names1 = ['X-MEN', 'INTERSTELLAR', 'INCEPTION', 'VALKYRIE', 'GLADIATOR', 'ICE AGE']
    movie_names2 = ['OPPENHEIMER', 'TENET', 'KUNG FU PANDA', 'EAGLE EYE', 'NARNIA', 'ANGELS & DEMONS']
    sources = """
        https://m.media-amazon.com/images/M/MV5BNDBhNDJiMWEtOTg4Yi00NTYzLWEzOGMtMjNmNjAxNTBlMzY3XkEyXkFqcGdeQXVyNTIzOTk5ODM@._V1_.jpg
        https://image.tmdb.org/t/p/original/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg
        https://m.media-amazon.com/images/I/71DwIcSgFcS.jpg
        https://images.jdmagicbox.com/comp/jd_social/news/2018jul13/image-46993-40zlbvqplm.jpg
        https://images-cdn.ubuy.co.in/6350e84bd5194b74054681be-ytch-movie-poster-gladiator-canvas-art.jpg
        https://image.tmdb.org/t/p/original/gLhHHZUzeseRXShoDyC4VqLgsNv.jpg
        https://m.media-amazon.com/images/I/81218n6JFgL._AC_UF1000,1000_QL80_.jpg
        https://m.media-amazon.com/images/M/MV5BMzU3YWYwNTQtZTdiMC00NjY5LTlmMTMtZDFlYTEyODBjMTk5XkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_FMjpg_UX1000_.jpg
        https://m.media-amazon.com/images/I/51qboNmFw3L._AC_UF894,1000_QL80_.jpg
        https://i.etsystatic.com/10683147/r/il/d6e3c2/2049546509/il_570xN.2049546509_n8i9.jpg
        https://img.fruugo.com/product/5/25/14537255_max.jpg
        https://m.media-amazon.com/images/M/MV5BMjEzNzM2MjgxMF5BMl5BanBnXkFtZTcwNTQ1MTM0Mg@@._V1_.jpg
    """
    sources = sources.splitlines()
    stylesList = ['', '', '', '', '', 'last']
    return render_template("home2.html", movie_names1=movie_names1, movie_names2=movie_names2, sources=sources, stylesList=stylesList)

@app.route('/playlists', methods=['POST', 'GET'])
def playlists():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    query = f'SELECT movies, watchlist_name FROM {username}'
    print(query)
    cur.execute(query)
    pairs = cur.fetchall()
    print(pairs)
    info = {}
    for row in pairs:
        temp = row[0][:-1].strip('()')
        movies = temp.split(')+(')
        print(movies)
        info[f'{row[1]}'] = movies
    print(info)
    return render_template('playlist.html', info=info)

@app.route('/addList', methods=['POST', 'GET'])
def addList():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    data = request.json
    list_name = data['list_name']
    query = f'INSERT INTO {username} (movies, watchlist_name) VALUES ("", "{list_name}")'
    print(query)
    cur.execute(query)
    print(data)
    responseObject = {
        'status': 'WatchList Created'
    }
    return responseObject

@app.route('/deleteList', methods=['POST', 'GET'])
def deleteList():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    data = request.json
    print(data)
    list_name = data['list_name']
    query = f'DELETE FROM {username} WHERE watchlist_name = "{list_name}"'
    print(query)
    cur.execute(query)
    responseObject = {
        'status': 'WatchList Deleted'
    }
    return responseObject

@app.route('/addMovie', methods=['POST', 'GET'])
def addMovie():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    data = request.json
    print(data)
    list_name = data['list_name']
    movie_name = data['movie_name']
    query = f'SELECT movies FROM {username} WHERE watchlist_name = "{list_name}"'
    print(query)
    cur.execute(query)
    movie = cur.fetchone()
    print(movie)
    movie = movie[0]
    movie_name = "(" + movie_name + ")+"
    if movie_name in movie:
        movie_name = movie_name[1:-2]
        responseObject = {
            'status': f"{movie_name} is already in {list_name}",
            'code': 1
        }
        return responseObject
    movie = movie + movie_name
    query = f'UPDATE {username} SET movies = "{movie}" WHERE watchlist_name = "{list_name}"'
    print(query)
    cur.execute(query)
    movie_name = movie_name[1:-2]
    responseObject = {
        'status': f"Added {movie_name} to {list_name}",
        'code': 0
    }
    return responseObject

@app.route('/removeMovie', methods=['POST', 'GET'])
def removeMovie():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    data = request.json
    print(data)
    list_name = data['list_name']
    movie_name = data['movie_name']
    query = f'SELECT movies FROM {username} WHERE watchlist_name = "{list_name}"'
    cur.execute(query)
    movie = cur.fetchone()
    print(movie)
    movie = movie[0]
    movie_name = "(" + movie_name + ")+"
    movie = movie.replace(movie_name, "")
    query = f'UPDATE {username} SET movies = "{movie}" WHERE watchlist_name = "{list_name}"'
    print(query)
    cur.execute(query)
    movie_name = movie_name[1:-2]
    responseObject = {
        'status': f"Deleted {movie_name} from {list_name}",
        'code': 0
    }
    return responseObject

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
