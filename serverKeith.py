from flask import Flask, render_template, session, redirect, url_for, flash, request 
from flask.ext.script import Manager 
from flask.ext.bootstrap import Bootstrap 
from flask.ext.moment import Moment 
from flask.ext.wtf import Form 
from wtforms import StringField, SubmitField 
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

#manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#(May need, may not) Function used to clean answers from HTML form
#def stringCleaner(s1):
#    l=len(s1)
#    endString=''
#    for i in range(2,l-2): endString += s1[i]
#    return endString

@app.route('/busNumber/<busNumber>/stop1/<stop1>/stop2/<stop2>',methods=['POST'])
def busLogic():
   # busNumber=request.form['busNumber']
   # stop1=request.form['stop1']
   # stop2=request.form['stop2']
    print(busNumber,stop1,stop2)
    return redirect('/')

@app.route('/', methods=['GET','POST'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
