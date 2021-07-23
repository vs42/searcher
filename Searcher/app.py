from elasticsearch import Elasticsearch
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import csv

csv_file = open('posts.csv', 'r', encoding='utf-8')
reader = csv.reader(csv_file)

app = Flask(__name__)

db = SQLAlchemy(app)


class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rubrics = db.Column(db.String(64))
    text = db.Column(db.String(120))
    created_date = db.Column(db.String(120))


migrate = Migrate(app, db)

es = Elasticsearch("elasticsearch:9200")


def csv2db():
    id = 1
    for row in reader:
        if id != 1:
            text = Text(text=row[0], created_date=row[1], rubrics=row[2])
            db.session.add(text)
            db.session.commit()
        id += 1


def db2index():
    if es.ping():
        print('pinged')
        for text in Text.query.all():
            if not es.exists(index='my_index', doc_type='my_index', id=text.id):
                es.create(index='my_index', doc_type='my_index', id=text.id,
                      body={'text': text.text})
    else:
        print('ping failed')


@app.route("/delete", methods=['post', 'get'])
def delete():
    result = ''
    if request.method == 'POST':
        delete_id = request.form['delete_text']
        if delete_id.isdigit():
            if es.exists(index='my_index', doc_type='my_index', id=int(delete_id)):
                result = 'deleted'
                es.delete(index='my_index', doc_type='my_index', id=int(delete_id))
                db.session.delete(Text.query.get(int(delete_id)))
            else:
                result = 'cannot delete, already deleted'
        else:
            result = 'cannot delete, print number'
    return render_template("home.html", result=result)


@app.route("/", methods=['post', 'get'])
@app.route("/search", methods=['post', 'get'])
def search():
    if request.method == 'POST':
        search_text = request.form['search_text']
        result = es.search(body={'query': {'match': {'text': search_text}}})
        result = result['hits']['hits']
        if len(result) > 20:
            result = result[:20]
        result = Text.query.filter(Text.id.in_([i['_id'] for i in result])).order_by('created_date')
        return render_template("result.html", result=result)
    return render_template("search.html")
