from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.

# 课程大分类表，前端/后端
class CourseCategory(models.Model):
    """
    课程大分类表
    """
    name = models.CharField(verbose_name='课程类型', max_length=64, unique=True)

    class Meta:
        verbose_name_plural = "01. 课程大表"

    def __str__(self):
        return "%s" % self.name


# 课程之分类表
class CourseSubCategory(models.Model):
    """
    课程子分类表
    """
    category = models.ForeignKey(verbose_name="所属大分类", to="CourseCategory", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="子课程类型", max_length=64)

    class Meta:
        verbose_name_plural = "02. 课程子表"

    def __str__(self):
        return "%s" % self.name


# 学位课程
class DegreeCourse(models.Model):
    """
    学位课程表
    """
    name = models.CharField(verbose_name='学位课程名', max_length=128, unique=True)
    course_img = models.CharField(verbose_name='课程示图', max_length=255)
    brief = models.TextField(verbose_name='学位课程简介')
    total_scholarship = models.PositiveIntegerField(verbose_name='总奖学金(里贝)', default=40000)
    mentor_compensation_bonus = models.PositiveIntegerField(verbose_name='本课程的导师辅导费用(里贝)', default=15000)
    period = models.PositiveIntegerField(verbose_name='建议学习周期（days)', default=150)  # 用于计算学位奖学金
    prerequisite = models.TextField(verbose_name='课程先修要求', max_length=1024)
    teachers = models.ManyToManyField(verbose_name='课程老师', to="Teacher")

    # 反向查询价格策略集，按周期计价,
    degree_price_policy_qs = GenericRelation(to='PricePolicy')

    # 反向查询课程问题集
    degree_asked_question = GenericRelation(to='OftenAskedQuestion')

    class Meta:
        verbose_name_plural = "03. 学位课程表"

    def __str__(self):
        return self.name


# 讲师 导师表
class Teacher(models.Model):
    """
    讲师 导师表
    """
    name = models.CharField(verbose_name='老师名', max_length=64)
    role_choices = (
        (0, '讲师'),
        (1, '导师'),
    )
    role = models.SmallIntegerField(verbose_name='老师角色', choices=role_choices, default=0)
    title = models.CharField(verbose_name='职位/职称', max_length=64)
    signature = models.CharField(verbose_name='签名', max_length=255, blank=True, null=True)
    image = models.CharField(verbose_name='老师照片', max_length=255)
    brief = models.CharField(verbose_name='老师简介', max_length=1024)

    class Meta:
        verbose_name_plural = "04. 老师表"

    def __str__(self):
        return self.name


# 课程咨询常见问题
class OftenAskedQuestion(models.Model):
    """
    常见问题表，有一个联合主键
    """
    question = models.CharField(verbose_name='常见问题', max_length=255)
    answer = models.CharField(verbose_name='答案', max_length=255)

    object_id = models.IntegerField(verbose_name='关联对象ID', help_text="多个表的对象主键")
    content_type = models.ForeignKey(verbose_name='所属表的类型', to=ContentType, on_delete=models.CASCADE,
                                     help_text='外键引用ContentType的主键')
    generic_fk_to_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        verbose_name_plural = "08. 常见问题表"
        unique_together = ('question', 'object_id', 'content_type')

    def __str__(self):
        return "%s-%s" % (self.generic_fk_to_object, self.question)


# 价格策略 重要的表
class PricePolicy(models.Model):
    """
    价格策略表， 将学位课和专题课的价格策略都放在这里。主要策略的不同维度是周期不同
    """
    valid_period_choices = (
        (1, '1天'), (3, '3天'),
        (7, '1周'), (14, '2周'),
        (30, '1个月'),
        (60, '2个月'),
        (90, '3个月'),
        (180, '6个月'), (210, '12个月'),
        (540, '18个月'), (720, '24个月'),
    )
    period = models.PositiveSmallIntegerField(verbose_name='学习周期', choices=valid_period_choices)
    price = models.FloatField()

    object_id = models.IntegerField(verbose_name='课程对象')
    content_type = models.ForeignKey(verbose_name='对应类型', to=ContentType, on_delete=models.CASCADE)

    generic_fk_to_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        verbose_name_plural = "13. 价格策略表"
        unique_together = ('object_id', 'content_type', 'price')


# 用户表
class UserInfo(models.Model):
    user = models.CharField(verbose_name='用户名', max_length=64)
    pwd = models.CharField(verbose_name='密码', max_length=64)

    class Meta:
        verbose_name_plural = '201. 学城用户表'

    def __str__(self):
        return self.user


# token表
class UserToken(models.Model):
    user = models.OneToOneField(verbose_name='用户', to='UserInfo', on_delete=models.CASCADE)
    token = models.CharField(verbose_name='token', max_length=128)
    expired = models.DateTimeField(verbose_name='有效期', auto_now_add=True)

    class Meta:
        verbose_name_plural = '202. 用户认证token表'

    def __str__(self):
        return "%s - %s" % (self.user, self.token)
