$(document).ready(function(){
	var data = 0;
	var loc1= '';
	var loc2= '';
	function close_accordion_section(){
		$('.accordion .accordion-section-title').removeClass('active');
		$('.accordion .accordion-section-content').slideUp(300).removeClass('open');
	}
	






	

	$('.accordion-section-title').click(function(e){
		var currentAttrValue = $(this).attr('href');
		if($(e.target).is('.active')){
			close_accordion_section();}
		else{
			close_accordion_section();
			$(this).addClass('active');
			$('.accordion '+currentAttrValue).slideDown(300).addClass('open');
		}
	});

	$('#stop1').on('change',function(){
		var e = document.getElementById("stop1");
		var strUser = e.options[e.selectedIndex].value;
		alert(strUser);
	});
	$('#stop2').on('change',function(){
		var stop2 = document.getElementById("stop2");
		var stop2Str=stop2.options[stop2.selectedIndex].value;
		alert(stop2Str);
	});


	
});
