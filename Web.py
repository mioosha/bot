from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/')
def index():
    user_id = request.args.get("user_id", "Неизвестный пользователь")
    return render_template("index.html", user_id=user_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
