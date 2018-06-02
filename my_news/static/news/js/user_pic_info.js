function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "/user/pic_info",
            dataType: "json",
            type:"POST",
            success:function(dat){
                if(dat.res == 1){
                    $('.user_center_pic>img',parent.document).attr('src',dat.pic_url);
                    $('.lgin_pic',parent.document).attr('src',dat.pic_url);
                                                   
                    $(".now_user_pic").attr("src", dat.pic_url)
                }
            }
        })
        
    })

})
