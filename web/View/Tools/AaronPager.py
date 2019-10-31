# 2.1 所需要的参数
# 序号          字段名             备注
# a           data_count      列表的总个数
# b           current_page_num当前页码
# C           page_rows       每页显示多少行数据（每页显示10条）
# D           page_num_size   页码条显示个数（建议为奇数，最多页面7个）
# 2.2 方法具有的内容
# 序号          字段名         备注
# 1               start   当前页列表显示的初始值
# 2               end     当前页列表显示的结束值
# 3           page_count  总页数
# 4           page_par_range  页码条显示范围
from django.utils.safestring import mark_safe
class AaronPager(object):
    def __init__(self, data_count, current_page_num, page_rows=10, page_num_size=7,base_url='/'):
        # 数据总个数
        self.data_count = data_count
        # 当前页
        try:
            v = int(current_page_num)
            if v <= 0:
                v = 1
            self.current_page_num = v
        except Exception as e:
            self.current_page_num = 1
        # 每页显示的行数
        self.page_rows = page_rows
        # 最多显示页面
        self.page_num_size = page_num_size
        #设置前台页面传递过来的url
        self.base_url=base_url
    def start(self):
        return (self.current_page_num - 1) * self.page_rows

    def end(self):
        return self.current_page_num * self.page_rows

    @property
    def page_count(self):
        # 总页数
        a, b = divmod(self.data_count, self.page_rows)
        if b == 0:
            return a
        return a + 1

    def page_par_range(self):
        #         总页数（ self.page_count）     总页码数（self.page_num_size）   当前页（self.current_page_num）
        #         如果总页数<总页码数
        if self.page_count < self.page_num_size:
            return range(1, self.page_count + 1)
        # 如果当前页数<总页码数/2
        part = self.page_num_size // 2
        if self.current_page_num < part:
            return range(1, self.page_num_size + 1)
        # 如果当前页+part >总页码数
        if self.current_page_num + part > self.page_count:
            return range(self.page_count - self.page_num_size+1, self.page_count+1)
        return range(self.current_page_num - part, self.current_page_num + part+1)

    def page_str(self):
        page_list = []
        first = "<li><a href='%s?p=1'>首页</a></li>" %(self.base_url,)
        page_list.append(first)
        if self.current_page_num == 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            prev = "<li><a href='%s?p=%s'>上一页</a></li>" %(self.base_url,self.current_page_num - 1)
        page_list.append(prev)
        for i in self.page_par_range():
            if i==self.current_page_num:
                temp = "<li class='active'><a href='%s?p=%s'>%s</a></li>" %(self.base_url,i,i)
            else:
                temp = "<li><a href='%s?p=%s'>%s</a></li>" %(self.base_url,i,i)
            page_list.append(temp)

        if self.current_page_num == self.page_count:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            nex = "<li><a href='%s?p=%s'>下一页</a></li>" %(self.base_url,self.current_page_num + 1)
        page_list.append(nex)
        last = "<li><a href='%s?p=%s'>尾页</a></li>" %(self.base_url,self.page_count)
        page_list.append(last)

        return ''.join(page_list)

    def page_str2(self, base_url):
        page_list = []

        if self.total_count < self.pager_num:
            start_index = 1
            end_index = self.total_count + 1
        else:
            if self.current_page <= (self.pager_num + 1) / 2:
                start_index = 1
                end_index = self.pager_num + 1
            else:
                start_index = self.current_page - (self.pager_num - 1) / 2
                end_index = self.current_page + (self.pager_num + 1) / 2
                if (self.current_page + (self.pager_num - 1) / 2) > self.total_count:
                    end_index = self.total_count + 1
                    start_index = self.total_count - self.pager_num + 1

        if self.current_page == 1:
            prev = '<li><a class="page" href="javascript:void(0);">上一页</a></li>'
        else:
            prev = '<li><a class="page" href="%s?p=%s">上一页</a></li>' % (base_url, self.current_page - 1,)
        page_list.append(prev)

        for i in range(int(start_index), int(end_index)):
            if i == self.current_page:
                temp = '<li class="active"><a class="page active" href="%s?p=%s">%s</a></li>' % (base_url, i, i)
            else:
                temp = '<li><a class="page" href="%s?p=%s">%s</a></li>' % (base_url, i, i)
            page_list.append(temp)

        if self.current_page == self.total_count:
            nex = '<li><a class="page" href="javascript:void(0);">下一页</a></li>'
        else:
            nex = '<li><a class="page" href="%s?p=%s">下一页</a></li>' % (base_url, self.current_page + 1,)
        page_list.append(nex)

        # jump = """
        # <input type='text'  /><a onclick='jumpTo(this, "%s?p=");'>GO</a>
        # <script>
        #     function jumpTo(ths,base){
        #         var val = ths.previousSibling.value;
        #         location.href = base + val;
        #     }
        # </script>
        # """ % (base_url,)
        #
        # page_list.append(jump)

        page_str = mark_safe("".join(page_list))

        return page_str