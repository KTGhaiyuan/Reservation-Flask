$(function(){
	$("i.more").click(function(){
		$(this).hide();
		$(".section2").show(300);
	})
	$(".dropdownmenu1 li a").click(function(){
		$("#dropdownMenu1").text($(this).text());
		// $("#dropdownMenu1").append(' <span class="caret"></span>');
	})
	$(".dropdownmenu2 li a").click(function(){
		$("#dropdownMenu2").text($(this).text());
		// $("#dropdownMenu2").append(' <span class="caret"></span>');
	})
	$(".btn-primary").click(function(){
		var a = $("#NameInput").val();
		var b = $("#TelephoneInput").val();
		var c = $("#YongInput").val();
		var d = $("#ClassInput").val();
		var e = $.trim($("#dropdownMenu1").text())
		if (a&&b&&c&&d&&e!="使用时间") {
			alert("预约成功!");
		}
		
	})
})