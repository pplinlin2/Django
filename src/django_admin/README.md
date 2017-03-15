# Customizing Django Admin
## Using the Django Admin
在django basics章節之中，我們已經學了一點關於django admin的使用，相信大家在自己的projects當中也有用到這項功能，這裡還想要告訴大家的是，其實django admin提供了很多客製化的空間，原始django admin提供的工具已經很不錯了！不過我們可以根據自己的須求來加強功能，像是:
* 根據某些欄位來排序讓表格看起來更合理
* 自訂搜尋欄位，讓人工找資料更便利
* 關閉delete功能、…

在開始之前先把實驗環境建立好囉！相信大家都很熟悉了！但再快速復習一下
```shell
django-admin startproject learning_site
cd learning_site/
python manage.py startapp courses
# 複製course/models.py
# 複製course/admin.py
# 修改learning_site/settings.py，將courses加入INSTALLED_APPS
python manage.py makemigrations
python manage.py migrate
python manage.py createsuper
python manage.py loaddata fixtures.json
```
讓我們先開始做一點小小的修改，還記得每一次登入django admin之後，左上角都會出現Django administration標題嘛？如果能顯示我們project的名字，那就更棒了！而且只要一點小修改就可以做到
```python
# courses/admin.py

admin.site.site_header = "Learning Site Admin"
```
有的時候我們邊思考邊把fields加入model當中，並沒有特別在意順序，django和django admin也不會針對fields進行特別的排序，django admin只會把最先加入的field顯示在最上方，有的時候就可能不是我們想要的效果，這裡就來介紹如何讓django來排序fields，讓表格顯示起來更有邏輯性，方法就是在ModelAdmin當中加入fields這個欄位，它是一個list，在list當中按我們想要的順序填入fields的名字，
```python
# courses/admin.py
class QuizAdmin(admin.ModelAdmin):
    fields = ['course', 'title', 'description', 'order', 'total_questions']

# 記得要註冊新加入的Admin
admin.site.register(models.Quiz, QuizAdmin)
```
[這裡](https://docs.djangoproject.com/en/1.9/intro/tutorial07/#customize-the-admin-form)有更多關於客製化admin表格的細節
## Customizing the List View
前面我們介紹了一些django admin的基本功能，現在來看看更細節的部份，django admin主要可以分為兩個部份，list view和detail view
* list view: 可以看到某一項model中所有的物件列表，例如: 我們可以點Courses看到所有database中課程的列表
* detail view: 可以點進某一個物件，看關於這個物件所有的細節，修改detail view就會更新到database當中

現在來想像一個list view應用情況，當database中的物件一多時，例如: 數百門課程、上千個問題時、…，很難一眼看到想要的資訊，幫list view加入搜尋功能就變得很有必要，這其實很簡單，只要在ModelAdmin class中加入search_fields就可以了！search_fields是一個list，放入想要被搜尋的欄位
```python
# courses/admin.py
class CourseAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']
    
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['prompt']
```
打開瀏覽器輸入`IP:8000/admin/courses/course/`就可以看到有一個search bar出現在上方，試著輸入Ruby、Python看看結果了！另外一項有點類似的功能是filter，可以在頁面右邊列出過濾條件，這些條件可以相互組合，例如: 在created_at選擇This year、在is_live選擇Yes，就可以得到今年建立而且已經上架的課程
```python
# courses/admin.py
class CourseAdmin(admin.ModelAdmin):
    list_filter = ['created_at', 'is_live']
```
有關於list_filter的詳細資訊可以看[這裡](https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter)

前面介紹的search_fields和list_filter讓我們更容易找到想要的物件，但是有的時候預設的filter似乎會不符合我們的須要，例如: created_at的filter可以讓我們根據時間選擇課程，但是最遠最遠就到今年，如果我想要搜尋2015年、2016年的課程呢？那就須要自訂filter了！
```python
# courses/admin.py
class YearListFilter(admin.SimpleListFilter):
    title = 'year created'  # by
    parameter_name = 'year' # url

    def lookups(self, request, model_admin):
        return (
            ('2015', '2015'),
            ('2016', '2016'),
        )# (url, side bar)

    def queryset(self, request, queryset):
        if self.value() in ['2015', '2016']:
            year = int(self.value())
            return queryset.filter(
                created_at__gte=date(year, 1, 1),
                created_at__lte=date(year, 12, 31)
            )
```

在預設的list view當中，我們可以看到所有課程的課名，這是因為我們在models.py當中有覆寫str函式，不然list view只會顯示Course object，也僅僅看到course title，但是能夠看到更多的fields對我們管理database更有幫助
* 可以有更多欄位來排序
* 可以一次看到更多細節
* 不用到detail view才看到所有資訊，可以將重要的資訊放在list view
```python
# courses/admin.py
class CourseAdmin(admin.ModelAdmin):
    ...
    list_display = ['title', 'created_at', 'is_live']
```
為list view增加欄位非常的簡單吧！

接下來要講解的是為list view新增我們自訂的欄位，
```python
# courses/models.py
class Course(models.Model):
    ...
    def time_to_complete(self):
        minutes = int(len(self.description.split())/20)
        return '{} min.'.format(minutes)
```
```python
# courses/admin.py
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_live', 'time_to_complete']
```
最後一個關於list view的主題，我們要達成一個目標，直接在list view裡面對物件進行編輯，不用再點進detail view裡面去，只為了更改一小部份資料，或許你以為要做這麼大幅度的改動須要修改很多地方，但其實django很多時候都可以輕易的做到客製化，將欄位名稱加入list_editable就可以了！加入list_editable的欄位必須先是在list_display當中，畢竟要先看得到才有辦法編輯囉！
```python
# courses/admin.py
class CourseAdmin(admin.ModelAdmin):
    list_editable = ['is_live']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'quiz', 'order']
    list_editable = ['quiz', 'order']
```
不難吧！下一步要思考的就是什麼欄位應該出現在list view？另外一個角度來看就是，什麼欄位適合繼續待在detail view？如果可以一眼看完並做更動的欄位，像是is_live，就可以放在list view；而description就太長而應該放在detail view。
## Customizing the Detail View
上一章我們介紹了list view，接下來要看的是detail view，大部份對物件的修改都是在這裡進行的，雖然也可以在list view修改物件，django已經可以自動化的將欄位顯示給我們，但有時候並不是最佳的格式，例如: 將選項一列一列顯示並不比一欄一欄好、或者我們想把相關的欄位顯示在一起、…，這些改動可以讓網站的管理更容易，也同時減少的出錯的機會，

這裡我們把Text的course、title、order、description四個欄位組在一起，另外一個content欄位自成一組，群組命名為Add content，並預設不顯示，要點擊才會展開
```python
# courses/admin.py
class TextAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'order', 'description')
        }), ('Add content', {
            'fields': ('content', ),
            'classes': ('collapse', ),
        }),
    )

admin.site.register(models.Text, TextAdmin)
```

現在已經學了怎麼把fields合成群組！再來看看更改一些外觀，看看如何把下拉式選單變成單選按鈕，這很適合當選項範圍確定，只有幾項、不會增長時，而且如果有把欄位加入list_display的話，這個修改在list view也會有效果
```python
# courses/admin.py
class QuestionAdmin(admin.ModelAdmin):
    ...
    radio_fields = {'quiz': admin.HORIZONTAL}
```
並把一列一列的欄位改成一欄一欄顯示，述語就是從stacked inline改成tabular inline，修改也只要把原本的admin.StackedInline改成admin.TabularInline
```python
# courses/admin.py
class AnswerInline(admin.TabularInline):
    ...
```

最後一項任務，讓我們為course增加status欄位，可以知道課程的狀態，是還在編寫、還在審察、還是已經上架了！這樣我們須要一樣操作可以來更新status和is_live欄位，
```python
# courses/models.py
class Course(models.Model):
    STATUS_CHOICES = (
        ('i', 'In Progress'),
        ('r', 'In Review'),
        ('p', 'Published'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='i')
```
目前action裡面只有一個「Delete selected courses」，我們增加一個action來把被選的course標記為Published
```python
# courses/admin.py
def make_published(modeladmin, request, queryset):
    queryset.update(status='p', is_live=True)

make_published.short_description = "Mark selected courses as Published"

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_live', 'time_to_complete', 'status']
    list_editable = ['status']
    actions = [make_published]
```
如果想要移除「Delete selected courses」防止誤刪的話，要再加上一行
```python
# courses/admin.py
admin.site.disable_action('delete_selected')
```
更改完後，從course的list view勾選課程，然後從Action選「Mark selected courses as Published」，按旁邊的「Go」，就可以更新status和is_live了！記得不是按下方的「Save」，按「Save」不會有任何效果的，這樣就達到客製化action的功能啦！更多有關action的介紹可以看[這裡](https://docs.djangoproject.com/en/1.9/ref/contrib/admin/actions/)
## Epilogue
到了這裡，大家已經見識過很多關於django admin的技巧了！相信也收獲不少，我們完成了搜尋、過濾、增加欄位等…很多功能，其實django admin的世界是很自由的，還有許多可以自訂的功能等待大家慢慢發掘囉！
