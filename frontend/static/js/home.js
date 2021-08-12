$(document).ready(function () {
    $('.simulation-button').click(function () {
        $(this).find('#text').hide();
        $(this).find('#spinner').show();
        window.location.href = $(this).data('url');
    });

    $('.simulation-form').submit(function () {
        let simulateButton = $(this).find('.simulate-button')
        simulateButton.find('#text').hide();
        simulateButton.find('#spinner').show();
        return true;
    });

    $('#existing-how').change(function() {
        let val = $(this).val();
        $('.hideable-div').css('display', 'none');
        $('.hideable-div input').prop('required', false);
        let divToShow = $(`#${val}`);
        divToShow.css('display', 'flex');
        divToShow.find('input').prop('required', true);
    });

    setTimeout(function() {
        $('#error').slideUp();
    }, 2000);
});