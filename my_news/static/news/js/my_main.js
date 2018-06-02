var is_exist = false;
$(function(){

	// 打开登录框
	$('.login_btn').click(function(){
        $('.login_form_con').show();
	})
	
	// 点击关闭按钮关闭登录框或者注册框
	$('.shutoff').click(function(){
		$(this).closest('form').hide();
	})

    // 隐藏错误
    $(".login_form #mobile").focus(function(){
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function(){
        $("#login-password-err").hide();
    });

    // 打开注册框
	$('.register_btn').click(function(){
		$('.register_form_con').show();
	})


	// 登录框和注册框切换
	$('.to_register').click(function(){
		$('.login_form_con').hide();
		$('.register_form_con').show();
	})

	// 登录框和注册框切换
	$('.to_login').click(function(){
		$('.login_form_con').show();
		$('.register_form_con').hide();
	})

	// 点击输入框，提示文字上移
	$('.form_group').on('click focusin',function(){
		$(this).children('.input_tip').animate({'top':-5,'font-size':12},'fast').siblings('input').focus().parent().addClass('hotline');
	})

	// 输入框失去焦点，如果输入框为空，则提示文字下移
	$('.form_group input').on('blur focusout',function(){
		$(this).parent().removeClass('hotline');
		var val = $(this).val();
		if(val=='')
		{
			$(this).siblings('.input_tip').animate({'top':22,'font-size':14},'fast');
		}
	})


   
    // 注册验证
	var error_mobile = false;
	var error_password = false;
	var error_check = false;

    $("#smscode").focus(function(){
        $("#register-sms-code-err").hide();
    })
	$("#imagecode").focus(function(){
        	$("#register-image-code-err").hide()
		});

	$('.register_form #register_mobile').blur(function() {
		check_mobile();
	}).focus(function(){
		$('#register-mobile-err').hide();
	});

	$('.register_form #register_password').blur(function() {
		check_pwd();
	}).focus(function(){
		$('#register-password-err').hide();
	});


	$('#agree').click(function() {
		if($(this).is(':checked'))
		{
			error_check = false;
			$(this).next().next().hide();
		}                           
		else                        
		{                           
			error_check = true;     
			$(this).next().next().html('请勾选同意').show();
		}
	});


	function check_mobile(){
		var mobile = $('.register_form #register_mobile').val(), mobile_re = /^[1][3,4,5,7,8][0-9]{9}$/;
		if(!mobile_re.test(mobile))
		{
			$('#register-mobile-err').html('请输入正确的11数字手机号码').show()
			error_mobile = true;

		}
		else
		{
			$.get("/user/user_exist?mobile="+mobile,function(data){
				if(data.res == 0){
					$("#register-mobile-err").text("该手机号已被注册").show();
                    is_exist = true
					error_mobile = true;
				}else if(data.res == 1){
					$("#register-mobile-err").hide();
					error_mobile = false;
                    is_exist = false
				}
		 	})

		}
	}

	function check_pwd(){
		var len = $('.register_form #register_password').val().length;
		if(len<6||len>20)
		{
			$("#register-password-err").html('密码最少6位，最长20位').show()
			error_password = true;
		}
		else
		{
			$("#register-password-err").hide();
			error_password = false;
		}		
	}


	
	$('.register_form_con').submit(function(e) {
		e.preventDefault()
		// check_mobile();
		check_pwd();


		if(error_mobile == false && error_password == false && error_check == false)
		{
				// 发起注册请求
			var mobile = $("#register_mobile").val();
       	 	var smscode = $("#smscode").val();
       	 	var password = $("#register_password").val();
        	var code_pwd = $("#imagecode").val();
        	var agree = $("#agree").prop("checked")
            if(!smscode){
                $("#register-sms-code-err").text("请输入短信验证码");
            }
            if(!code_pwd){
                $("#register-image-code-err").html("请输入图片验证码").show()
            
            }

			$.ajax({
				url:"/user/register",
				type:"POST",
				data:{
					"mobile":mobile,
					"password":password,
					"code_pwd":code_pwd,
					"agree": agree,
                    "smscode": smscode,
					"csrf_token": $("#register_csrf_token").val()
				},
				dataType:"json"
			}).done(function(dat){
				if(dat.res==1){
					$('.to_login').click()
				}else if(dat.res==2){
					alert("注册失败，请重试")
				}else if(dat.res == 3){
                    $("#register-sms-code-err").text("短信验证码不正确!").show();
                }else{
					$("#register-image-code-err").html("验证码输入错误").show()
				}
			}).fail(function(){
				  alert("服务器超时，请重试")
			})
		}
		else
		{
			return;
		}

	});

    // 退出登录
    $("#logout").click(function(){
        $.get("/user/logout",function(dat){
            if(dat.res==1){
                location.href = ''
            }
        })
    })

   
	// TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault()
        var mobile = $(".login_form #mobile").val()
        var password = $(".login_form #password").val()
		var mobile_re = /^[1][3,4,5,7,8][0-9]{9}$/;

        if (!mobile_re.test(mobile)) {
            $("#login-mobile-err").text("用户名错误").show();
            return;
        }

        if (!password || password.length<6||password.length>20) {
            $("#login-password-err").text("密码错误").show();
            return;
        }

        // 发起登录请求
        $.ajax({
            url: "/user/login",
            type: "POST",
            data:{
                "mobile": mobile,
                "pwd": password,
                "csrf_token": $("#login_csrf_token").val()
            },
            dataType: "json"
        }).done(function(dat){
            if(dat.res == 1){
                $('.shutoff').closest('form').hide();
                location.href = ""  ;
            }else if(dat.res == 2){
                $("#login-password-err").text("密码错误").show();
            }else{
                $("#login-mobile-err").text("用户名错误").show();
            }
        }).fail(function(){;
            alert("服务器超时，请重试")
        })
    })



	// 根据地址栏的hash值来显示用户中心对应的菜单
	var sHash = window.location.hash;
	if(sHash!=''){
		var sId = sHash.substring(1);
		var oNow = $('.'+sId);		
		var iNowIndex = oNow.index();
		$('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
		oNow.show().siblings().hide();
	}

	// 用户中心菜单切换
	var $li = $('.option_list li');
	var $frame = $('#main_frame');

	$li.click(function(){
		if($(this).index()==5){
			$('#main_frame').css({'height':900});
		}
		else{
			$('#main_frame').css({'height':660});
		}
		$(this).addClass('active').siblings().removeClass('active');

	})

})





    

var imageCodeId = ""

// TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    $("#img_code").attr({"src":$("#img_code").attr("src")+1})
}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (mobile.length != 11) {
        $("#register-mobile-err").html("请输入11位数字的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    if(is_exist){
        $("#register-mobile-err").text("该手机号已被注册,请重新输入").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return 
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#register-image-code-err").html("请填写验证码！").show()
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送短信验证码
	$.get("/user/get_sms_code?mobile="+mobile + "&img_code=" + imageCode,function(dat){
        if(dat.res==1){
        	var time = 3;
        	var timer = setInterval(function(){
				$(".get_code").html(time+"秒后可重新发送").show();
        		time -= 1;
				if(time == 0){
        		clearInterval(timer)
				$(".get_code").html("重新发送").show();
				$(".get_code").attr("onclick", "sendSMSCode();");

			}
			},1000)
        }else{
            $(".get_code").attr("onclick", "sendSMSCode();");
            $("#register-image-code-err").html("验证码错误！").show()
        }
    })
}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        //$li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
