from asyncio import current_task
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import _thread
import notify2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/maindb.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class maindb(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(200), nullable=False)
    tdata = db.Column(db.String(200), nullable=False)
    tdeadline = db.Column(db.String(500), nullable=False)
    tstatus = db.Column(db.String(40), default="Incomplete")

    def __repr__(self) -> str:
        return f"{self.tid} - {self.tdata}"

@app.route('/', methods=['GET', 'POST'])
def addTask():
    if request.method=="GET":
        current = datetime.strptime(str(datetime.now())[:19], "%Y-%m-%d %H:%M:%S")
        tdeadlineH = current.hour
        tdeadlineM = current.minute
        tdeadlineS = current.second
        tdeadlined = current.day
        tdeadlinem = current.month
        tdeadliney = current.year
        
        return render_template("addTask.html", tdeadlineH = tdeadlineH, tdeadlineM = tdeadlineM, tdeadlineS = tdeadlineS, tdeadlined = tdeadlined, tdeadlinem = tdeadlinem, tdeadliney = tdeadliney)
    if request.method=='POST':
        tdata = request.form['tdata']
        tdeadliney = request.form['tdeadliney']
        tdeadlinem = request.form['tdeadlinem']
        tdeadlined = request.form['tdeadlined']
        tdeadlineH = request.form['tdeadlineH']
        tdeadlineM = request.form['tdeadlineM']
        tdeadlineS = request.form['tdeadlineS']
        tdeadline = datetime(int(tdeadliney), int(tdeadlinem), int(tdeadlined), int(tdeadlineH), int(tdeadlineM), int(tdeadlineS), 0)
        task = maindb(uid=0 , tdata=tdata ,tdeadline=tdeadline)
        db.session.add(task)
        db.session.commit()
        todo = maindb.query.filter_by(uid=0,tdata=tdata).first()
        print(todo)
        tid = todo.tid
        current_time = datetime.now()
        def looper(current_time, tdeadline, tdata, tid):
            while(current_time < tdeadline):
                current_time = datetime.now()
                #print(todoCheck)
                tdeadlinenew = maindb.query.filter_by(tid=tid).first().tdeadline
                #print(tdeadlinenew)
                if str(tdeadlinenew) != str(tdeadline):
                    tdeadlineH = tdeadlinenew[11:13]
                    tdeadlineM = tdeadlinenew[14:16]
                    tdeadlineS = tdeadlinenew[17:19]
                    tdeadlined = tdeadlinenew[8:10]
                    tdeadlinem = tdeadlinenew[5:7]
                    tdeadliney = tdeadlinenew[:4]
                    tdeadline = datetime(int(tdeadliney), int(tdeadlinem), int(tdeadlined), int(tdeadlineH), int(tdeadlineM), int(tdeadlineS))
                #print(current_time, tdeadline)
                continue
            
            print("Success")
            notify2.init("To Do Reminder")
            notify2.Notification("To Do Reminder", tdata).show()
            return 0
        _thread.start_new_thread(looper, (current_time, tdeadline, tdata, tid))
        return redirect("/viewTasks")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")

@app.route('/viewTasks', methods=['GET', 'POST'])
def view():
    allTodo = maindb.query.filter_by(uid=0).all()
    return render_template("viewTasks.html", allTodo=allTodo)

@app.route('/completeTask/<int:tid>', methods=['GET'])
def completeTask(tid):
    todo = maindb.query.filter_by(tid=tid).first()
    todo.tstatus = "Completed"
    db.session.add(todo)
    db.session.commit()
    return redirect("/viewTasks")

@app.route('/updateTask/<int:tid>', methods=['GET', 'POST'])
def update(tid):
    if request.method=="GET":
        todo = maindb.query.filter_by(tid=tid).first()
        tdata = todo.tdata
        tdeadlineH = todo.tdeadline[11:13]
        tdeadlineM = todo.tdeadline[14:16]
        tdeadlineS = todo.tdeadline[17:19]
        tdeadlined = todo.tdeadline[8:10]
        tdeadlinem = todo.tdeadline[5:7]
        tdeadliney = todo.tdeadline[:4]
        return render_template("updateTask.html", tid=tid, tdata=tdata, tdeadlineH = tdeadlineH, tdeadlineM = tdeadlineM, tdeadlineS = tdeadlineS, tdeadlined = tdeadlined, tdeadlinem = tdeadlinem, tdeadliney = tdeadliney)
    if request.method=="POST":
        todo = maindb.query.filter_by(tid=tid).first()
        tdata = request.form['tdata']
        tdeadliney = request.form['tdeadliney']
        tdeadlinem = request.form['tdeadlinem']
        tdeadlined = request.form['tdeadlined']
        tdeadlineH = request.form['tdeadlineH']
        tdeadlineM = request.form['tdeadlineM']
        tdeadlineS = request.form['tdeadlineS']
        tdeadline = str(datetime(int(tdeadliney), int(tdeadlinem), int(tdeadlined), int(tdeadlineH), int(tdeadlineM), int(tdeadlineS)))
        todo.tdata = tdata
        todo.tdeadline = tdeadline
        db.session.add(todo)
        db.session.commit()
        return redirect("/viewTasks")     

@app.route('/deleteTask/<int:tid>')
def delete(tid):
    todo = maindb.query.filter_by(tid=tid).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/viewTasks")            
               
            

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234, debug=True)