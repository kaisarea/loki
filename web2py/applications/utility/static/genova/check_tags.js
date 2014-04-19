

var missing = $('tbody.key_inputs input:text').length;
var total_inputs = 0;
var unique_count = 0;
var values = new Array();
var debug1 = "";
var debug2 = "";
var fivetuple_keywords = new Array();
var duplicity_troubles = 0;
var radios_check = 0;
var all_radios = $('tbody input:radio').length/2;
var frequence_of_occurrence = 0;

$(function () {
    $('#response').submit(function(f) {
	    missing = 0;
	    duplicity_troubles = 0;
	    radios_check = 0;
	    $('.error_message').hide();
	    $('p.tag_error').attr('class', 'image_tag');
	    $('input.input_error').attr('class', 'image_tag');
	    $('table.input_error').attr('class', 'radio');
  	    radios_check = $('td input:radio:checked').length;

	    //$('p.error_message').hide();
	
	    $('input[class=keyword]').each(function(i) {
 		values[$(this).id] = $(this).val();
        	total_inputs = total_inputs+1;
        	if(values[$(this).id] == "")
        	{
                missing = missing + 1;
        	}
	    });


	    jQuery('tbody.key_inputs').each(function(k) {
        	fivetuple_keywords = new Array();
        	for(var m = 0; m < 5; m++)
        	{
                	fivetuple_keywords.push($(this).find('input')[m].value);
			current_keyword = $(this).find('input')[m].value;
			alert(fivetuple_keywords);
			frequency_of_occurrence = $(this).find('input:text[value="' + current_keyword + '"]').length;
			if(frequence_of_occurrence > 1)
			{
			    text_area = $(this).find('input:text[value="' + current_keyword + ']');
			    text_area.attr('class', 'input_error');
			    text_area.parent().parent().find('p.image_tag').attr('class', 'tag_error');
				
			}
        	}
        	unique_ans = jQuery.unique(fivetuple_keywords);
        	if(unique_ans.length != 5)
        	{
                duplicity_troubles = duplicity_troubles + 1;
        	}

	    });

	    if(missing == 0 & duplicity_troubles == 0 & radios_check == all_radios)
  	    {
		    alert('all good');
		    return;
  	    }
	    else
	    {
		    alert('should not go further');
		    $('input:radio').each(function(){
                if(!$('#' + $(this).attr('name')).is(':checked'))
                {
                    $(this).parent().parent().parent().parent().attr('class', 'input_error');
                }
       	 	});
		    $(':radio:checked').parent().parent().parent().parent().attr('class', 'radio');

		    $('tbody input:text[value=""]').each(function(){
			    $(this).attr('class', 'input_error');
			    $(this).parent().parent().find('p.image_tag').attr('class', 'tag_error');
		    });

		    $('p.error_message').show();
		    $.post('/genova/track_error_submit', $('#response').serialize());
		    f.preventDefault();
	    }

    });


    function leave_training(){
        window.scroll(0,0);
        $('#shadow').fadeOut();
    }

    function hide_training() {
        window.scroll(0,0);
        $('#shadow').fadeOut();
        $('.congrats').fadeOut();
    }

    $(".training").bind('click', show_training);
    $('.leave_training').bind('click', hide_training);    
    $(".cancel_training").bind('click', leave_training);


    $(document).on('click', 'a.training', show_training);    

});


function check_submit_2() {
    values = $('input[class=keyword]').map(function() {return $(this).val()})

	$('.error_message').hide();
	$('p.tag_error').attr('class', 'image_tag');
	$('input.input_error').attr('class', 'image_tag');
	$('table.input_error').attr('class', 'radio');

    // Compute the duplicates
    var duplicates = Object();
    duplicates[''] = true // So that you can't "duplicate" the empty string :)
    $('input[class=keyword]').map(function() {duplicates[$(this).val()] = true})
    var num_dupes = Object.keys(hash).length

    // Select them, and the blanks, in red
    if (num_dupes > 3) { // Give the guy a break
        $('input[class=keyword]').map(function() {
            var is_duplicated = duplicates[$(this).val()]
            var is_blank = $(this).val().length == 0
            if (is_duplicated || is_blank) {

                // Fill this in:
                // ... it should color this input and "Tag N" red

            }})

        // Add the message at the bottom
        // etc. ...

    }
}
