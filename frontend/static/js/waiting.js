$(document).ready(function() {
    let checkProgress = setInterval(
        function () {
            $.get(
                '/simulation/check-progress',
                function (progress) {
                    progress *= 100;
                    if (progress === 100) {
                        clearInterval(checkProgress);
                        $('#progress-bar').css({
                            'border-top-right-radius': '5px',
                            'border-bottom-right-radius': '5px'
                        });
                        setTimeout(
                            function () {
                                let universeKey = $('#progress-bar').data('universe-key');
                                window.location.href = `/simulation/${universeKey}`;
                            },
                            2500
                        );
                    }
                    $('#progress-bar').css('width', progress + '%');
                }
            )
        },
        500
    )
});