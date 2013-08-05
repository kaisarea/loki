function select_tab() {
    $('.stats .tab.selected').removeClass('selected')
    $(this).addClass('selected')

    // Insert this tab's description into the details box
    $('#details_box').html($(this).find('.details').html())
}

$(document).ready(function() {
    $('.stats .tab').mouseenter(select_tab)
    select_tab.call($('.stats .tab').first()[0])
})