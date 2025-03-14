'''from flask import requests 
@app_route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    return do_the_login()#обработка логина про POST-запросе
  else:
    return show_the_login_form() #ОТображение формы логина прие GET запросе
  
  
@app_get('/login')
def login_get():
  return show_the_login

@app_post('/login')
def login_post:
  return do_the_login()'''

'''from flask import redirect, url_for
@app.route('/')
def index():
  return redirect(url_for('login'))
  '''


