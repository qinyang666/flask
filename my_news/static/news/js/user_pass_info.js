function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function(e){
        e.preventDefault()
        var current_pwd = $("#current_pwd").val(),
        new_pwd = $("#new_pwd").val(),
        cpwd = $("#cpwd").val(),
        csrf_token = $("#pwd_csrf_token").val();
        if (!current_pwd){
            $(".error_tip").text("请输入当前密码").show();
            return 
        }
        if(!new_pwd){
            $(".error_tip").text("请输入新密码").show();
            return 
        }
        if(new_pwd != cpwd){
            $(".error_tip").text("两次密码不一致").show();
            return 
        }
        if(new_pwd == current_pwd){
            $(".error_tip").text("新密码与原密码不能相同").show();
            return 
        }
        if(current_pwd.length>20 || current_pwd.length<6){
            $(".error_tip").text("当前密码错误").show();
            return 
        }
        if(new_pwd.length>20 || new_pwd.length<6){
            $(".error_tip").text("请输入6-20新位密码").show();
            return 
        }
        $.post("/user/pass_info",
                {   current_pwd:current_pwd, 
                    cpwd:cpwd, 
                    new_pwd: new_pwd,
                    csrf_token: csrf_token},
                function(dat){
                   if(dat.res == 1){
                        parent.location.href = "/user/logout";
                   }else if(dat.res==2){
                        $(".error_tip").text("修改密码失败，请稍后重试！").show();
                   }else{
                        $(".error_tip").text("当前密码错误").show();
                   } 
        
        })  
        

})
    
})
