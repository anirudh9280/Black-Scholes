from flask import Flask

app = Flask('MyFlaskApp')
@app.route('/', methods=["GET"])
def welcome():
    return "<h1>Hello evan</h1>"

if __name__ == "__main__":
    app.run(); 

