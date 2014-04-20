function show_training() {
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
            // Then the user passes!

            // Let's enable the hit...
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
    window.scroll(0,0);
    $('#shadow').fadeOut();
}

function hide_training() {
    window.scroll(0,0);
    $('#shadow').fadeOut();
    $('.congrats').fadeOut();
}


$(function () {
    // Bind these functions to events
    // We do all bindings here, because this block won't be run
    // until the dom has loaded and the nodes exist
    $(".training").bind('click', show_training);
    $('.leave_training').bind('click', hide_training);
    $(".cancel_training").bind('click', leave_training);
    $('.quiz input:text').on("change", validate_training_entry)

    $(document).on('click', 'a.training', show_training);
})
