function validate (event) {
    $('.error').removeClass('error')
	$('.error_message').hide();
    $.post('/genova/track_error_submit', $('#response').serialize());
    
    // First, downcase and trim whitespace from all tags
    $('input.keyword').each(function () {$(this).val($(this).val().toLowerCase().trim())})

    // Go through each image's set of 5 tags
	sets = '.image_set';
	$(sets).each(function() {
        var $curr_set = $(this)

        // Highlight all duplicate and blank tags in this set
		$curr_set.find('input.keyword').each(function() {
			has_duplicate = $curr_set.find('input.keyword:text[value="'
                                           + $(this).val() + '"]').length > 1
            is_empty = $(this).val() == ''
			if(has_duplicate || is_empty)
				$(this).parent('p').addClass('error')
		})

        // The radio button is empty if there are two unchecked radio
        // buttons within this image set
        var empty_radio = $curr_set.find('input[type="radio"]:not(:checked)').length > 1
        if (empty_radio)
            $(this).find('.radio').addClass('error')
	})

    if ($('.error').length > 0) {
        event.preventDefault()
	    $('p.error_message').show();
        // And now scroll the error message into view
        $('html, body').animate({scrollTop: $(document).height()}, 'slow');
    }
}


$( function () {
    $('#response').on('submit', validate)
})