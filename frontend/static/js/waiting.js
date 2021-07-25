$(document).ready(function() {
    setInterval(
        function () {
            $.get(
                '/simulation/check-progress',
                function (progress) {
                    progress *= 100;
                    $('#simulation-progress').html(progress);
                }
            )
        },
        500
    )
});