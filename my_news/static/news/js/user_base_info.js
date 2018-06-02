function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender").val()
        var select_gender = $(".gender:checked").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        $.ajax({
            url: "/user/base_info",
            type: "POST",
            data: {
                "special_name":signature,
                "username":nick_name,
                "gender":select_gender,
                "csrf_token": $("#info_csrf_token").val()
            },
            dataType:"json"
        }).done(function(dat){
            if(dat.res==1){
                $(".user_center_name", parent.document).text("用户"+nick_name)
                $("#user_login", parent.document).children().eq(1).text("用户："+nick_name)
            }
        }).fail(function(){
            alert("服务器请求失败，请重试")
        })
    })
})
