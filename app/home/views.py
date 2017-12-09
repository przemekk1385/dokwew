from flask import (abort, current_app as app, flash, render_template,
                   redirect, send_from_directory, url_for)
from flask_login import current_user, login_required

from . import home
from ..models import Document, Meeting, User

import os


@home.route('/')
def homepage():
    return render_template('home/index.html', title='Start')


@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('home/admin_dashboard.html', title="Pulpit")


@home.route('/dashboard')
@login_required
def dashboard():
    return render_template('home/dashboard.html', title='Pulpit')


@home.route('/documents/', defaults={'page': 1})
@home.route('/documents/<int:page>')
@login_required
def list_documents(page):
    user = User.query.get_or_404(current_user.get_id())
    documents = user.documents.paginate(page,
                                        app.config['ITEMS_PER_PAGE'])
    if documents.total == 0:
        flash('Brak dokumentów widocznych dla użytkownika %s.' %
              user.username, 'info')
    return render_template('home/list_documents.html',
                           documents=documents,
                           title='Lista dokumentów')


@home.route('/documents/download/<int:document_id>')
@login_required
def download_document(document_id):  # todo: check user id before serving
    document = Document.query.get_or_404(document_id)
    if os.path.isfile(os.path.join(app.config['MEDIA_DIR'],
                      document.filename)):
        return send_from_directory(app.config['MEDIA_DIR'], document.filename,
                                   as_attachment=True)
    else:
        flash('Nie można pobrać dokumentu %s.' % document.filename, 'danger')
        return redirect(url_for('home.dashboard'))


@home.route('/meetings', defaults={'page': 1})
@home.route('/meetings/<int:page>')
@login_required
def list_meetings(page):
    user = User.query.get_or_404(current_user.get_id())
    meetings = user.meetings.paginate(page,
                                      app.config['ITEMS_PER_PAGE'])
    board = False
    management = False
    if meetings.total == 0:
        flash('Brak wydarzeń widocznych dla użytkownika %s.' %
              user.username, 'info')
    else:
        for meeting in meetings.items:
            meeting.count = meeting.documents.count()
        if user.id == app.config['BOARD_ID']:
            board = True
        if user.id == app.config['MANAGEMENT_ID']:
            management = True
    return render_template('home/list_meetings.html',
                           board=board,
                           management=management,
                           meetings=meetings,
                           title='Lista wydarzeń')


@home.route('/meetings/details/<int:meeting_id>')
@login_required
def meeting_details(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    documents = meeting.documents.all()
    board = False
    management = False
    if current_user.id == app.config['BOARD_ID']:
        board = True
    if current_user.id == app.config['MANAGEMENT_ID']:
        management = True
    return render_template('home/meeting_details.html',
                           board=board,
                           documents=documents,
                           management=management,
                           meeting=meeting,
                           title='Szczegóły wydarzenia')
