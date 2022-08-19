import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

app = Flask(__name__)

app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.excel']
app.config['UPLOAD_PATH'] = 'uploads/'

df = pd.read_excel("TrkceTwit .xlsx")
df.drop('Unnamed: 2', inplace=True, axis=1)
X_train,x_test,y_train,y_test  = train_test_split(df["Tweets"],df["Duygu"],test_size=0.2)

model = make_pipeline(TfidfVectorizer(),MultinomialNB())
model.fit(X_train,y_train)

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('asdsdd.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        if filename[-4:] =="xlsx":
            data =pd.read_excel(f"uploads\{filename}")
            
            return render_template("content.html",veri =data)
        else :
            data =pd.read_csv(f"uploads\{filename}")
            
            return render_template("content.html",veri =data)
    return '', 204



if __name__ == "__main__":
    app.run(debug =True)#uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
