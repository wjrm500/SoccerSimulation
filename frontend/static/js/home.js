$(document).ready(function () {
    $('#new-simulation-button').click(function () {
        window.location.href = '/new';
    });

    $('#new-simulation-form').submit(function() {
        $('#simulate-button #text').hide();
        $('#simulate-button #spinner').show();
        $('#progress-bar-container').show();
        setTimeout(function () {
            setInterval(function () {
                $.get(
                    '/simulation/check-progress',
                    function (progress) {
                        progress *= 100;
                        if (progress > 99.5) {
                            $('#progress-bar').css({
                                'border-top-right-radius': '5px',
                                'border-bottom-right-radius': '5px'
                            });
                        }
                        $('#progress-bar').css('width', progress + '%');
                    }
                )
            }, 400);
        }, 2000)
    });
})