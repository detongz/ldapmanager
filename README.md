# LdapManager

用户登陆，修改密码

普通用户看文档;高级用户增删改查用户。

目前还没有加上权限控制的部分，也就是所有用户都可以增删改查。页面和控制逻辑待补充。

ldapscripts对我来讲不好用，总是莫名其妙出bug。

ldapmanager/common/ldap.py脚本里用python的ldap3库做了curd，实现了部分ldapscripts功能，不过有个缺陷是直接调用了admin账户去curd，这个待改进。
计划前端部分在这个脚本基础上封装。
