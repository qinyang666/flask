function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 收藏
    $(".collection").click(function () {
        var news_id = $(this).attr("data-news_id")
        $.get("/collect/"+news_id,function(dat){
            if(dat.res==0){
                $(".login_form_con").show()
            }else if(dat.res==2){
                alert("收藏失败，请稍后重试")
            }else{
                $(".collected").show()
                $(".collection").hide()
                
            }
        })
       
    })

    // 取消收藏
    $(".collected").click(function () {
        var news_id = $(this).prev().attr("data-news_id")
        $.get("/collect/"+news_id,function(dat){
            if(dat.res==0){
                $(".login_form_con").show()
            }else if(dat.res==2){
                alert("取消收藏失败，请稍后重试")
            }else{
                $(".collected").hide()
                $(".collection").show()
                
            }
        })
     
    })
    
    // 创建vue接管评论区
    vue_comment = new Vue({
        el:".comment_list_con",
        delimiters:["[[","]]"],
        data:{
            comment_list:[]
        }
    })

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var news_id = $(".collection").attr("data-news_id")
        var comment = $(".comment_input").val()
        var csrf_token = $("#comment_csrf_token").val()
        if(!comment){
            return 
        }
        $.post("/comment",{comment:comment, news_id:news_id,csrf_token:csrf_token},function(dat){
            if(dat.res==1){
                comment_list = dat.comment_list
            }
        })

    })

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            }else {
                $this.addClass('has_comment_up')
            }
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            alert('回复评论')
        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})
