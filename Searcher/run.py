import app
import time

app.db.create_all()
app.csv2db()
for i in range(100):
    if not app.es.ping():
        time.sleep(1)
    else:
        time.sleep(10)
        break
if app.es.ping() and app.es.count()['count'] < 1500:
    app.db2index()
else:
    raise ConnectionError()
app.app.run(host='0.0.0.0')
