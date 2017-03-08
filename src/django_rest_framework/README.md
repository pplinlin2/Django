# Django REST Framework
## RESTful Django
Django REST Framework簡稱DRF，是一個強大、有彈性、構建於django之上的框架，DRF被用來建造RESTful API，DRF提供了許多工具，讓我們更容易寫Web API，當然我們可以不用DRF而直接使用django來寫Web API，但就喪失了許多DRF提供給我們的便利性，DRF提供了Hyperlink-relation、pagination、throttling、token-base authentication、…等很多功能，這些主題都會一一介紹，讓我們先安裝DRF、建立course的環境和所使用的course model囉！
```console
# pip install djangorestframework
Collecting djangorestframework
  Downloading djangorestframework-3.5.4-py2.py3-none-any.whl (709kB)
    100% |████████████████████████████████| 716kB 1.2MB/s
Installing collected packages: djangorestframework
Successfully installed djangorestframework-3.5.3
```
開啟設定檔ed_reviews/settings.py，將rest_framework加入app，並在最底端加入幾項設定，
* authentication是辨認連線的人是誰？是使用者A？是使用者B？可以參考[這裡](http://www.django-rest-framework.org/api-guide/authentication/)
* permission則是管理哪個使用者可以做什麼事？使用者A能做什麼事？使用者B不能做什麼事？IsAuthenticatedOrReadOnly代表經過authenticated的用戶可以create、edit、delete record，其餘的人只能看到這些資料，可以參考[這裡](http://www.django-rest-framework.org/api-guide/permissions/)
```python
# ed_reviews/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
]

...
# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ), 
}
```
```python
# ed_reviews/urls.py
from django.conf.urls import include

urlpatterns = [
    ...
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
]
```
完成後執行`createsuperuser`，在瀏覽器輸入IP:8000/api-auth/login就可以看到登入畫面了！輸入使用者帳密後，會看到The current URL didn't match any of these.的錯誤訊息，原因是我們還沒有建立profile的頁面，但我們已經完成登入了！

Serializer是DRF強大的功能之一，它可以將django model轉換為方便閱讀及管理的JSON，JSON的全名是JavaScript Object Notation，是一種輕量級的資料交換語言，讓人和電腦都可以方便閱讀，很適合作為網路連線時交換資料的媒介，Serializer也可以將JSON轉換回django model，和django form一樣，DRF Serializer可以自動從model生成欄位，也有create、update database的能力，這是我們要使用的model，完成後記得把fixtures.json載入進來
```python
# courses/models.py
...
class Course(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    
    def __str__(self):
        return self.title


class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    comment = models.TextField(blank=True, default='')
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['email', 'course']
    
    def __str__(self):
        return '{0.rating} by {0.email} for {0.course}'.format(self)
```
要使用DRF Serializer，首先，要建立一個檔案serializers.py，可以預期的裡面會有好幾個serializer，正如models.py裡面會有一些model，在meta裡面我們指定了serializer所對應的model，並且用field指定須要被serialize的欄位，由於我們不太想讓所有人可以輕易得到別人的email，但是又不能把這個欄位去除掉，因為在建立Review時還是須要填寫這個欄位，所以把email指定為write only
```python
# courses/serializers.py
from rest_framework import serailizer
from . import models

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
    	extra_kwargs = {
            'email': {'write_only': True}, 
        }
        fields = ('course', 'name', 'email', 'comment', 'rating', 'created_at', )
        model = models.Review

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'title', 'url', )
        model = models.Course
```
設定完成後打開django shell，來測試一下我們寫的serializer，從model取出一個course，經由serializer和JSONRenderer轉換成JSON，JSONRenderer所產生的是byte string，如果python要使用的話要再經過一次處理
```python
from rest_framework.renderers import JSONRenderer
from courses.models import Course
from courses.serializers import CourseSerializer
course = Course.objects.latest('id')
course.title
serializer = CourseSerializer(course)
serializer
serializer.data
JSONRenderer().render(serializer.data)
```
```python
>>> from rest_framework.renderers import JSONRenderer
>>> from courses.models import Course
>>> from courses.serializers import CourseSerializer
>>> course = Course.objects.latest('id')
>>> course.title
u'Python Collections'
>>> serializer = CourseSerializer(course)
>>> serializer
CourseSerializer(<Course: Python Collections>):
    id = IntegerField(label='ID', read_only=True)
    title = CharField(max_length=255)
    url = URLField(max_length=200, validators=[<UniqueValidator(queryset=Course.objects.all())>])
>>> serializer.data
{'url': u'https://teamtreehouse.com/library/python-collections', 'id': 2, 'title': u'Python Collections'}
>>> JSONRenderer().render(serializer.data)
'{"id":2,"title":"Python Collections","url":"https://teamtreehouse.com/library/python-collections"}'
```
在serializer準備好之後，我們要來看API怎樣處理http request，DRF提供了一個view class叫做APIView，它是django view class的subclass，增加了一些重要的功能，同樣的API要接收的是DRF的request object而不是djanog的http request object，DRF的request object是django http request的extention class，增加了像是JSON data處理、authentication、…等功能，更多關於APIView的介紹可以看[這裡](http://www.django-rest-framework.org/api-guide/views/)，讓我們開始建構views.py吧！在初始化CourseSerializer時用了一個參數many=True代表輸入的是多個object
```python
# courses/views.py
from rest_framework.views import APIView
from rest_framework.response import Response

from . import models
from . import serializers

class ListCourse(APIView):
    def get(self, request, format=None):
        courses = models.Course.objects.all()
        serializer = serializers.CourseSerializer(courses, many=True)
        return Response(serializer.data)
```
```python
# courses/urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ListCourse.as_view(), name='course_list'),
]
```
將設定course的上層URL，這裡使用api/v1來對API進行版本的管理，如果之後API欄位改變，在不破壞原有API的情況下，只要新增api/v2就可以了！有關版本管理的資訊請看[這裡](http://www.django-rest-framework.org/api-guide/versioning/#versioning)
```python
# ed_reviews/urls.py
urlpattern = [
    ...
    url(r'^api/v1/courses/', include('courses.urls', namespace='courses')),
]
```
完成在後瀏覽器輸入IP:8000/api/v1/courses/就可以看到Course List出現啦！但是好像沒有編輯的頁面，這就是我們的下一個目標了！
* 首先，將原本class ListCourse換成ListCreateCourse，別忘了urls.py也須要做相對應的更新
* post函式:
  * 將request data讀入serializer，此時資料都還在記憶體裡
  * 檢查格式
    * 如果符合，再存入database，格式的檢查之後會詳細介紹
    * raise_exception=True: 如果不符合，則跳出exception
  * 最後回傳201 Created，[這裡](http://www.django-rest-framework.org/api-guide/status-codes/)是status code的列表
```python
# courses/views.py
from rest_framework import status

class ListCreateCourse(APIView):
    ...
    def post(self, request, format=None):
        serializer = serializers.CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```
```python
# courses/urls.py
urlpatterns = [
    url(r'^$', views.ListCreateCourse.as_view(), name='course_list'),
]
```
完成在後瀏覽器輸入IP:8000/api/v1/courses/就可以看到Course Create List出現，拉到下方可以看到有POST區域，但如果開啟無痕視窗，會發現POST區域消失了！因為無痕視窗的尚未登入的狀態，在content區域輸入`{"title": "Object-Oriented Python"}`會得到
```javascript
{
    "url": [
        "This field is required."
    ]
}
```
因為沒有輸入url欄位，在content區域改輸入`{"title": "Object-Oriented Python", "url": "https://teamtreehouse.com/library/python-collections"}`則會得到
```javascript
{
    "url": [
        "course with this url already exists."
    ]
}
```
因為url欄位的unique=True，但輸入的url是重覆的，最後我們輸入`{"title": "Object-Oriented Python", "url": "https://teamtreehouse.com/library/objectoriented-python"}`就可以得到201 Created
```javascript
{
    "id": 3,
    "title": "Object-Oriented Python",
    "url": "https://teamtreehouse.com/library/objectoriented-python"
}
```
再按GET就可以看到有三門課程出現啦！但是有沒有更簡單的方法來建立DRF API呢？讓我們繼續看下去了！
## Make the REST Framework Work for You
上一節我們寫了List和Create View，但是其他的CRUD還沒有實做，再復習一下CRUD代表Create、Read、Update、Delete，是對data的基本操作，當然我們可以繼續再刻一個update view、delete view、…，但DRF提供了我們generic view來完成這件事，就不用重覆造輪子了！DRF generic view讓我們可以比較容易的根據model來建立出API view，讓我們把原本的ListCreateView用generic view來改寫，只須要繼承generics.ListCreateAPIView，指定queryset和serializer_class就可以了！很簡單吧！和前面的比較，我們的程式碼從十行降到三行！
```python
# courses/views.py
...
from rest_framework import generics

class ListCreateCourse(generics.ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
```
畫面看起來幾乎一模一樣，除了下方的POST區域，用了generic view，POST區域從原本要輸入JSON的一塊，變成了只要輸入欄位就好了！當然按下Raw data，也可以輸入JSON，而且generic view幫我們把JSON的key都準備好了！我們繼續寫Create、Update、Delete的功能，同樣很簡單，只要繼承generics.RetrieveUpdateDestroyAPIView，再指定相同的queryset和serializer_class即可，記得要為新的view加URL
```python
# courses/views.py
class RetrieveUpdateDestroyCourse(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
```
```python
# courses/urls.py
urlpatterns = [
    ...
    url(r'^(?P<pk>\d+)/$', views.RetrieveUpdateDestroyCourse.as_view(), name='course_detail'),
]
```
完成後在瀏覽器輸入IP:8000/api/v1/courses/1/可以看到course id=1的課程，下方的PUT區域可以更改內容，再複習一下，REST當中用POST來建立物件、用PUT來更新物件，右上的DELETE可以刪除課程，刪除前會有視窗跳出來再尋問一次，實際按按看囉！
```javascript
{
    "id": 1,
    "title": "Python Basics",
    "url": "https://teamtreehouse.com/library/python-basics"
}
```
更多有關generic view的資訊請看[這裡](http://www.django-rest-framework.org/api-guide/generic-views/)

目前為止，我們用generics view來寫REST API，讓程式碼精簡了不少，但還沒有把reviews加進來，如果想要做一個`/api/v1/courses/1/reviews/`來得到course 1的所有review，更進一步，希望`/api/v1/courses/1/reviews/1/`可以得到course 1的review 1，看來得要改寫一下generics view class，先把Review的generic view寫完
```python
# courses/views.py
...
class ListCreateReview(generics.ListCreateAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer

class RetrieveUpdateDestroyReview(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
```
```python
# courses/urls.py
urlpatterns = [
    ...
    url(r'^(?P<course_pk>\d+)/reviews/$',
        views.ListCreateReview.as_view(),
        name='review_list'),
    url(r'^(?P<course_pk>\d+)/reviews/(?P<pk>\d+)/$',
        views.RetrieveUpdateDestroyReview.as_view(),
        name='review_detail'),
]
```
然後我們要改寫ListCreateReview的get_queryset函式
```python
class ListCreateReview(generics.ListCreateAPIView):
    ...
    def get_queryset(self):
        return self.queryset.filter(course_id=self.kwargs.get('course_pk'))
```
完成後在瀏覽器輸入IP:8000/api/v1/courses/1/reviews/可以看到有一個raring給5顆星的review
```javascript
[
    {
        "course": 1,
        "name": "Kenneth",
        "comment": "",
        "rating": 5,
        "created_at": "2016-05-11T17:18:04.891000Z"
    }
]
```
往POST的區域看去，我們希望當我們新增reviews時，自動代入目前我們所觀注的這門課，以這個例子來說就是course 1，也就是Python basics，在目前使用情境下這個問題好像不會很嚴重，但是想像一下如果facebook當中，我們能以別人的帳號的發文，那是多麼嚴重的事，所以對courses/views稍加修改
```python
from django.shortcuts import get_object_or_404

class ListCreateReview(generics.ListCreateAPIView):
    ...
    def perform_create(self, serializer):
        course = get_object_or_404(
            models.Course, pk=self.kwargs.get('course_pk'))
        serializer.save(course=course)
```
同樣的，在detail view中，我們也想要確保只能對該course之下的review進行操作
```python
class RetrieveUpdateDestroyReview(generics.RetrieveUpdateDestroyAPIView):
    ...
    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            course_id=self.kwargs.get('course_pk'),
            pk=self.kwargs.get('pk'))
```
前面我們用generic view來簡化了API的實作，也覆寫了generic view的一些函式來達到階層的效果，接下來要實作第二個版本的API，想要完成的目標是可以呼叫`/api/v2/reviews/`和`/api/v2/reviews/1/`來檢視review，這和原本的API結構會有衝突，為了讓原本的API用戶不會被影響，我們用v2來呼叫新API，v1來呼叫舊API，這樣就不會相互干擾了！介紹2樣新工具:viewsets和routers
* routers是DRF提供、專為view set而設計的工具，為APIView自動生成URL，雖然看似幫助不大，但是能少寫些URL還是不錯的
* viewsets則把所有相關的views都合進一個單一的class，叫做view set，所以就無須再建立一堆List Create APIView和Retrieve Update Destroy APIView，只須要為每一個項目建立一個view set就可以了！

```python
# courses/views.py
from rest_framework import viewsets

class CourseViewSet(viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
```
```python
# ed_reviews/urls.py
from rest_framework import routers

from courses import views

router = routers.SimpleRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    ...
    url(r'^api/v2/', include(router.urls, namespace='apiv2')),
]
```
用了viewsets和routers之後，從瀏覽器輸入IP:8000/api/v2/courses/可以得到和之前相同的效果，也可以輸入IP:8000/api/v2/reviews/來操作reviews，但如果還是想要有IP:8000/api/v2/courses/1/reviews/這個動作來觀看某course底下所有的reviews呢？讓我們再做一點修改
```python
# courses/views.py
from rest_framework.decorators import detail_route
from rest_framework.response import Response

class CourseViewSet(viewsets.ModelViewSet):
    ...
    @detail_route(methods=['get'])
    def reviews(self, request, pk=None):
        course = self.get_object()
        serializer = serializers.ReviewSerializer(
            course.reviews.all(), many=True)
        return Response(serializer.data)
```
完成啦！最後再處理一個問題，現在可以從course底下看到關於這門課的所有review，那麼把所有reviews列出來，也就是/api/v2/reviews/這項功能好像沒什麼意義，能不能把List的功能去除掉呢？
再描述一次想要達到的效果，目前每個項目都可以有List、Create、Retrieve、Update、Destroy這幾項功能，我們想只使用其中某幾項功能，透過DRF的mixins可以達到這個目標，先看一下要如何簡單實作出ModelViewSet的功能，
```python
from rest_framework import viewsets, mixins

class ModelViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    pass
```
ModelViewSet其實只是繼承了多個mixin的一個viewset，知道這件事之後，要達到我們想做的事只要讓ReviewViewSet不要繼承ListModelMixin就可以了！
```python
from rest_framework import mixins

class ReviewViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    ...
```
更多關於routers的資料請看[這裡](http://www.django-rest-framework.org/api-guide/routers/)，更多關於viewsets的資料請參考[這裡](http://www.django-rest-framework.org/api-guide/viewsets/)，目前為止，我們已經從最底層的APIView、看到generic view、到最後的viewsets

現在我們要查詢關於某項課程的reviews，須要用`/api/v2/courses/1/reviews/`來查看，如果能夠把那項課程reviews的id、甚至URL也列出來，那該有多好！？讓我們來看看如何達成這件事吧！在CourseSerializer新增了一個欄位reviews，並把它加入Meta的fields
```python
# courses/serializers.py
class CourseSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        fields = ('id', 'title', 'url', 'reviews')
```
```javascript
{
    "id": 1,
    "title": "Python Basics",
    "url": "https://teamtreehouse.com/library/python-basics",
    "reviews": [
        {
            "id": 1,
            "course": 1,
            "name": "Kenneth",
            "comment": "",
            "rating": 5,
            "created_at": "2016-05-11T17:18:04.891000Z"
        }
    ]
}
```
從瀏覽器看`/api/v2/courses/1/`可以發現多了一項reviews，把course 1底下所有的review的細節全部列出來，效果還不錯，但這樣子的缺點是如果reivew總數很多的話，容易大大拖慢資料傳遞、處理的速度…，所以如果知道data總數的話有個不太大的上限，這是個還不錯的方法！例如:1-1的關係，像是一個使用者對應一組基本資料，

再看另外一種course和review的對應方式，透過URL link，直接看完成後的效果就能輕易理解
```python
# courses/serializers.py
class CourseSerializer(serializers.ModelSerializer):
    reviews = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='apiv2:review-detail'
    )
```
```javascript
{
    "id": 1,
    "title": "Python Basics",
    "url": "https://teamtreehouse.com/library/python-basics",
    "reviews": [
        "http://172.17.28.72:8000/api/v2/reviews/1/",
        "http://172.17.28.72:8000/api/v2/reviews/3/"
    ]
}
```
可以透過Response裡的URL連結，再執行下一步的操作，這種模式稱為Hateioas，是Hypermedia As The Engine Of Application State的網寫，所有物件透過Hyperlink互相連結，不用保存大量的資料，須要的時候透過Hyperlink去獲取。這種模式的缺點和之前一樣，再大量data時會要生成大量的URL，也會拖慢執行速度。

再看一個相似的效果，把HyperlinkedRelatedField換成PrimaryKeyRelatedField，這只會傳回review的primary key，速度是最快的，只要使用者知道review的相對應URL，就可以使用primary key了！
```python
# courses/serializers.py
class CourseSerializer(serializers.ModelSerializer):
    reviews = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
```
```javascript
{
    "id": 1,
    "title": "Python Basics",
    "url": "https://teamtreehouse.com/library/python-basics",
    "reviews": [
        1,
        3
    ]
}
```
我們介紹了三種Serializer的relation，更多資訊可以看[官網介紹](http://www.django-rest-framework.org/api-guide/relations/)

最後介紹一個工具，確保我們不用一次處理上千筆回傳資料，這項工叫pagination，DRF為generic view和view set提供了內建的pagination，先要在settings.py做全域的設定，當然也可以為單獨的view設定自己的pagination，我們展示全域的設定怎麼修改
```python
# ed_reviews/settings.py
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}
```
第一項啟用了分頁機制，第二項設定每一頁最多有五個項目，通常不會設定成那麼小的數字，不過我們的資料庫裡面沒有很多資料，打開瀏覽器看`/api/v2/courses/`可以看到回傳內容改變了！原本的內容被放到一個result裡面，多了count代表總共有幾項，也多了next、previous提供前往上、下頁的連結，把PAGE_SIZE偷偷改成1可以看到明顯的結果，可以看到next是下一頁的URL
```javascript
{
    "count": 3,
    "next": "http://172.17.28.72:8000/api/v2/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Python Basics",
            "url": "https://teamtreehouse.com/library/python-basics",
            "reviews": [
                "http://172.17.28.72:8000/api/v2/reviews/1/",
                "http://172.17.28.72:8000/api/v2/reviews/3/"
            ]
        }
    ]
}
```
要注意的是設定了default page會影響到所有的頁面，但不包括我們自己修改過views的某些部份，例如CourseViewSet裡面我們添加的detail_route就不在pagination的範圍內，這就須要寫客製化的pagination了！
```python
# courses/views.py
class CourseViewSet(viewsets.ModelViewSet):
    ...
    @detail_route(methods=['get'])
    def reviews(self, request, pk=None):
        self.pagination_class.page_size = 1
        reviews = models.Review.objects.filter(course_id=pk)

        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = serializers.ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
```
這樣就完成了客製化的pagination，關於Pagination的資料可以參考[這裡](http://www.django-rest-framework.org/api-guide/pagination/)
## Security and Customization
## Epilogue
