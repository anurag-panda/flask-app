from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Attendance
from camera import Camera
import cv2

camera = Camera()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    attendances = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.timestamp.desc()).limit(10)
    return render_template('dashboard.html', attendances=attendances)

@app.route('/attendance')
@login_required
def attendance():
    return render_template('attendance.html')

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = camera.process_frame(frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/mark_attendance', methods=['POST'])
@login_required
def mark_attendance():
    status = request.form.get('status', 'check_in')
    attendance = Attendance(user_id=current_user.id, status=status)
    db.session.add(attendance)
    db.session.commit()
    flash(f'Attendance marked: {status}')
    return redirect(url_for('dashboard'))
