from flask_wtf import FlaskForm
from wtforms import (BooleanField, DateField, FieldList, FileField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import InputRequired, Length, Regexp


class ListFormBase(FlaskForm):
    submit = SubmitField('Przypisz')


def list_form_builder(elements, label):
    class ListForm(ListFormBase):
        pass

    for (i, element) in enumerate(elements):
        #  setattr(ListForm, '%s_%d' % (label, i), BooleanField(label=label))
        setattr(ListForm, element, BooleanField(label=element))
    return ListForm()


class CreateEditMeetingForm(FlaskForm):
    date = DateField(
        'Data',
        format='%Y-%m-%d',
        validators=[
            InputRequired()
        ],
        description='Format rrrr-mm-dd'
    )
    signature = StringField(
        'Oznaczenie',
        validators=[
            InputRequired(),
            Regexp('^[IVXL]+$|^\d+$', message=('Dozwolone znaki to I, V, X, L,'
                                               + ' lub cyfry od 0 do 9.'))
        ],
        description='Cyfra rzymska lub arabska'
    )
    summary = TextAreaField('Podsumowanie', validators=[InputRequired()])
    user_id = SelectField('Widoczne dla', coerce=int,
                          validators=[InputRequired()])
    submit = SubmitField('Zapisz')


class AssignDocumentForm(FlaskForm):
    signature = StringField(
        'Oznaczenie',
        validators=[
            Regexp('^$|^\d+$',
                   message='Dozwolone są tylko cyfry lub puste pole.')
        ],
        description='Cyfra arabska lub puste pole'
    )
    type_id = SelectField('Typ', coerce=int,
                          validators=[InputRequired()])
    submit = SubmitField('Zapisz')


class EditShareDocumentForm(FlaskForm):
    description = StringField(
        'Opis',
        validators=[
            InputRequired(),
            Length(max=100)
        ],
        description='Maksymalnie 100 znaków.'
    )
    type_id = SelectField('Typ', coerce=int,
                          validators=[InputRequired()])
    user_id = SelectField('Widoczne dla', coerce=int,
                          validators=[InputRequired()])
    submit = SubmitField('Zapisz')
