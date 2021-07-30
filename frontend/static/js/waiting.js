$(document).ready(function() {
    let universeKey = $('#progress-bar').data('universe-key');
    let originTime = (new Date()).getTime();
    let checkProgress = setInterval(
        function () {
            $.get(
                `/simulation/check-progress/${universeKey}`,
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
                                window.location.href = `/simulation/${universeKey}`;
                            },
                            2500
                        );
                    }
                    $('#progress-bar').css('width', progress + '%');
                    let currentTime = (new Date()).getTime();
                    let millisecondsPassed = currentTime - originTime;
                    let millisecondsPerPctProgress = millisecondsPassed / progress;
                    let pctProgressRemaining = 100 - progress;
                    let millisecondsRemaining = millisecondsPerPctProgress * pctProgressRemaining;
                    let estSecondsRemaining = Math.round(millisecondsRemaining / 1000);
                    $('#seconds-remaining').html(estSecondsRemaining);
                }
            )
        },
        500
    );
    $('#submit-email').click(function () {
        let emailInput = $('#email-input').val();
        if (validateEmail(emailInput)) {
            $.post(
                '/simulation/store-email',
                {
                    universe_key: universeKey,
                    email_input: emailInput
                },
                function (response) {
                    alert('done');
                }
            );
        } else {
            alert('Invalid email address entered');
        }
    });
});

function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}