管理员账号：admin/1qaz@WSX
---
Q:为什么将xadmin拷贝到项目中？
A:需要对其源码进行必要修改，如model中使用了自定义的feild type后可能需要修改xadmin.util.display_for_field()方法，以便兼容
