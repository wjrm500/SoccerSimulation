$(document).ready(function() {
    setInterval(
        function () {
            $.get(
                '/simulation/check-progress',
                function (progress) {
                    progress *= 100;
                    if (progress > 99) {
                        $('#progress-bar').css({
                            'border-top-right-radius': '5px',
                            'border-bottom-right-radius': '5px'
                        });
                        setTimeout(
                            function () {
                                let universeKey = $('#progress-bar').data('universe-key');
                                window.location.href = `/simulation/${universeKey}`;
                            },
                            3000
                        );
                    }
                    $('#progress-bar').css('width', progress + '%');
                }
            )
        },
        500
    )
});