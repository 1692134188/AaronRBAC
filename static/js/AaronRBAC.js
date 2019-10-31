(function () {
    var requestUrl = null;

    /*通过正则获取url中的参数*/
    function getUrlParam(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return decodeURI(r[2]);
        return null;
    }

    function init(pager) {
        $.ajax({
            url: requestUrl,
            type: 'GET',
            data: {'pager': pager},
            dataType: "JSON",
            success: function (result) {
                initGlobalData(result.global_dict);
                initHeader(result.table_config);
                initBody(result.table_config, result.data_list);
                initPager(result.pager);
            }
        })
    }

    function initGlobalData(global_dict) {
        $.each(global_dict, function (k, v) {
            window[k] = v;
        })
    }

    function initHeader(table_config) {
        var tr = document.createElement('tr');
        $.each(table_config, function (k, item) {
            if (item.display) {
                var th = document.createElement('th')
                th.innerHTML = item.title
                $(tr).append(th)
            }
        })
        $('#table_th').empty();
        $('#table_th').append(tr);
    }

    function initBody(table_config, data_list) {
        $('#table_tb').empty();

        $.each(data_list, function (k, row) {
            var tr = document.createElement('tr');
            tr.setAttribute('row-id', row['id']);
            $.each(table_config, function (k, config) {
                if (config.display) {

                    var td = document.createElement('td')

                    td.innerHTML = makeTdText(row, config);
                    /* 属性colConfig.attrs = {'edit-enable': 'true','edit-type': 'select'}  */
                    $.each(config.attrs, function (kk, vv) {
                        if (vv[0] == '@') {
                            td.setAttribute(kk, row[vv.substring(1, vv.length)]);
                        } else {
                            td.setAttribute(kk, vv);
                        }
                    });
                    $(tr).append(td)
                }
            })
            $('#table_tb').append(tr);
        })
    }

    function initPager(pager) {
        $('#idPagination').html(pager);
    }

    ///把'text': {'content': "<a href='/userdetail-{m}.html'>{n}</a>", 'kwargs': {'n': '查看详细', 'm': '@id'}},
    ///转换成 "<a href='/userdetail-1.html'>查看详细</a>"
    function makeTdText(row, config) {
        //第一步，把{'n': '查看详细', 'm': '@id'}  转换成  {n: "查看详细", m: 1}
        var kwargs = {};  //  {n: "查看详细", m: 1}
        $.each(config.text.kwargs, function (key, value) {
            if (value.substring(0, 2) == '@@') {
                var globalName = value.substring(2, value.length); // 全局变量的名称
                var currentId = row[config.q]; // 获取的数据库中存储的数字类型值
                var t = getTextFromGlobalById(globalName, currentId);
                kwargs[key] = t;
            } else if (value[0] == '@') {
                kwargs[key] = row[value.substring(1, value.length)];
            } else {
                kwargs[key] = value;
            }
        });
        //第二步，把 {n: "查看详细", m: 1} 转换成
        var temp = config.text.content.format(kwargs);
        return temp;
    }

    String.prototype.format = function (kwargs) {
        // this ="laiying: {age} - {gender}";
        // kwargs =  {'age':18,'gender': '女'}
        var ret = this.replace(/\{(\w+)\}/g, function (km, m) {
            return kwargs[m];
        });
        return ret;
    };

    function getTextFromGlobalById(globalName, currentId) {
        // globalName = "user_type_choices"
        // currentId = 1
        var ret = null;
        $.each(window[globalName], function (k, item) {
            if (item[0] == currentId) {
                ret = item[1];
                return
            }
        });
        return ret;
    }

    function bindEditMode() {
        $('#idEditMode').click(function () {
            var editing = $(this).hasClass('btn-warning');
            if (editing) {
                // 退出编辑模式
                $(this).removeClass('btn-warning');
                $(this).text('进入编辑模式');

                $('#table_tb').find(':checked').each(function () {
                    var $currentTr = $(this).parent().parent();
                    trOutEditMode($currentTr);
                })

            } else {
                // 进入编辑模式
                $(this).addClass('btn-warning');
                $(this).text('退出编辑模式');
                $('#table_tb').find(':checked').each(function () {
                    var $currentTr = $(this).parent().parent();
                    trIntoEditMode($currentTr);
                })
            }
        })
    }

    function trIntoEditMode($tr) {
        $tr.addClass('success');
        $tr.attr('has-edit', 'true');
        $tr.children().each(function () {
            // $(this) => td
            var editEnable = $(this).attr('edit-enable');
            var editType = $(this).attr('edit-type');
            if (editEnable == 'true') {
                if (editType == 'select') {
                    var globalName = $(this).attr('global-name'); //  "users_status_choices"
                    var origin = $(this).attr('origin'); // 1
                    var new_val = $(this).attr('new-val'); // 1
                    if (typeof (new_val) != "undefined") {
                        origin = new_val;
                    }
                    // 生成select标签
                    var sel = document.createElement('select');
                    sel.className = "form-control";
                    $.each(window[globalName], function (k1, v1) {
                        var op = document.createElement('option');
                        op.setAttribute('value', v1[0]);
                        op.innerHTML = v1[1];
                        $(sel).append(op);
                    });
                    $(sel).val(origin);

                    $(this).html(sel);
                } else if (editType == 'input') {
                    // input文本框
                    // *******可以进入编辑模式*******
                    var innerText = $(this).text();
                    var tag = document.createElement('input');
                    tag.className = "form-control";
                    tag.value = innerText;
                    $(this).html(tag);
                }
            }
        })
    }

    function trOutEditMode($tr) {
        $tr.removeClass('success');
        $tr.children().each(function () {
            // $(this) => td
            var editEnable = $(this).attr('edit-enable');
            var editType = $(this).attr('edit-type');
            if (editEnable == 'true') {
                if (editType == 'select') {
                    // 获取正在编辑的select对象
                    var $select = $(this).children().first();
                    // 获取选中的option的value
                    var newId = $select.val();
                    // 获取选中的option的文本内容
                    var newText = $select[0].selectedOptions[0].innerHTML;
                    // 在td中设置文本内容
                    $(this).html(newText);
                    $(this).attr('new-val', newId);

                } else if (editType == 'input') {
                    // *******可以退出编辑模式*******
                    var $input = $(this).children().first();
                    var inputValue = $input.val();
                    $(this).html(inputValue);
                    $(this).attr('new-val', inputValue);
                }

            }
        })
    }

    function bindCheckbox() {
        // $('#table_tb').find(':checkbox').click()
        $('#table_tb').on('click', ':checkbox', function () {
            if ($('#idEditMode').hasClass('btn-warning')) {
                var ck = $(this).prop('checked');
                var $currentTr = $(this).parent().parent();
                if (ck) {
                    // 进入编辑模式
                    trIntoEditMode($currentTr);
                } else {
                    // 退出编辑模式
                    trOutEditMode($currentTr)
                }
            }
        })
    }

    function bindReverseAll() {
        $('#idReverseAll').click(function () {
            $('#table_tb').find(':checkbox').each(function () {
                // $(this) => checkbox
                if ($('#idEditMode').hasClass('btn-warning')) {
                    if ($(this).prop('checked')) {
                        $(this).prop('checked', false);
                        trOutEditMode($(this).parent().parent());
                    } else {
                        $(this).prop('checked', true);
                        trIntoEditMode($(this).parent().parent());
                    }
                } else {
                    if ($(this).prop('checked')) {
                        $(this).prop('checked', false);
                    } else {
                        $(this).prop('checked', true);
                    }
                }
            })
        })
    }

    function bindCancelAll() {
        $('#idCancelAll').click(function () {
            $('#table_tb').find(':checked').each(function () {
                // $(this) => checkbox
                if ($('#idEditMode').hasClass('btn-warning')) {
                    $(this).prop('checked', false);
                    // 退出编辑模式
                    trOutEditMode($(this).parent().parent());
                } else {
                    $(this).prop('checked', false);
                }
            });
        })
    }

    function bindCheckAll() {
        $('#idCheckAll').click(function () {
            $('#table_tb').find(':checkbox').each(function () {
                // $(this)  = checkbox
                if ($('#idEditMode').hasClass('btn-warning')) {
                    if ($(this).prop('checked')) {
                        // 当前行已经进入编辑模式了
                    } else {
                        // 进入编辑模式
                        var $currentTr = $(this).parent().parent();
                        trIntoEditMode($currentTr);
                        $(this).prop('checked', true);
                    }
                } else {
                    $(this).prop('checked', true);
                }
            })
        })
    }

    function bindSave() {
        $('#idSave').click(function () {
            var postList = [];
            //找到已经编辑过的tr，tr has-edit='true'
            $('#table_tb').find('tr[has-edit="true"]').each(function () {
                // $(this) => tr
                var temp = {};
                var id = $(this).attr('row-id');
                temp['id'] = id;
                $(this).children('[edit-enable="true"]').each(function () {
                    // $(this) = > td
                    var name = $(this).attr('name');
                    var origin = $(this).attr('origin');
                    var newVal = $(this).attr('new-val');
                    if (origin != newVal) {
                        temp[name] = newVal;
                    }
                });
                postList.push(temp);
            })

            $.ajax({
                url: requestUrl,
                type: 'PUT',
                data: {'post_list': JSON.stringify(postList)},
                dataType: 'JSON',
                success: function (arg) {
                    if (arg.status) {
                        init(3);
                    } else {
                        alert(arg.error);
                    }
                }
            })
        })
    }

    function bindChangePager() {
        $('#idPagination').on('click', 'a', function () {
            var num = $(this).text();
            init(num);
        })
    }

    jQuery.extend({
        'NB': function (url) {
            requestUrl = url;
            init(getUrlParam("p"));
            bindEditMode();
            bindCheckbox();
            bindCheckAll();
            bindCancelAll();
            bindReverseAll();
            bindSave();
            bindChangePager();
        },
        'changePager': function (num) {
            init(num);
        }
    })
})()