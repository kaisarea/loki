$(document).ready(function() {
	$("[class^='count[']").each(function() {
		var elClass = $(this).attr('class');
		var minWords = 0;
		var maxWords = 0;
		var countControl = elClass.substring((elClass.indexOf('['))+1, elClass.lastIndexOf(']')).split(',');
		
		if(countControl.length > 1) {
			minWords = countControl[0];
			maxWords = countControl[1];
		} else {
			maxWords = countControl[0];
		}	
		
		$(this).after('<div class="wordCount">Write at least ' + minWords + ' words.  You have <strong>0</strong> so far.</div>');
		//if(minWords > 0) {
		//	$(this).siblings('.wordCount').addClass('error');
		//}	
		
		$(this).bind('keyup click blur focus change paste', function() {
			var numWords = jQuery.trim($(this).val()).split(' ').length;
			if($(this).val() === '') {
				numWords = 0;
			}	
			$(this).siblings('.wordCount').children('strong').text(numWords);
			
			if(numWords < minWords) {
				//$(this).siblings('.submit').removeClass('ui-widget');
			        $('#submit').attr('disabled', 'true');
			} else {
				//$(this).siblings('.wordCount').removeClass('error');	
				$('#submit').removeAttr('disabled');
			}
		});
	});
});


