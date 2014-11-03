function submit_log() {
	current_content = $('input:hidden[name=activity_log]').attr('value');
	//new_content = current_content + ", " + action_string;
	//console.log(new_content)
    	//$('input:hidden[name=activity_log]').attr('value', new_content);
	var study, hitid, assignment_id, phase, workerid;
        study = $('input:hidden[name=study_number]').val()
        hitid = $('input:hidden[name=hit_id]').val()
        assignmentid = $('input:hidden[name=ass_id]').val()
        phase = $('input:hidden[name=phase]').val()
        workerid = $('input:hidden[name=worker_id]').val()
        $.ajax({
                url: '/genova/index',
                data: {
                        feedback: 'present',
                        study: study,
                        action_desc: action_type,
                        hitid: hitid,
                        assignmentid: assignmentid,
                        phase: phase,
                        workerid: workerid,
			logs: current_content
                },
                type: "POST",
                dataType: "json",
                success: function (json) {
                        console.log("ajax call successfull");
                        console.log(json)
                },
                error: function( xhr, status, errorThrown ) {
                        console.log( "Error: " + errorThrown);
                        console.log( "Status: " + status);
                },
                complete: function(xhr, status) {
                        console.log("Ajax complete");
                }
        });
}

function reportAbort(){
	// this is gonna work for some browsers but not for Safari 6.1.6
	submit_log();
}

function alter_log(action_detail) {
        //var action_type;
        //var action_time;
        //action_time = new Date($.now());
        //action_type = 'training entered';
        //action_information = { 'action_time': action_time,
        //                        'action_type': action_type};
        //console.log(action_information);
        action_string = JSON.stringify(action_detail);
        console.log(action_string);
        if($('input:hidden[name=activity_log]').length == 0){
                $('<input>').attr({
                        type: 'hidden',
                        id: 'activity_log',
                        name: 'activity_log',
                        value: action_string
                }).appendTo('form#response');
        }
        else {
                current_content = $('input:hidden[name=activity_log]').attr('value');
                new_content = current_content + ", " + action_string;
                console.log(new_content)
                $('input:hidden[name=activity_log]').attr('value', new_content);
        }	
}


function show_training() {
        var action_type;
        var action_time;
        action_time = new Date($.now());
        action_type = 'training entered';
        action_information = { 'action_time': action_time,
                                'action_type': action_type};
	alter_log(action_information);	
    	scrollTo(0,0);
	jQuery('#shadow').fadeIn().find('button').click(function(e) {
        	e.preventDefault();
        	if($('input[id=quiz_given]').val()=='0')
        	{
            		overall = 15;
        	}
        	else
        	{
            		overall = $('.quiz input[name=correct]').length;
        	}

        	if(overall == 15)
        	{
            		$('.image_set input').prop("disabled", false);
            		$('input:submit').prop('disabled', false);
            		$('.train_info').css('visibility', 'hidden');

            		$('#shadow').fadeOut();

            		if($('input[id=quiz_given]').val()=='1')
            		{
                		$('.congrats').fadeIn();
            		}
            		$('.trainbutton').fadeIn();
            		window.scroll(0,0);
        	}
        	else
        	{
            		$('div.err').remove();
            		$('div.cor').remove();
            		if($('div[name=batch1] input[name=empty]').length > 0 | $('div[name=batch1] input[name=incorrect]').length > 0)
            		{
                		$('.quiz div[name=batch1]').after('<div class="err" style="left: 1em; clear: both;">You have either filled incorrectly or not at all one of the fields in the first batch of questions!</div>');
            		}
            		else
            		{
                		$('.quiz div[name=batch1]').after('<div class="cor" style="left: 1em; clear: both;">Success!</div>');
            		}
            		if($('div[name=batch2] input[name=empty]').length > 0 | $('div[name=batch2] input[name=incorrect]').length > 0)
            		{
                		$('.quiz div[name=batch2]').after('<div class="err" style="left: 1em; clear: both;">You have either filled incorrectly or not at all one of the fields in the second batch of questions!</div>');
            		}
            		else
            		{
                		$('.quiz div[name=batch2]').after('<div class="cor" style="left: 1em; clear: both;">Success!</div>');
            		}
            		if($('div[name=batch3] input[name=empty]').length > 0 | $('div[name=batch3] input[name=incorrect]').length > 0)
            		{
                		$('.quiz div[name=batch3]').after('<div class="err" style="left: 1em; clear: both;">You have either filled incorrectly or not at all one of the fields in the third batch of questions!</div>');
            		}
            		else
            		{
                		$('.quiz div[name=batch3]').after('<div class="cor" style="left: 1em; clear: both;">Success!</div>');
            		}
        	}
    	});
}

function validate_training_entry () {
	var action_time;
	action_time = new Date($.now());
	action_information = { 'action_time': action_time, 
				'action_type': 'training form input', 
				'text_field_id': $(this).attr('id'), 
				'text_field_name': $(this).attr('name'),
				'text_field_value': $(this).attr('value') };
	alter_log(action_information);
    /* ... */ 
    	possible_answers = new Array("object", "orientation", "emotion", "technique", "time", "color",
                                 "emotion", "artistic genre");
    	user_answer = new Array(this.value.toLowerCase().trim());
    	if($(user_answer).not(possible_answers).length != 0)
    	{
        	if($(this).attr('id').length==4)
        	{
           		multiplier = $(this).attr('id')[3];
        	}
        	else
        	{
            		multiplier = $(this).attr('id')[3] + $(this).attr('id')[4];
        	}

        	if(multiplier < 6)
        	{
            		my_top = (multiplier-1.1)*23;
        	}
        	else if(multiplier < 11)
        	{
            		my_top = (multiplier-6.1)*23;
        	}
        	else
        	{
            		my_top = (multiplier-11.1)*23;
        	}
        	$(this).after('<span style="position: absolute; left: 200px; min-width: 200px; top: ' + my_top + 'px;" class="err">Not a possible answer!</span>');
        	$(this).attr("name", "incorrect");
    	}
    	else
    	{
        	$(this).parent().find('.err').remove();
        	position_input = $('.quiz input:text').index($(this));
        	correct_answers = new Array("technique", "time", "technique", 
                                    "emotion", "artistic genre", "technique", "emotion", "object",
                                    "emotion", "object", "time", "color", "emotion",
                                    "technique", "artistic genre");
        	if (correct_answers[position_input]==user_answer)
        	{
            		this.name="correct";
        	}
        	else
        	{
            		$(this).attr("name", "incorrect");
        	}
    	}        
}

function leave_training(){
	var action_type;
	var action_time;
	action_time = new Date($.now());
	action_type = 'leave training incomplete';
	action_information = { 'action_time': action_time, 
				'action_type': action_type};
    	alter_log(action_information);
	window.scroll(0,0);
    	$('#shadow').fadeOut();
}

function hide_training() {
	var action_type;
	var action_time;
	action_time = new Date($.now());
	action_type = 'leave training in a training=false condition';
	action_information = { 'action_time': action_time, 
				'action_type': action_type};
	alter_log(action_information);
    	window.scroll(0,0);
    	$('#shadow').fadeOut();
    	$('.congrats').fadeOut();
}

function validate (event) {
    	$('.error').removeClass('error');
    	$('.error_message').hide();
    
    	// First, downcase and trim whitespace from all tags and remove quotes
    	$('input.keyword').each(function () {
		$(this).val($(this).val().toLowerCase().trim().replace("'", "").replace('"', ''));
	});

    	// Go through each image's set of 5 tags
	sets = '.image_set';
	$(sets).each(function() {
        	var $curr_set = $(this);

        // Highlight all duplicate and blank tags in this set
		$curr_set.find('input.keyword').each(function() {
            // console.log('Duplicates for ', $(this).val(), 'is', 
            //             $curr_set.find('input.keyword:text[value="' + $(this).val() + '"]'))
			has_duplicate = $curr_set.find('input.keyword:text[value="' + $(this).val() + '"]').length > 1;
            		is_empty = $(this).val() == '';
			if(has_duplicate || is_empty)
				$(this).parent('p').addClass('error');
		})

        // The radio button is empty if there are two unchecked radio
        // buttons within this image set
        	var empty_radio = $curr_set.find('input[type="radio"]:not(:checked)').length > 1;
        	if (empty_radio)
            		$(this).find('.radio').addClass('error');
	})

    	if ($('.error').length > 0) {
        	event.preventDefault();  // Stops submit from happening
		var action_type;
		var action_time;
		action_time = new Date($.now());
		action_type = "training submission with mistakes";
        	action_information = { 'action_time': action_time,
                                	'action_type': action_type};
        	alter_log(action_information);
		$('p.error_message').show();
        // And now scroll the error message into view
        	$('html, body').animate({scrollTop: $(document).height()}, 'slow');
   	 }
}

$(function () {
    // Bind these functions to events
    // We do all bindings here, because this block won't be run
    // until the dom has loaded and the nodes exist

    	$(".training").bind('click', show_training);
    	$('.leave_training').bind('click', hide_training);
    	$(".cancel_training").bind('click', leave_training);
    	$('.quiz input:text').on("change", validate_training_entry)
	// log activation of the keywords in the HIT and put a time stamp on it
/*$('#test').bind('blur mousedown mouseup focus', function (e) {
    // This is your combined function
    // Inside here you can use e.type to find out whether it was a
    // "blur", "mousedown", "mouseup", etc...
});*/
	$('input.keyword').bind('focus', function(e) { 
		console.log("HIT keyword activated"); 
		var action_type;
		var action_time;
		action_time = new Date($.now());
		action_type = 'image tag ' + e.type;
		action_information = { 'action_time': action_time, 
					'action_type': action_type,
					'text_field_id': $(this).attr('id'), 
					'text_field_name': $(this).attr('name'),
					'text_field_value': $(this).attr('value') };
		alter_log(action_information);
	});

	$(document).on('click', 'a.training', show_training);
    	$('#response').on('submit', validate);
    	$(window).on('unload onbeforeunload pageleave beforeunload', reportAbort);
})





