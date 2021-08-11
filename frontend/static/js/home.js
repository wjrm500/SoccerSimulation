$(document).ready(function () {
    $('#new-simulation-button').click(function () {
        $(this).find('#text').hide();
        $(this).find('#spinner').show();
        window.location.href = '/new';
    });

    $('#new-simulation-form').submit(function () {
        let simulateButton = $(this).find('.simulate-button')
        simulateButton.find('#text').hide();
        simulateButton.find('#spinner').show();
        return true;
    });
})