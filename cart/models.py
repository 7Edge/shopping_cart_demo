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

    # 方向查询优惠券策略
    coupon_qs = GenericRelation(to='Coupon', related_query_name='degreecourse')

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
    expired = models.DateTimeField(verbose_name='有效期')

    class Meta:
        verbose_name_plural = '202. 用户认证token表'

    def __str__(self):
        return "%s - %s" % (self.user, self.token)


# 课程优惠卷
class Coupon(models.Model):
    """优惠卷类型"""

    name = models.CharField(verbose_name='优惠券名', max_length=64)
    brief = models.TextField(verbose_name='优惠券介绍', null=True, blank=True)
    coupon_type_choices = ((0, '通用券'),
                           (1, '折扣券'),
                           (2, '满减券'))
    coupon_type = models.SmallIntegerField(verbose_name='券类型', choices=coupon_type_choices)

    money_equivalent_value = models.IntegerField(verbose_name='等值货币', null=True, blank=True)
    off_percent = models.PositiveIntegerField(verbose_name="折扣百分比", help_text="只针对折扣券，例7.9折，写79",
                                              null=True, blank=True)
    minimum_consume = models.PositiveIntegerField(verbose_name='最低消费', default=0, help_text="仅在满减券时填写此字段")

    object_id = models.PositiveIntegerField(verbose_name='课程id', blank=True, null=True, help_text='通用卷不用绑定课程')
    content_type = models.ForeignKey(verbose_name='课程类型', to=ContentType, null=True, blank=True,
                                     on_delete=models.CASCADE)
    content_object = GenericForeignKey()

    quantity = models.PositiveIntegerField(verbose_name='优惠券数量', default=1)
    open_date = models.DateField(verbose_name='优惠券领取开始时间')
    close_date = models.DateField(verbose_name='优惠券领取结束时间')
    valid_begin_date = models.DateField(verbose_name='有效期开始时间', null=True, blank=True)
    valid_end_date = models.DateField(verbose_name='有效期结束时间', null=True, blank=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name='优惠卷有效期(天)', blank=True, null=True,
                                                    help_text='自从券被领取时开始算起')

    date = models.DateTimeField(verbose_name='创建日期', auto_now_add=True)

    class Meta:
        verbose_name_plural = "500001. 优惠卷类型"

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)

    def save(self, *args, **kwargs):
        if not self.coupon_valid_days or (self.valid_begin_date and self.valid_end_date):
            if self.valid_begin_date and self.valid_end_date:
                if self.valid_end_date <= self.valid_begin_date:
                    raise ValueError("valid_end_date 有效期结束日期必须晚于 valid_begin_date ")
            if self.coupon_valid_days == 0:
                raise ValueError("coupon_valid_days 有效期不能为0")
        if self.close_date < self.open_date:
            raise ValueError("close_date 优惠券领取结束时间必须晚于 open_date优惠券领取开始时间 ")

        super(Coupon, self).save(*args, **kwargs)


# 优惠卷记录
class CouponRecord(models.Model):
    """优惠券发放，优惠券消费记录"""
    account = models.ForeignKey(verbose_name='所属账户', to='UserInfo', on_delete=models.CASCADE)
    coupon = models.ForeignKey(verbose_name="优惠券类型", to='Coupon', on_delete=models.CASCADE)
    coupon_number = models.CharField(verbose_name='优惠卷编号', max_length=64, unique=True)

    status_choices = ((0, '未使用'),
                      (1, '已使用'),
                      (2, '已过期'))
    status = models.SmallIntegerField(verbose_name='优惠卷状态', choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name='领取时间', help_text='用户领取时间')
    used_time = models.DateTimeField(verbose_name='使用时间', null=True, blank=True)

    # order = models.ForeignKey(verbose_name='使用的订单', to="Order", blank=True, null=True, verbose_name='关联订单')

    class Meta:
        verbose_name_plural = "500002. 优惠卷记录"

    def __str__(self):
        return '%s-%s-%s' % (self.account, self.coupon_number, self.status)
