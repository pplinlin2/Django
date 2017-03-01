# Django basics
## It worked
在開始學習之前讓我們把工具先都帶齊，工欲善其事，必先利其器。首先安裝Python Package Index(pip)，在安裝了pip之後，就可以輸入指令`pip install django`簡單的安裝django了！我們也先一步安裝一些之後會用到的工具，包括查看database的sqlite3、列出目錄結構的tree。
```console
# sudo apt-get install python-pip
# pip install django
# sudo apt-get install sqlite3 tree
```
使用`django-admin`來建立我們的django project，可以看到project目錄底下有個manage.py，這個是整個project的進入點，許多操作都必須要透過這隻程式來執行。
```console
# django-admin startproject learning_site
# tree learning_site/
learning_site/
├── learning_site
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py

1 directory, 5 files
```
首先，進到learning_site資料夾，之後所有的操作都會在以這個資料夾為root directory，修改learning_site/settings.py，把允許連線設定為全開，然後就可以透過`python manage.py runserver`來開啟django server，我們指定port為8000，所以可以通過瀏覽器輸入IP:8000進入網站，正確無誤的話可以看到「It worked!」出現
```python
# learning_site/settings.py
...
ALLOWED_HOSTS = ['*']
...
```
```console
# python manage.py runserver 0.0.0.0:8000
Performing system checks...

System check identified no issues (0 silenced).

You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

February 14, 2017 - 01:55:22
Django version 1.10.5, using settings 'learning_site.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```
在啟動django server時，出現一段紅字「You have 13 unapplied migrations(s)...」這段警告，這是什麼意思呢？migration是指我們把database的結構改變，因為結構改變，所以裡面的data也須要做相應的變更，下面幾種情況都是migration的例子:
* 要增加一個新的欄位
* 把一個已經存在的欄位改名
* 刪除欄位已經存在的欄位

所以我們先按「Ctrl + C」把django server終止，然後就像紅字裡面的提示輸入`python manage.py migrate`來變更database
```console
# python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying sessions.0001_initial... OK
```
雖然我們還沒有建立任何database，但是django預設會在project目錄底下建立一個database，名字叫做db.sqlite3，由名字可以知道這是一個SQLite database，通過指令`sqlite3 db.sqlite3 -line .tables`可以發現django幫我們建立許多預設的table，有好幾個跟authentication有關，之後都會一一介紹，再次執行`runserver`可以發現紅字警告就消失了！
## Views
接下來，我們建立learning_site/views.py，寫一個hello_world的function，這個function接收一個叫request的參數，代表從client端收到的請求，雖然我們目前用不到這個參數，但是所有的view都必須要接收這個參數，再來我們把要傳回給client端的資訊都交給HttpResponse，由hello_world返回。
```python
# learning_site/views.py
from django.http import HttpResponse

def hello_world(request):
    return HttpResponse('Hello world!')
```
寫好view後，還有一步要進行，就是我們必須給這個view一個URL地址，這樣才可以訪問的到這個view，所以須要修改learning_site/urls.py，將view與URL連結，url的第一個參數是一個regular expression，第二個參數是要連結的view
```python
# learning_site/urls.py
# 我們須要用到hello_world，因此將views import進來
from . import views

# 在urlpatterns中加入新的url
urlpatterns = [
    ...
    url(r'^$', views.hello_world), 
]
```
完成上面2步設定之後，用剛才學的`runserver`，打開瀏覽器輸入IP:8000就可以看到「Hello world!」出現在眼前了！
## Models
如果想把project當中的功能細切出來，則須要建立一個app，成為一個模組，這樣的話有幾個優點：
* 一個project可以有許多app，將不相依的功能分開，便於維護與開發
* app可以提供給別的project使用，可以快速開發相似的app，也可以避免重新開發相同的功能

我們用`python manage.py startapp`來建立一個新的app，完成後可以發現當前目錄下有一個course目錄
```console
# python manage.py startapp courses
# tree courses
course
├── admin.py
├── apps.py
├── __init__.py
├── migrations
│   └── __init__.py
├── models.py
├── tests.py
└── views.py

1 directory, 7 files
```
建立一個app後，必須將app加入project當中，方法是修改learning_site/setting.py
```python
# learning_site/setting.py
# 在INSTALLED_APPS的最後加入我們的app courses
INSTALLED_APPS = [
    ...
    'courses',
]
```
再來要建立一些class在database裡面，在django當中使用一種技術叫ORM來與database連繫，ORM代表「Object Relational Mapper」，ORM的原則如下:
* python中的每個class代表一個database中的table
* python class中的attribute代表database table裡的一個column

在知道了基本的原理後，開始構思一下model course須要哪一些attribute:
* created_at: 記錄course建的時間，可以自動記下輸入的時間
* title: course的標題，最多容納255個字
* description: course的介紹，不限字數

下方courses/models.py是規畫完成後的檔案，要成為table的class都要繼承models.Model，再針對不同的attribute使用models當中的DateTimeField、CharField、TextField進行設定，[連結](https://docs.djangoproject.com/en/1.8/ref/models/fields/)當中有介紹更多有關models中attribute類型的選項

```python
# courses/models.py
class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
```

由於我們變更了database的結構，所以須要執行`python manage.py makemigrations`來建立migration的更新檔，執行之後可以看到courses/migration資料夾下產生的檔案0001_initial.py就是更新檔，其實我們也可以自己寫更新檔定義自己的更新規則，但暫時不探討這個進階的話題，有興趣的讀者可以先自行研究一下。再來再下`python manage.py migrate`真正的更新database，
```console
# python manage.py makemigrations
Migrations for 'courses':
  courses/migrations/0001_initial.py:
    - Create model Course
# python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, courses, sessions
Running migrations:
  Applying courses.0001_initial... OK
# 
```
現在database已經更新了，但是database裡面沒有任何course，下一步要創造course來加入database，django提供的方法很多種，我們先學第一種，通過shell command來建立course，先執行`python manage.py shell`進入django shell！一開始因為還沒有加入任何course，所以`Course.object.all()`回傳了一個空的QuerySet，在`c.save()`這步之前，Course object僅存在於memory之中；這步之後，Python Basics就存在database裡了！再查詢一次，QuerySet中就有一個Course object，當然Course object這個名字實在不是很有意義，我們之後會再改善這個情況
```console
# python manage.py shell
>>> from courses.models import Course
>>> Course.objects.all()
<QuerySet []>
>>> 
>>> c = Course()
>>> c.title = "Python Basics"
>>> c.description = "Learn the basics of Python"
>>> c.save()
>>> Course.objects.all()
<QuerySet [<Course: Course object>]>
```
先不要離開django shell，上面花了好幾步來建立course，這次我們用另外一個型式，只要一步就可以建立course，完成後再查詢可以看到有2個Course object
```console
>>> Course(title="Python Collections", description="Learn about dict, list, and tuple").save()
>>> Course.objects.all()
<QuerySet [<Course: Course object>, <Course: Course object>]>
```
再學一個從django shell創立course的型式，這個方法的好處除了一步完成外，它會回傳剛建立的Course object，細微的差別，在寫django scripts有時會更加簡潔，完成後輸入`exit()`或是按「Ctrl + D」離開shell
```console
>>> Course.objects.create(title="Object-Oriented Python", description="Learn about Python's classes")
<Course: Course object>
>>> Course.objects.all()
<QuerySet [<Course: Course object>, <Course: Course object>, <Course: Course object>]>
>>> exit()
# 
```
接下來要進行剛有提到的改善，剛才`Course.object.all()`的回傳顯示一堆Course object，完全一樣無法分辨順序，於是我們修改courses/models.py，在class Course中覆寫function __str__，
```python
# courses/models.py
class Course(models.Model):
	...
    def __str__(self):
    	return self.title
```
再次執行django shell，可以看到所有的Course object都變成course的title了！剛才輸入的course全都有成功的建立！
```
# python manage.py shell
>>> from courses.models import Course
>>> Course.objects.all()
<QuerySet [<Course: Python Basics>, <Course: Python Collections>, <Course: Object-Oriented Python>]>
```
在為course model建立view之前，[連結](https://docs.djangoproject.com/en/1.8/topics/db/queries/#retrieving-objects)當中有更多關於建立、取得ORM的資訊，有興趣的讀者可以多多學習囉！

再來要學的是如何為app建立view，這個view當中要顯示剛剛創建的course，從`Course.objects.all()`取回所有course之後，用list comprehension得到output，用HttpResponse以純文字的方式顯示，
```python
# courses/views.py
from django.http import HttpResponse
from .models import Course

def course_list(request):
    courses = Course.objects.all()
    output = ", ".join([str(course) for course in courses])
    return HttpResponse(output)
```
同樣的，要修改urls.py，但除了要新增courses/urls.py之外，也要告訴原來的learning_site/urls.py須要授權給courses/urls.py，建立階層URL pattern，因為django不會自動去尋找app的urls.py，除非有在learning_site/urls.py寫好設定，完成後執行runserver，在瀏覽器中輸入IP:8000/courses就可以看到所有course的title囉！
```python
# courses/urls.py
from django.conf.urls import url 
from . import views

urlpatterns = [ 
    url(r'^$', views.course_list), 
]
```
```python
# learning_site/urls.py
from django.conf.urls import include

urlpatterns = [ 
    url(r'^courses/', include('courses.urls')), 
    ...
]
```
最後，如果不想要每次要新增course都要從django shell敲命令，那就一定要學django admin，先從learning_site/urls.py當中admin的url看出一點端倪，django提供了一個類似phpMyAdmin的圖形介面來管理ORM，讓我們不用繼續跟文字介面打交道，在開始之前，須要執行`python manage.py createsuperuser`建立superuser，帳密帳建好之後，在瀏覽器中輸入IP:8000/admin，用剛剛的帳密登入
```console
# python manage.py createsuperuser
Username: admin
Email address: admin@gmail.com
Password: ********
Password (again): ********
Superuser created successfully.
```
登入之後可以看到有2個django提供預設的model，分別是Groups和Users，點進Users可以看到剛創建的admin，再點進去可以看到許多細節，啊我們的course呢？其實只要做一點小修改，就可以讓course也同樣擁有好用的圖形管理介面，打開courses/admin.py
```python
# courses/admin.py
from .models import Course

admin.site.register(Course)
```
再登入IP:8000/admin，可以看到courses出現在面版上囉！點進去三個python course如期望的出現！再點進去可以看每個course的欄位，created_at和id這種自動生成的attribute因為不想被手動更改，所以也不會顯示出來，面版中有許多地方可以新增course，大家可以先碰碰玩玩囉！
## Templates
Template本質是html檔案，由一堆tag、attribute所組成，它從views接收了一些data，這些data是從models傳回來後經過整理的，然後把這些data根據我們寫的語法render到html裡面，再把render後的html回傳給使用者，這是一種server-side rendering。而把data render到html的工作是交由template engine來執行，template engine的目的也就是能以類python的語法處理views傳來的data，之後也會把django template engine的語法一一介紹給大家囉！

先在courses底下建立templates資料夾，在templates底下再建一個courses資料夾，看似有點冗長，但這麼做可以確保跟這個app有關的template都存在自己的資料夾底下，別人要拿去用、修改時，不用費心再去蒐集、搜尋相關的template，好啦！讓我們為course_list建一個檔案courses/templates/courses/course_list.html
```html
<!-- courses/templates/courses/course_list.html -->
{% for course in courses %}
<h2>{{ course.title }}</h2>
{{ course.description }}
{% endfor %}
```
再修改courses/view.py，我們將要return render，render的第一個參數是request、第二個是template的路徑、第三個是要傳給template的dictionary
```python
# courses/view.py
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})
```
再執行runserver，可以看到我們的第一個template啦！至於想要幫hello_world也做一個template的話，須要在root directory底下建一個templates資料夾，然後修改learning_site/settings.py裡的TEMPLATES，先解釋一些裡面的參數：
* BACKEND: 指定template engine
* DIRS: 指定額外的templates搜尋資料夾
* APP_DIRS: 是否要去各個app資料夾底下的templates裡找檔案

我們將templates加入DIRS即可
```python
# learning_site/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', 
        'DIRS': ['templates'], 
        'APP_DIRS': True, 
        ...
    },
]
```
然後建立templates/home.html幫hello world生成一個template，再修改learning_site/views.py的return，回傳正確的render，因為沒有data須要傳給template，所以第三個參數context預設為None，可以不填，更多關於render的選項可以參考[這裡](https://docs.djangoproject.com/en/1.8/topics/http/shortcuts/#render)
```html
<!-- templates/home.html -->
<h1>Welcome!</h1>
```
```python
# learning_site/views.py
from django.shortcuts import render

def hello_world(request):
    return render(request, 'home.html')
```
再來要講解template繼承的議題，同一個網站之中常會有相同的部份，例如: header、footer、側欄選單、…，如果能避免掉重覆複製、貼上同一段html，那當然是再好也不過了！讓我們先建立一個架構，編輯templates/layout.html，在想要客製化的區段加入`{% block %}{% endblock %}`的tag，並為block命名；再編輯templates/home.html，首先要用`{% extends %}`來繼承template，然後把客制化的內容加進block區段之中
```html
<!-- templates/layout.html -->
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}{% endblock %}</title>
</head>
  <body>{% block content %}{% endblock %}</body>
</html>
```
```html
<!-- templates/home.html -->
{% extends "layout.html" %}

{% block title %}Hello title{% endblock %}

{% block content %}
<h1>Welcome!</h1>
{% endblock %}
```
再介紹一個tag，這個tag可以讓我們在template當中使用靜態檔案，包括css、javascript或是圖檔，為了要能使用須要修改一些設定檔，這裡以使用下載回來的jquery.js為例，
* 先創建一個資料夾assets，底下建一個js資料夾，下載jquery的程式碼
* 編輯learning_site/settings.py最尾端，加入一段STATICFILES_DIRS告訴django去哪裡找這些static file
* 在learning_site/urls.py加入staticfiles_urlpatterns，目的是在debug模式中，會在URL中增加一個「/static」的路徑，指向assets資料夾
* 編輯templates/layout.html，引入jquery.js
* 最後編輯templates/home.html，就可以自由使用我們所引入的檔案了！
```console
# mkdir -p assets/js
# cd assets/js/
# wget https://code.jquery.com/jquery-3.1.1.min.js
```
```python
# learning_site/settings.py
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
```
```python
# earning_site/urls.py
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
...
urlpatterns += staticfiles_urlpatterns()
```
```html
<!-- templates/layout.html -->
{% load static from staticfiles %}
...
<head>
  <script src="{% static 'js/jquery-3.1.1.min.js' %}"></script>
</head>
```
```html
<!-- templates/home.html -->
{% block content %}
<h1>Welcome!</h1>
<script>
$("body").css({
  "margin": "0 auto",
  "width": "960",
  "background-color": "lightgray"
});
</script>
{% endblock %}
```
再來要看的是model與model之間的關係，例如一個course可以有好幾個step，要如何表現出這種關聯呢？先為step新增一個class，編輯learning_site/models.py，Step裡面有一欄course的類型的是ForeignKey，指向了table Course，所以形成了一個course可以擁有好幾個step的情況，通常稱為one-to-many relationship，
```python
# learning_site/models.py
class Step(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course)

    def __str__(self):
        return self.title
```
完成後記得migrate，然後把Step加入admin當中，再跑runserver，就可以新增Step了！當step一多，所有course的step都混在一起，實在很難分辨，其實只要再加一小段程式，就可以在admin中只修改屬於某個course的step，這種將小的表格隸屬於另外一個大表格的型式叫做inline，打開courses/admin.py，
* 為Step建立一個class StepInline，它繼承了StackedInline，另外一種常見的是TabularInline，前者會把內容分成好幾列，後者內容呈現為同一欄，比較壓縮、簡潔，大家可以自己換一換查看效果，套用合適的選項，記得要將model指定為Step
* 為Course建立CourseAdmin，將CourseAdmin和Course建立關聯的方法和Step不一樣，這是要特別注意的

[連結](https://docs.djangoproject.com/en/1.8/ref/contrib/admin/#inlinemodeladmin-objects)當中有更多關於inline的介紹，有興趣的朋友可以先看看了！
```python
# courses/admin.py
class StepInline(admin.StackedInline):
    model = Step

class CourseAdmin(admin.ModelAdmin):
    inlines = [StepInline, ]

admin.site.register(Course, CourseAdmin)
admin.site.register(Step)
```
再跑runserver，打開admin隨意打開一個course，step都列在下面，可以直接新增、刪除、更改屬於這個course的step，很方便吧！

在打開IP:8000/courses時，可以看到目前所有的course，這通常稱為list view，但我們想要點一個course時可以顯示出關於這個course的詳細資料，這被稱為detail view，list view已經完成了！繼續建構detail view吧！編輯courses/views.py，
```python
# courses/views.py
def course_detail(request, pk):
    course = Course.objects.get(pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})
```
course_detail除了接收request之外，還接收一個參數pk指定要查看哪一個course，這個pk是從courses/urls.py當中傳過來的
```python
# courses/urls.py
urlpatterns = [
    ...
    url(r'(?P<pk>\d+)/$', views.course_detail),
]
```
再來編寫courses/templates/courses/course_detail.html
```html
<!-- courses/templates/courses/course_detail.html -->
{% extends "layout.html" %}

{% block title %}{{ course.title }}{% endblock %}

{% block content %}
<article>
  <h2>{{ course.title }}</h2>
  {{ course.description }}
  <section>
  {% for  step in course.step_set.all %}
    <h3>{{ step.title }}</h3>
    {{ step.description }}
  {% endfor %}
  </sction>
</article>
{% endblock %}
```
其中step_set是由Foreign Key自動生成的QuerySet，我們要從QuerySet中取出所有的step，所以用all，注意在django template當中不能呼叫function，template engine會處理這件事，故不用all()而是用all，跑一下runserver，當我們輸入IP:8000/courses/1/就可以看到結果了！

在從ORM取出step時，希望step可以按照一定順序排列，而不是按輸入的順序，不然後來補進去的step就會打亂原本的順序，要解決這件事就要用model當中加入Meta，讓我們編輯courses/models.py
```python
# courses/models.py
class Step(models.Model):
    ...
    class Meta:
        ordering = ['order', ]
```
修改過後step就會按照order來排序了！如果在ordering = ['attr1', 'attr2', ]，則objects會先按attr1排列，如果attr1值相同再按attr2排列

到目前為止，都假設使用者會輸入正確的URL，假如使用者輸入IP:8000/courses/999/這種不存在的網址，django就會出現錯誤訊息500 Internal Server Error，但是我們期待出現的是404 Not Found，因為出錯原因是沒有這個course，所以修改courses/views.py來修正這個問題
```python
# courses/views.py
from django.shortcuts import get_object_or_404

def course_detail(request, pk):
#   course = Course.objects.get(pk=pk)
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})
```
再輸入一次錯誤URL就成功出現404頁面啦！
## Misc
我們的step到目前為止都還沒有內容，讓我們在step中新增一個content欄位，然後跑makemigrations
```python
# courses/models.py
class Step(models.Model):
    ...
    content = models.TextField()
    ...
```
```console
# python manage.py makemigrations
You are trying to add a non-nullable field 'content' to step without a default; we can't do that (the database needs something to populate existing rows).
Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
 2) Quit, and let me add a default in models.py
```
出現了上面的警告，什麼意思呢？意思是database當中已經有好幾筆資料，但是我們新增了一個沒有預設值的欄位，所以已經存在的data不知道該如何新增，按2跳出後繼續修改
* `blank=True`: 在admin中、別處新增object時該欄位可以留白
* `default=''`: 當該欄位沒有填時，提供一個預設值

完成之後就可以順利makemigrations、migrate了！
```python
# courses/models.py
class Step(models.Model):
    ...
    content = models.TextField(blank=True, default='')
    ...
```
最後我們為step新增detail的頁面，想必大家也有能力完成這件事了！可以自己試試看先啊~
```python
# courses/views.py
def step_detail(request, course_pk, step_pk):
    step = get_object_or_404(Step, course_id=course_pk, pk=step_pk)
    return render(request, 'courses/step_detail.html', {'step': step})
```
```python
# courses/urls.py
urlpatterns = [
    url(r'(?P<course_pk>\d+)/(?P<step_pk>\d+)/$', views.step_detail),
    ...
]
```
```html
<!-- courses/templates/courses/step_detail.html -->
{% extends "layout.html" %}

{% block title %}{{ step.title }} - {{ step.course.title }}{% endblock %}

{% block content %}
<article>
  <h2>{{ step.course.title }}</h2>
  <h3>{{ step.title }}</h3>
  {{ step.content|linebreaks }}
</article>
{% endblock %}
```
template的最後有一個linebreaks，這個tag可以把分行的內容分別形成一個段落，大家可以新增一個step輸入幾行內容，然後比較linebreaks的效果了！

還有一個要介紹的tag是url，網頁時常有許多連結連到不同的頁面，但是當網址變更的時候，就要調整這些URL，django有提供一個tag叫做url來解決這項問題，首先我們先為urls.py裡面的url加入name參數，為它們命名
```python
# courses/urls.py
urlpatterns = [
    url(r'^$', views.course_list, name='list'),
    url(r'(?P<course_pk>\d+)/(?P<step_pk>\d+)/$', views.step_detail, name='step'),
    url(r'(?P<pk>\d+)/$', views.course_detail, name='detail'),
]
```
就可以在template當中使用url tag，我們打原來的標題都加進超連結，下面修改完後、跑runserver可以看到超連結生效了！
```html
<!-- courses/templates/courses/course_list.html -->
{% for course in courses %}
<h2>
  <a href="{% url 'detail' pk=course.pk %}">
    {{ course.title }}
  </a>
</h2>
{{ course.description }}
{% endfor %}
```
```html
<!-- courses/templates/courses/course_detail.html -->
<h3>
  <a href="{% url 'step' course_pk=step.course.pk step_pk=step.pk %}">
    {{ step.title }}
  </a>
</h3>
```
```html
<!-- courses/templates/courses/step_detail.html -->
<h2>
  <a href="{% url 'detail' pk=step.course.pk %}">
    {{ step.course.title }}
  </a>
</h2>
```
再處理一個跟超連結有關的議題，就是剛才我們在為URL命名時，用了list、detail這種很容易重覆的名字，於是須要使用namespace來區隔不同app下的重覆命名
```python
# learning_site/urls.py
urlpatterns = [
    url(r'^courses/', include('courses.urls', namespace='courses')),
    ...
]
```
加入了namespace後，須要調整剛剛所有使用了url tag的地方
```html
<!-- courses/templates/courses/course_list.html -->
<a href="{% url 'courses:detail' pk=course.pk %}">
```
```html
<!-- courses/templates/courses/course_detail.html -->
<a href="{% url 'courses:step' course_pk=step.course.pk step_pk=step.pk %}">
```
```html
<!-- courses/templates/courses/step_detail.html -->
<a href="{% url 'courses:detail' pk=step.course.pk %}">
```
所有功能依舊正常運作
## Tests
再來要進行的是test，什麼是test呢？例如:原本有5個test function分別驗證了5項功能，今天我改了一段程式碼，只要再跑這些test function而且通過，就可以代表我沒有不小心破壞到原有的功能，確保了程式碼的品質，

django原本就預備了test檔案，打開courses/test.py吧！所有testcase都要繼承TestCase，裡面每一個function都是一個測試項目，必須以test開頭命名，第一步我們來測試model，想要確定每一個object被創造出來的時間一定會 < 現在的時間
```python
# courses/tests.py
from .models import Course
from django.utils import timezone

class CourseModelTests(TestCase):
    def test_course_creation(self):
        course = Course.objects.create(
            title="Python Regular Expression",
            description="Learn to write regular expression in Python"
        )
        now = timezone.now()
        self.assertLess(course.created_at, now)
```
```console
# python manage.py test
Creating test database for alias 'default'...
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```
Pass！多寫幾項測試後會發現，每一項測試開始之前，我們都須要建立一個或一些course來供測試，這項工作似乎很重覆，於是test framework提供了一個setUp function，可以將這個class的初始化工作寫到這個function裡面，

第二步來測試view，測試view時，為了連同url一同測試，須要import reverse，藉由reverse我們可以得到url namepspace和url name相對應的view，而在測試時要使用一個函式叫self.client，它有點像一個瀏覽器，接收request，回傳response包含了下面列的一些狀態、結果
* status_code: HTTP的回傳狀態，200、404、500、…
* context: view裡面render第三個參數的dictionary

在這裡我們測試course list是否有回傳200OK，以及在setUp裡面新增的2個course，有沒有正確接收到
* 測試list view時，會得到一個course的list，所以用assertIn來確保新增的course有在list裡面
* 測試detail view時，會收到一個單獨的course，所以用assertEqual來確保輸出和輸入相同
```python
# courses/tests.py
class CourseViewsTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Python Testing",
            description="Learn to write tests in Python"
        )
        self.course2 = Course.objects.create(
            title="New Course",
            description="A new course"
        )

    def test_course_list_view(self):
        resp = self.client.get(reverse('courses:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.course, resp.context['courses'])
        self.assertIn(self.course2, resp.context['courses'])

    def test_course_detail_view(self):
        resp = self.client.get(reverse('courses:detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.course, resp.context['course'])
```
Pass！最後來測試template
* 用assertTemplateUsed來確保response有使用某個html檔
* 用assertContains來確保response裡面有某個字串
```python
# courses/tests.py
class CourseViewsTest(TestCase):
    ...
    def test_course_list_view(self):
        ...
        self.assertTemplateUsed(resp, 'courses/course_list.html')
        self.assertContains(resp, self.course.title)
```
先寫測試再寫程式，這種寫程式的流程稱為TDD，Test Driven Development。不管是先寫測試、還是寫完程式後再寫測試，經過我們可以充分測試，進一步完善我們的程式，也讓我們對自己的程式有更強的信心。
## Epilogue
經過一整章的介紹，大家已經可以搭建一個前後台功能兼俱、功能齊全的網站了！沒有像想像中的困難吧！接下來，每一章我們都會再針對一個主題做更深入的探討！繼續加油囉！
