from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import os

app = Flask(__name__)
app.secret_key = "top-secret 🤫"
TA_PASSWORD = os.environ.get("TA_PASSWORD", "ta123")

queue = []

# ---------- Helpers ----------
def ta_required():
    return session.get("ta_logged_in")


# ---------- Student: Submit ----------
@app.route("/", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        question = request.form.get("question", "").strip()

        if not question or name:
            # If empty, just reload submit page
            return redirect(url_for("submit"))

        qid = str(uuid.uuid4())
        queue.append({
            "id": qid,
            "name": name if name else "Anonymous",
            "question": question
        })

        # ALWAYS redirect after successful POST
        return redirect(url_for("wait", qid=qid))

    return render_template("submit.html")


# ---------- Student: Waiting ----------
@app.route("/wait/<qid>")
def wait(qid):
    position = None

    for i, q in enumerate(queue):
        if q["id"] == qid:
            position = i
            break

    # If not found → resolved
    if position is None:
        return render_template("done.html")

    return render_template("wait.html", position=position)


# ---------- TA Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        password = request.form.get("password")
        if password == TA_PASSWORD:
            session["ta_logged_in"] = True
            return redirect(url_for("view_queue"))
        else:
            error = "Incorrect password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("ta_logged_in", None)
    return redirect(url_for("login"))


# ---------- TA Queue ----------
@app.route("/queue")
def view_queue():
    if not ta_required():
        return redirect(url_for("login"))
    return render_template("queue.html", queue=queue)


@app.route("/resolve/<int:index>")
def resolve(index):
    if not ta_required():
        return redirect(url_for("login"))

    if 0 <= index < len(queue):
        queue.pop(index)

    return redirect(url_for("view_queue"))


@app.route("/reset")
def reset():
    if not ta_required():
        return redirect(url_for("login"))

    queue.clear()
    return redirect(url_for("view_queue"))


# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
