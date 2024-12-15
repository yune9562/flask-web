from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

# MySQL Database Connection Configuration
db = pymysql.connect(
    host='localhost',
    user='root',
    password='toor',
    database='flaskDB',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post')
@app.route('/post/page/<int:page>')
def post(page=1):
    posts_per_page = 10
    offset = (page - 1) * posts_per_page
    search_query = request.args.get('search', '')
    search_option = request.args.get('search_option', 'all')

    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM boardtest")
        total_posts = cursor.fetchone()['total']
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        # 검색 옵션에 따른 쿼리 변경
        if search_option == 'title':
            cursor.execute(
                "SELECT * FROM boardtest WHERE title LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                ('%' + search_query + '%', posts_per_page, offset)
            )
        elif search_option == 'content':
            cursor.execute(
                "SELECT * FROM boardtest WHERE content LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                ('%' + search_query + '%', posts_per_page, offset)
            )
        elif search_option == 'all':
            cursor.execute(
                "SELECT * FROM boardtest WHERE title LIKE %s OR content LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
                ('%' + search_query + '%', '%' + search_query + '%', posts_per_page, offset)
            )

        posts = cursor.fetchall()

    return render_template('post.html', postlist=posts, total_pages=total_pages, current_page=page, search=search_query, search_option=search_option)

@app.route('/post/content/<int:id>')
def content(id):
    with db.cursor() as cursor:
        cursor.execute("UPDATE boardtest SET view = view + 1 WHERE id = %s", (id,))
        db.commit()
        cursor.execute("SELECT * FROM boardtest WHERE id = %s", (id,))
        post = cursor.fetchall()
    return render_template('content.html', data=post)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        content = request.form['content']
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO boardtest (name, title, content) VALUES (%s, %s, %s)",
                (name, title, content)
            )
            db.commit()
        return redirect('/post')
    return render_template('write.html')

@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE boardtest SET title = %s, content = %s WHERE id = %s",
                (title, content, id)
            )
            db.commit()
        return redirect(f'/post/content/{id}')
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM boardtest WHERE id = %s", (id,))
        post = cursor.fetchall()
    return render_template('edit.html', data=post)

@app.route('/post/delete/<int:id>')
def delete(id):
    return render_template('delete.html', id=id)

@app.route('/post/delete/success/<int:id>')
def delete_success(id):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM boardtest WHERE id = %s", (id,))
        db.commit()
        # Reset the ID values after deletion
        cursor.execute("SET @new_id = 0;")
        cursor.execute("UPDATE boardtest SET id = (@new_id := @new_id + 1);")
        cursor.execute("ALTER TABLE boardtest AUTO_INCREMENT = 1;")
        db.commit()
    return redirect('/post')

if __name__ == '__main__':
    app.run(debug=True)
