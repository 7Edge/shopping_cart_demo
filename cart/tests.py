from django.test import TestCase

# Create your tests here.


from django.db.models import Q

a = {b'course_img': b'/cart/images/python_full_stack.jpg', b'policy_id': b'1',
     b'degree_price_policy_qs': b'{"1": {"period": 180, "period_str": "6\\u4e2a\\u6708", "price": 800.0}}',
     b'name': b'Python\xe5\x85\xa8\xe6\xa0\x88\xe5\xbc\x80\xe5\x8f\x91'}

payment_template = {

     "paymentcenter_1_1": {
          "name": 'python',
          "image": 'app01.jpg',
          "price": 1000.00,
          "period": 120,
          "period_str": "一年",
          "coupon_list": {
               100: {
                    "name": '618活动！',
                    "type": 0,

                    "status": 0,
                    "get_time": '2019-10-10',

               },
               101: {

               }
          },
          "coupon": 100

     }
}
