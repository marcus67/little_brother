
$(document).ready(function () {
    $('ul.navbar-nav li')
            .click(function (e) {
        $('ul.navbar-nav li')
            .removeClass('active');
        $(e).addClass('active');
    });
});

/*
$(document).ready(function () {
    $('ul.navbar-nav > li').click(function (e) {
        $('ul.navbar-nav > li').css('background-color', 'transparent');
        $(e).css('background-color', '#c0c0c0');
    });
});
*/
