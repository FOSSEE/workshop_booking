from django.db import models


# Create your models here.

class Nav(models.Model):
    name = models.CharField(max=20)
    link = models.CharField(max=20)
    position = models.IntegerField()

    def __str__(self):
        return self.name


class SubNav(models.Model):
    nav = models.ForeignKey(Nav, on_delete=models.CASCADE)
    name = models.CharField(max=20)
    link = models.CharField(max=100)
    position = models.IntegerField()

    def __str__(self):
        return self.name


class Page(models.Model):
    permalink = models.CharField(max=100, unique=True)
    title = models.CharField(max=50)
    imports = models.TextField(help_text='External imports like css,js files, will be placed in <head> tag (already '
                                         'includes bootstrap4 and jQuery)')
    content = models.TextField(help_text='Body of the page')
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.title


class StaticFiles(models.Model):
    filename = models.CharField(max=70, unique=True)
    file = models.FileField(upload_to='static/{}'.format(filename), blank=False,
                            help_text='Please upload static files (images, css, js, etc) one by one')

    def __str__(self):
        return self.filename
