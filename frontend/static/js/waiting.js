$(document).ready(function() {
    setInterval(
        function () {
            $.get(
                '/simulation/check-progress',
                function (progress) {
                    progress *= 100;
                    $('#simulation-progress').html(progress);
                    if (progress > 99) {
                        alert('done');
                        let universeKey = $('#simulation-progress').data('universe-key');
                        window.location.href = `/simulation/${universeKey}`;
                    }
                }
            )
        },
        500
    )
});