
/*
$(document).ready(function () {
    $('ul.navbar-nav > li')
            .click(function (e) {
        $('ul.navbar-nav > li')
            .removeClass('active');
        $(this).addClass('active');
    });
});
 */

$(document).ready(function () {
    $('ul.navbar-nav > li').click(function (e) {
        $('ul.navbar-nav > li').css('background-color', 'transparent');
        $(this).css('background-color', '#c0c0c0');
    });
});
