# Django ORM
## Basic ORM Usage
先復習一下我們是如何使用django ORM
* 當要取得所有的course，使用`Course.objects.all()`
* 當只想要取得course的QuerySet，使用`Course.objects.none()`
* 當取得某個course，使用`Course.objects.get(pk=...)`
* 當不確定某個object是否存在，使用`get_object_or_404`
而所謂的QuerySet其實就是從資料庫裡傳回來的查詢，存在記憶體當中，在開始之前，我們先建立course的環境和所使用的course model，相信下面的步驟各位也可以自行完成，在這裡幫大家再做一次，忘記的話可以回django basics章節再複習一下囉！
```console
# django-admin startproject learning_site
# cd learning_site/
# python manage.py startapp courses
```
```python
# learning_site/settings.py
...
ALLOWED_HOSTS = ['*']
...
INSTALLED_APPS = [
    ...
    'courses', 
]
```
```python
# courses/models.py
from django.contrib.auth.models import User

class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(User)
    subject = models.CharField(default='', max_length=100)

    def __str__(self):
        return self.title
```
```console
# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
Username (leave blank to use 'qvs'): admin
Email address: admin@gmail.com
Password:
Password (again):
Superuser created successfully.
```
建立了database後，須要再建立一些course object，為了免除輸入、輸出之苦，django提供了loaddata和dumpdata命令，讓我們可以將database裡的資料輸出成稱為fixture file的文字檔，也可以把fixture file輸入成database
* `python manage.py loaddata <fixture file>`: 把已經初始化好的檔案直接輸入進database
* `python manage.py dumpdata [app|model]`: 將database裡的資料輸出

```console
# python manage.py loaddata fixtures.json
Installed 20 object(s) from 1 fixture(s)
```
在完成database建立後，開始介紹一些ORM的基本功能。當我們存一些object到database之後，大部份的情況只會想要再取一些有興趣的資料出來，例如:如果你打開冰箱，只能取出一樣、或所有東西，相信這種冰箱也不會有人買吧！所以這裡要介紹的是filter，通過filter可以限制範圍、取出想要的資料。如果想要拿到由admin所開的課時，先看看不用filter，如何達到過濾的效果
```python
# courses/orm.py
from courses import models
teacher_name = 'admin'
# 使用filter之前
teacher = models.User.objects.get(username=teacher_name)
courses = teacher.course_set.all()
print courses
```
```python
>>> execfile('courses/orm.py')
<QuerySet [<Course: Python Basics>, <Course: Python Collections>, <Course: Object-Oriented Python>, <Course: Python Testing>]>
```
接下來介紹filter的使用方法:
```python
Model.objects.filter(attribute__condition=value)
```
這是filter的基本型式，condition可以有兩種型式: related model和field lookups，先介紹related model
* related model: 官網說明在[這裡](https://docs.djangoproject.com/en/1.9/topics/db/queries/#lookups-that-span-relationships)，例如:手機Phone有ForeignKey製造商manufactor，而製造商Manufactor有attribute公司名字name，要找出蘋果的手機可以查詢`Phone.objects.filter(manufactor__name="Apple")`來得到結果

這裡我們用filter來獲得與之前相同的結果，但型式可以簡潔許多，
```python
# courses/orm.py
from courses import models
teacher_name = 'admin'
# 使用filter之後
courses = models.Course.objects.filter(teacher__username=teacher_name)
print courses
```
再來介紹第二種condition型式
* field lookups: 官網說明在[這裡](https://docs.djangoproject.com/en/1.9/topics/db/queries/#field-lookups)，常見的選項有大於等於gte、小於等於lte、搜尋字串的icontains(i代表case-insensitive，不管大小寫)

這裡藉由filter找含有某關鍵字的course，來展示field lookups中icontains的效果
```python
# courses/orm.py
from courses import models
key_word = 'obj'
courses = models.Course.objects.filter(title__icontains=key_word)
print courses
```
```python
>>> execfile('courses/orm.py')
<QuerySet [<Course: Object-Oriented Python>, <Course: Java Objects>]>
```
另外一個使用了filter的意外效果是，當teacher_name不存在於database的時，不須要使用get_object_or_404來防範，filter會直接回傳空的QuerySet。更多filter的詳細說明請參考[連結](https://docs.djangoproject.com/en/1.9/topics/db/queries/#retrieving-specific-objects-with-filters)

再來介紹一個相反的功能: exclude，exclude排除所有符合條件的object，exclude的用法和filter一模一樣
filter的使用方法:
```python
Model.objects.exclude(attribute__condition=value)
```
```python
# courses/orm.py
from courses import models
key_word = 'obj'
courses = models.Course.objects.exclude(subject__in=['Python', 'Java'])
print courses
```
```python
>>> execfile('courses/orm.py')
<QuerySet [<Course: Build a Simple Android App>, <Course: Android Activity Lifecycle>, <Course: SQL Basics>, <Course: Modifying Data with SQL>, <Course: jQuery Basics>, <Course: Build a Simple Dynamic Site with Node.js>, <Course: Build a Basic PHP Website>]>
```
接下來要介紹update，update讓我們可以更新QuerySet，先在course model當中增加一個published欄位，代表這門課程是否已經發佈了，記得更改完要跑`makemigrations`和`migrate`
```python
# courses/models.py
class Course(models.Model):
    ...
    published = models.BooleanField(default=False)
```
更新完後列出所有已經發佈的課程，如我們所預期，得到一個空的QuerySet
```python
# courses/orm.py
from courses import models
courses = models.Course.objects.filter(published=True)
print courses
```
```python
>>> execfile('courses/orm.py')
<QuerySet []>
```
先看看不用update如何達到更新的效果
```python
# courses/orm.py
from courses.models import Course
courses = Course.objects.all()
course = courses[0]
course.published = True
course.save()
print Course.objects.filter(published=True)
```
再看看如何用update來執行更新，下面將所有課程的published更新為True，
```python
>>> from courses.models import Course
>>> Course.objects.update(published=False)
15
>>> print Course.objects.filter(published=True)
<QuerySet []>
```
update其實是對QuerySet進行操作，上面程式碼中的update之前省略了一個all，也就是說下列兩行是等價的，既然是對QuerySet進行操作，我們同樣可以在執行update之前先用filter、exclude來選擇要update的對象，這樣子比前面取出所有的record然後對每一項執行save快速、簡潔不少
```python
Course.objects.all().update(published=True)
Course.objects.update(published=True)
```
我們可以對QuerySet進行delete操作，同樣的我們可以一項一項取出來然後刪除，但是對QuerySet執行delete顯然是更好的作法，下面示範刪除科目裡面有關鍵字php的課程
```python
>>> php_courses = Course.objects.filter(subject__icontains='php')
>>> print php_courses
<QuerySet [<Course: Build a Basic PHP Website>]>
>>> php_courses.delete()
(1, {u'courses.Course': 1})
>>>
>>> Course.objects.filter(subject__icontains='php')
<QuerySet []>
```
更多有關update的資料可以參考[這裡](https://docs.djangoproject.com/en/1.9/topics/db/queries/#updating-multiple-objects-at-once)，有關delete的資料可以看[這裡](https://docs.djangoproject.com/en/1.9/topics/db/queries/#deleting-objects)

在django basics章節中，我們已經介紹了好幾種新增object的方法，包括:從django shell新增、從django admin新增、…，這裡會提到三種常見ORM新增object的方法:create、bulk_create、get_or_create，先看看之前是如何在django shell當中使用create新增course的，
```python
from django.contrib.auth.models import User
teacher = User.objects.get(username='admin')
course = Course.objects.create(teacher=teacher, subject='Python', title='Django Basics')
course.id
```
如果我們要同時新增好幾項課程，當然可以寫個loop，或是分好幾行、每行create一項object，但django提供了我們bulk_create，可以同時新增多項object，直接看下去囉！
```python
Course.objects.bulk_create([
    Course(teacher=teacher, title='Django Forms', subject='Python'), 
    Course(teacher=teacher, title='Django ORM', subject='Python'),
])
```
```python
>>> Course.objects.filter(title__icontains='django')
<QuerySet [<Course: Customizing Django Templates>, <Course: Django Basics>, <Course: Django Forms>, <Course: Django ORM>]>
```
剛才新增的object都成功進入database啦！而且使用bulk_create只會產生一個SQL query，增進了不少效能，同時，我們也想要避免把沒必要的object加入database中，像是以前學的get_object_or_404可以避免取到無效的object，get_or_create可以幫忙檢查attribute是否有重覆，正確才會新增，並回傳一個boolean值告訴使用者是否有新增object，
```python
course, created = Course.objects.get_or_create(title='course1')
# 如果不須要用到created參數，可以用下底線(_)替代
course, _ = Course.objects.get_or_create(title='course2')
```
下面示範新增兩門課程，一項有重覆、一項是全新的
* 新增Django Forms回傳False，代表database裡已經這項object
* 新增Django REST Framework回傳True，代表成功新增object
```python
>>> Course.objects.get_or_create(teacher=teacher, title='Django Forms', subject='Python')
(<Course: Django Forms>, False)
>>> Course.objects.get_or_create(teacher=teacher, title='Django REST Framework', subject='Python')
(<Course: Django REST Framework>, True)
```
有的時候我們並不須要把整個object都從database裡面撈出來，只想要得到object當中的一部份資訊，例如:有一堆人來參加派對，我們只須要知道每個人的名字就可以了！這種情況可以使用values，在values中代入想要獲得的參數名，回傳時就可以僅得到須要的參數，這裡展示一下只想得到科目為Java課程的名字和id
```python
>>> Course.objects.filter(subject='Java').values('id', 'title')
<QuerySet [{'id': 18, 'title': u'Java Basics'}, {'id': 19, 'title': u'Java Objects'}, {'id': 20, 'title': u'Java Data Structures'}]>
```
而value_list類似於values，但回傳的是tuple而非dictionary，在某些情況下會更適合，這裡就不多著墨了，更多有關values的資料可以參考[這裡](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#values)，關於value_list可以看[這裡](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#values-list)

再展示一項功能，有關時間的操作:datetimes，第二個參數可以指定精細到哪一種程度，例如:指定'year'，則月份、日期都可能不會是正確的數字
```python
>>> dates = Course.objects.datetimes('created_at', 'year')
>>> dates
<QuerySet [datetime.date(2015, 1, 1), datetime.date(2016, 1, 1), datetime.date(2017, 1, 1)]>
>>>
>>> dates = Course.objects.datetimes('created_at', 'month')
>>> dates
<QuerySet [datetime.datetime(2015, 6, 1, 0, 0, tzinfo=<UTC>), datetime.datetime(2016, 1, 1, 0, 0, tzinfo=<UTC>), datetime.datetime(2017, 3, 1, 0, 0, tzinfo=<UTC>)]>
>>> dates = Course.objects.datetimes('created_at', 'day')
>>>
>>> dates
<QuerySet [datetime.datetime(2015, 6, 1, 0, 0, tzinfo=<UTC>), datetime.datetime(2016, 1, 19, 0, 0, tzinfo=<UTC>), datetime.datetime(2017, 3, 2, 0, 0, tzinfo=<UTC>)]>
```
有關datetimes的詳細介紹可以看[這裡](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#datetimes)

最後要介紹的是order_by，可以對從database取出來的object進行排序，不然預設會按照id由小排到大，order_by裡要加的參數是:想要做為排序依據的欄位，預設是遞增，如果想要遞減，要在欄位前加減號(-)，這裡展示把所有的course依create_at由大到小排列，也就是最新的課程排前面
```python
>>> Course.objects.all().order_by('-created_at').values('id', 'title')[:3]
<QuerySet [{'id': 25, 'title': u'Django REST Framework'}, {'id': 24, 'title': u'Django ORM'}, {'id': 23, 'title': u'Django Forms'}]>
```
有關order_by的詳細介紹可以看[這裡](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#order-by)
## Total Control
經過前段的講解，對於ORM我們有了一定的認識，在這個基礎之上，繼續看有哪一些工具可以幫助我們在下query時可以更有效率、更簡潔囉！

F object是一項當想要realtime存取database時的重要工具，因為F object可以直接存取database裡面的record，而非在memory中的資料，使用了F object之後，如果要使用更新後的值，記得要下refresh_from_db來更新記憶體中的資料
```python
# courses/models.py
class Like(models.Model):
    total = models.IntegerField(default=0)

    def __str__(self):
        return str(self.total)
```
跑了`migrate`後開啟django shell來試試看
```python
from django.db.models import F
from courses.models import Like
like = Like.objects.create()

# 對一個object操作F object
like.total = F("total") + 1
like.save()
like.refresh_from_db()
like.total

# 對一個QuerySet操作F object
Like.objects.all().update(total = F("total") + 1)
like.refresh_from_db()
like.total
```
更多關於F object的資料可以參考[這裡](https://docs.djangoproject.com/en/1.9/ref/models/expressions/#f-expressions)

filter和exclude可以達到選擇所要的record或是排除不要的record，但有的時候我們須要更複雜的邏輯，例如:AND或是OR，這時就可以使用Q object了！這個範例中我們想要搜尋已經發佈的，而且title中有關鍵字或description中有關鍵字的課程
```python
# courses/orm.py
from courses.models import Course
from django.db.models import Q
key_word = 'app'
courses = Course.objects.filter(
    Q(published=True), 
    Q(title__icontains=key_word)| 
    Q(description__icontains=key_word)
)
print courses
```
更多的有關Q object的資料可以參考[這裡](https://docs.djangoproject.com/en/1.9/topics/db/queries/#complex-lookups-with-q-objects)，有了Q object不代表我們須要建造自己的搜尋引擎，有很多好的開源軟體像是elasticsearch可以使用。

有的時候我們須要為QuerySet當中每一個object添加統計資訊，例如:每一部影片有好幾個給分評價，我想要知道每一部影片的平均得分是多少，或是全部影片的平均得分是幾分，這樣子就要用到兩項新工具了！前項要用annotate、後項要用aggregate！
```python
# courses/orm.py
from django.db.models import Count
from django.contrib.auth.models import User
# 查看每位老師開了多少門課
teachers = User.objects.annotate(Count('course'))
[t.course__count for t in teachers]
# 查看所有老師總共開了幾門課
User.objects.aggregate(Count('course'))
```
結果如下
```python
>>> teachers = User.objects.annotate(Count('course'))
>>> [t.course__count for t in teachers]
[8, 0, 2, 4, 3, 1]
>>> User.objects.aggregate(Count('course'))
{'course__count': 18}
```
更多關於annotate和aggregate可以參考[這裡](https://docs.djangoproject.com/en/1.9/topics/db/aggregation/)

最後題兩個跟效能有關的函式，分別是select_related和prefetch_related，功能都是預先載入record
* 當有Foreign指向別的model時，用select_related將別的model預先載入
* 當別的model有Foreign指來時，用prefetch_related將來源model預先載入
```python
# courses/orm.py
from django.contrib.auth.models import User
from courses.models import Course

courses = Course.objects.select_related('teacher').all()
teachers = User.objects.prefetch_related('course_set').all()
```
* 當course須要用到teacher時，可以使用select_related來將項目先載入
* 當teacher須要用到course時，可以使用prefetch_related來將項目先載入

這樣先將所須項目先載入，雖然增加了當次查詢的負擔，但是如果有正確的預載入，也就是說先載入的項目後來有用到，那麼這次預載入就達到節省時間的效果了！這裡有[select_related](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#select-related)和[prefetch_related](https://docs.djangoproject.com/en/1.9/ref/models/querysets/#prefetch-related)的相關資料
## Epilogue
經過一整章的介紹之後，想必大家對於ORM的操作更加熟悉了！有些功具雖然暫時用不到，但知道這些工具的存在，大概知道這些功具的用途，哪一天須要的時候，再詳細查看它的文件，瞭解使用的細節，可以寫出更簡潔、更高效的ORM指令囉！
