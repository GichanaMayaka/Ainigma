from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_list(value):
    '''takes a text value and verifies that there is at least one comma '''
    values = value.split(',')
    if len(values) < 2:
        raise ValidationError(
            "The selected field requires an associated list of choices. Choices must contain more than one item.")


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    profile_picture = models.ImageField(upload_to='/images/', blank=True)

    def __str__(self):
        return str(self.user)


class Survey(models.Model):
    survey_name = models.CharField(max_length=400)
    survey_description = models.TextField()

    def __str__(self):
        return self.survey_name

    def questions(self):
        if self.pk:
            return Question.objects.filter(survey=self.pk)
        else:
            return None


class Category(models.Model):
    category_name = models.CharField(max_length=400)
    survey = models.ForeignKey(Survey)

    def __str__(self):
        return self.category_name


class Question(models.Model):
    TEXT = 'text'
    RADIO = 'radio'
    SELECT = 'select'
    SELECT_MULTIPLE = 'select-multiple'
    INTEGER = 'integer'

    QUESTION_TYPES = (
        (TEXT, 'text'),
        (RADIO, 'radio'),
        (SELECT, 'select'),
        (SELECT_MULTIPLE, 'Select Multiple'),
        (INTEGER, 'integer'),
    )

    question_text = models.TextField()
    required = models.BooleanField()
    category = models.ForeignKey(Category, blank=True, null=True, )
    survey = models.ForeignKey(Survey)
    question_type = models.CharField(max_length=200, choices=QUESTION_TYPES, default=TEXT)
    # the choices field is only used if the question type
    choices = models.TextField(blank=True, null=True,
                               help_text='if the question type is "radio," "select," or "select multiple" provide a '
                                         'comma-separated list of options for this question .')

    def save(self, *args, **kwargs):
        if self.question_type == Question.RADIO or self.question_type == Question.SELECT or self.question_type == Question.SELECT_MULTIPLE:
            validate_list(self.choices)
        super(Question, self).save(*args, **kwargs)

    def get_choices(self):
        ''' parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.'''
        return tuple([(choice.strip(), choice.strip()) for choice in self.choices.split(',')])

    def __str__(self):
        return self.question_text


class Response(models.Model):
    # a response object is just a collection of questions and answers with a
    # unique interview uuid
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey)
    comments = models.TextField('Additional Comments', blank=True, null=True)
    interview_uuid = models.CharField("Interview unique identifier", max_length=36)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "response {}".format(self.interview_uuid)


class AnswerBase(models.Model):
    question = models.ForeignKey(Question)
    response = models.ForeignKey(Response)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


# these type-specific answer models use a text field to allow for flexible
# field sizes depending on the actual question this answer corresponds to. any
# "required" attribute will be enforced by the form.
class AnswerText(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerRadio(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerSelect(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerSelectMultiple(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerInteger(AnswerBase):
    body = models.IntegerField(blank=True, null=True)
