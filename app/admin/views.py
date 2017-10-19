from flask import (abort, current_app as app,
                   flash, redirect, request, render_template, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from . import admin, filters
from .forms import (AssignDocumentForm, EditShareDocumentForm,
                    CreateEditMeetingForm)
from .. import db
from ..models import Document, Meeting, Type, User

import os


"""
Auxiliary functions
"""


def check_admin():
    if not current_user.is_admin:
        abort(403)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Błąd w polu %s. %s' % (getattr(form, field).label.text,
                  error), 'danger')


def list_upload_dir():
    documents = []
    for el in os.listdir(app.config['UPLOAD_DIR']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_DIR'], el)):
            documents.append({'filename': el})
    if len(documents) == 0:
        flash('Brak nieprzypisanych dokumentów.', 'info')
    return documents


"""
Document's related functions
"""


@admin.route('/documents', defaults={'page': 1})
@admin.route('documents/<int:page>')
@login_required
def manage_documents(page):
    check_admin()
    unassigned_documents = list_upload_dir()
    shared_documents = Document.query.\
        filter(Document.type.has(Type.is_standlone)).\
        paginate(page, app.config['ITEMS_PER_PAGE'])
    if shared_documents.total == 0:
        flash('Brak udostępnionych dokumentów.', 'info')
    return render_template('admin/manage_documents.html',
                           shared_documents=shared_documents,
                           unassigned_documents=unassigned_documents,
                           title='Zarządzaj dokumentami')


@admin.route('/documents/assign/<int:meeting_id>/<filename>',
             methods=['GET', 'POST'])
@login_required
def assign_document(meeting_id, filename):
    check_admin()
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.user_id == app.config['BOARD_ID']:
        meeting.board = True
    if meeting.user_id == app.config['MANAGEMENT_ID']:
        meeting.management = True
    form = AssignDocumentForm()
    types = Type.query.with_entities(Type.id, Type.name).\
        filter_by(is_standlone=False)
    form.type_id.choices = types
    if form.validate_on_submit():
        type = Type.query.get_or_404(form.type_id.data)
        if type.signature_required and form.signature.data == '':
            flash('Typ %s wymaga podania oznaczenia dokumentu.' % type.name,
                  'danger')
        if len(filename) > app.config['MAX_FILENAME_LENGTH']:
            flash('Maksymalna długość nazwy pliku to %i znaków.' %
                  app.config['MAX_FILENAME_LENGTH'], 'danger')
        if not form.errors:
            src = os.path.join(app.config['UPLOAD_DIR'], filename)
            dst = os.path.join(app.config['MEDIA_DIR'], filename)
            if os.path.isfile(dst):
                flash('Dokument o nazwie %s już istnieje.' % filename,
                      'danger')
            else:
                os.rename(src, dst)
                type = Type.query.get_or_404(form.type_id.data)
                if form.signature.data != '' and not type.signature_required:
                    document = Document(filename=filename,
                                        type_id=form.type_id.data,
                                        meeting_id=meeting_id)
                    flash('Zignorowano oznaczenie dokumentu dla typu %s.' %
                          type.name, 'warning')
                else:
                    document = Document(signature=form.signature.data,
                                        filename=filename,
                                        type_id=form.type_id.data,
                                        meeting_id=meeting_id)
                db.session.add(document)
                db.session.commit()
                flash('Przypisano dokument', 'success')
                return redirect(url_for('admin.edit_meeting',
                                        meeting_id=meeting_id))
    else:
        flash_errors(form)
    return render_template('admin/assign_document.html',
                           document=filename,
                           form=form,
                           meeting=meeting,
                           title='Przypisz dokument')


@admin.route('/documents/delete/<filename>')
@login_required
def delete_document(filename):
    check_admin()
    dst = os.path.join(app.config['UPLOAD_DIR'], filename)
    if os.path.isfile(dst):
        os.remove(dst)
        flash('Usunięto plik %s.' % filename, 'success')
    else:
        flash('Nie można usunąć pliku %s.' % filename, 'danger')
    return redirect(url_for('admin.manage_documents'))


@admin.route('/documents/edit/<int:document_id>', methods=['GET', 'POST'])
@login_required
def edit_document(document_id):
    check_admin()
    document = Document.query.get_or_404(document_id)
    form = EditShareDocumentForm(obj=document)
    types = Type.query.with_entities(Type.id, Type.name).\
        filter(Type.is_standlone, Type.id != document.type_id).all()
    form.type_id.choices = [(document.type_id, document.type.name)] + types
    users = User.query.with_entities(User.id, User.username).\
        filter(~User.is_admin, User.id != document.user_id).all()
    form.user_id.choices = [(document.user_id, document.user.username)] + users
    if form.validate_on_submit():
        document.description = form.description.data
        document.type_id = form.type_id.data
        document.user_id = form.user_id.data
        db.session.commit()
        flash('Zmieniono dokument.', 'success')
        return redirect(url_for('admin.manage_documents'))
    else:
        flash_errors(form)
    form.description = document.description
    return render_template('admin/edit_share_document.html',
                           form=form,
                           edit_document=True,
                           title='Edytuj dokument')


@admin.route('/documents/share/<filename>', methods=['GET', 'POST'])
@login_required
def share_document(filename):
    check_admin()
    form = EditShareDocumentForm()
    types = Type.query.with_entities(Type.id, Type.name).\
        filter(Type.is_standlone).all()
    form.type_id.choices = types
    users = User.query.with_entities(User.id, User.username).\
        filter(~User.is_admin).all()
    form.user_id.choices = users
    if form.validate_on_submit():
        if len(filename) > app.config['MAX_FILENAME_LENGTH']:
            flash('Maksymalna długość nazwy pliku to %i znaków.' %
                  app.config['MAX_FILENAME_LENGTH'], 'danger')
        if not form.errors:
            src = os.path.join(app.config['UPLOAD_DIR'], filename)
            dst = os.path.join(app.config['MEDIA_DIR'], filename)
            if os.path.isfile(dst):
                flash('Dokument o nazwie %s już istnieje.' % filename,
                      'danger')
            else:
                os.rename(src, dst)
            document = Document(description=form.description.data,
                                filename=filename,
                                type_id=form.type_id.data,
                                user_id=form.user_id.data)
            db.session.add(document)
            db.session.commit()
            flash('Udostępniono dokument', 'success')
            return redirect(url_for('admin.manage_documents'))
    else:
        flash_errors(form)
    return render_template('admin/edit_share_document.html',
                           form=form,
                           share_document=True,
                           title='Udostępnij dokument')


@admin.route('/document/cancel/<int:document_id>')
@login_required
def stop_sharing(document_id):
    check_admin()
    document = Document.query.get_or_404(document_id)
    src = os.path.join(app.config['MEDIA_DIR'], document.filename)
    dst = os.path.join(app.config['UPLOAD_DIR'], document.filename)
    if os.path.isfile(dst):
        flash('Możliwy duplikat dokumenty %s.' % document.filename, 'danger')
    else:
        if os.path.isfile(src):
            os.rename(src, dst)
        else:
            flash('Brak dokumentu źródłowego.', 'warning')
        db.session.delete(document)
        db.session.commit()
        flash('Przerwano udostępnianie dokumentu %s.' % document.filename,
              'success')
    return redirect(url_for('admin.manage_documents'))


@admin.route('/documents/unassign/<int:meeting_id>/<int:document_id>')
@login_required
def unassign_document(meeting_id, document_id):
    check_admin()
    document = Document.query.get_or_404(document_id)
    src = os.path.join(app.config['MEDIA_DIR'], document.filename)
    dst = os.path.join(app.config['UPLOAD_DIR'], document.filename)
    if os.path.isfile(dst):
        flash('Możliwy duplikat dokumenty %s.' % document.filename, 'danger')
    else:
        if os.path.isfile(src):
            os.rename(src, dst)
        else:
            flash('Brak dokumentu źródłowego.', 'warning')
        db.session.delete(document)
        db.session.commit()
        flash('Zwolniono dokument %s.' % document.filename, 'success')
    return redirect(url_for('admin.edit_meeting', meeting_id=meeting_id))


@admin.route('/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_documents():
    check_admin()
    if request.method == 'POST':
            f = request.files.get('document')
            dst = os.path.join(app.config['UPLOAD_DIR'],
                               secure_filename(f.filename))
            f.save(dst)
    return render_template('admin/upload_documents.html',
                           title='Załaduj dokumenty')


"""
Meeting's related functions
"""


@admin.route('/meetings', defaults={'page': 1})
@admin.route('/meetings/<int:page>')
@login_required
def manage_meetings(page):
    check_admin()
    meetings = Meeting.query.paginate(page, app.config['ITEMS_PER_PAGE'])
    if meetings.total == 0:
        flash('Brak wydarzeń.', 'info')
    else:
        for meeting in meetings.items:
            if meeting.user_id == app.config['BOARD_ID']:
                meeting.board = True
            if meeting.user_id == app.config['MANAGEMENT_ID']:
                meeting.management = True
    return render_template('admin/manage_meetings.html',
                           meetings=meetings,
                           title='Zarządzaj wydarzeniami')


@admin.route('/meetings/create', methods=['GET', 'POST'])
@login_required
def create_meeting():
    check_admin()
    form = CreateEditMeetingForm()
    users = User.query.with_entities(User.id, User.username).\
        filter(~User.is_admin).all()
    form.user_id.choices = users
    if form.validate_on_submit():
        meeting = Meeting(date=form.date.data,
                          signature=form.signature.data,
                          summary=form.summary.data,
                          user_id=form.user_id.data)
        db.session.add(meeting)
        db.session.commit()
        flash('Dodano wydarzenie.', 'success')
        return redirect(url_for('home.admin_dashboard'))
    else:
        flash_errors(form)
    return render_template('admin/create_edit_meeting.html',
                           create_meeting=True,
                           form=form,
                           title='Utwórz wydarzenie')


@admin.route('/meetings/delete/<int:meeting_id>')
@login_required
def delete_meeting(meeting_id):
    check_admin()
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.documents.count() > 0:
        flash('Wydarzenie ma przypisane dokumenty.', 'danger')
    else:
        db.session.delete(meeting)
        db.session.commit()
        flash('Usunięto wydarzenie', 'success')
    return redirect(url_for('admin.manage_meetings'))


@admin.route('/meetings/edit/<int:meeting_id>', methods=['GET', 'POST'])
@login_required
def edit_meeting(meeting_id):
    check_admin()
    meeting = Meeting.query.get_or_404(meeting_id)
    form = CreateEditMeetingForm(obj=meeting)
    users = User.query.with_entities(User.id, User.username).\
        filter(~User.is_admin, User.id != meeting.user_id).all()
    form.user_id.choices = [(meeting.user_id, meeting.user.username)] + users
    if form.validate_on_submit():
        meeting.date = form.date.data
        meeting.signature = form.signature.data
        meeting.summary = form.summary.data
        meeting.user_id = form.user_id.data
        db.session.commit()
        flash('Zmieniono wydarzenie.', 'success')
        return redirect(url_for('admin.manage_meetings'))
    else:
        flash_errors(form)
    form.date = meeting.date
    form.signature = meeting.signature
    form.summary = meeting.summary
    documents = list_upload_dir()
    return render_template('admin/create_edit_meeting.html',
                           assigned_documents=meeting.documents.all(),
                           edit_meeting=True,
                           form=form,
                           meeting_id=meeting_id,
                           title='Edytuj wydarzenie',
                           unassigned_documents=documents)
