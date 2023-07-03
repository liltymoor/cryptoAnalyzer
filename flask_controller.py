

from flask import Flask, render_template
import pandas as pd




app = Flask(__name__, template_folder='flask_templates')




@app.route('/')
def home():
    return render_template('index.html')


@app.route('/data/<crypto>', methods=['GET'])
def data(crypto):
    df = pd.read_parquet(f'temp/{crypto}.parquet')
    return df.to_json(orient='records')


if __name__ == '__main__':
    app.run(debug=False)
