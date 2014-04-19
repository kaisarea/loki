



function check_submit() {
    clear_errors();

    // Compute the duplicates
    var duplicates = Object();
    var frequency_of_occurrence = 0;
    duplicates[''] = true; // So that you can't "duplicate" the empty string :)
    var keywords = 'input[class=keyword]';
    $(keywords).map(function() {
	frequency_of_occurrence = $('input.keyword:text[value="' + $(this).val() + '"]').length;
	if(frequency_of_occurrence > 1)
	{
		duplicates[$(this).val()] = true;
	}
    });
    var num_dupes = Object.keys(duplicates).length;
    var num_blanks = $('input.keyword:text[value=""]').length; 
    var troubles = num_blanks + num_dupes;
    // Compute the blank checkboxes
    var blank_checkboxes = $('td input:radio:not(:checked)');
    var num_blank_checkboxes = blank_checkboxes.length;

    // Select them, and the blanks, in red
    if (troubles > 3) 
    { // Give the guy a break
        $(keywords).map(function() 
	{
            var is_duplicated = duplicates[$(this).val()];
            var is_blank = $(this).val().length == 0;
            if (is_duplicated || is_blank) 
	    {
		$(this).attr('class', 'input_error');
		$(this).parents('tr').find('p.image_tag').attr('class', 'tag_error');
                // Fill this in:
                // ... it should color this input and "Tag N" red
		//if(is_blank)
		//{
	//		num_blanks = num_blanks + 1;
		//}
            }
         });

        $(blank_checkboxes).map(function() 
        {
		$(this).parents('table.radio').attr('class', 'input_error');
            // Fill this in:
            // ... it should give this checkbox a red border

        });
	$('input:radio:checked').parents('table.input_error').attr('class', 'radio');
	$('p.error_message').show();
      }
}
	
        // Add the message at the bottom
        // etc. ...

function clear_errors() {
    //var keywords = 'input[class=keyword]'
    //var checkboxes = $('td input:radio')
    
    // Clear error message at bottom
	$('.error_message').hide();
	$('p.tag_error').attr('class', 'image_tag');
	$('input.input_error').attr('class', 'keyword');
	$('table.input_error').attr('class', 'radio');

    // Clear keywords
    //$(keywords).each(function () {

        // Fill this in
        // it should make the keyword unhighlighted

    //})

    // Clear checkboxes
    //$(checkboxes).each(function () {

        // Fill this in
        // it should make the keyword unhighlighted

    //})
}
