$(document).ready(function() {
    $('#links').css('display', 'none');
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
                        $('#time-remaining-text').html('Waiting for database to respond...')
                        let checkDatabase = setInterval(
                            function() {
                                $.get(
                                    `/simulation/check-universe-key-exists-in-database/${universeKey}`,
                                    function (complete) {
                                        if (JSON.parse(complete)) {
                                            clearInterval(checkDatabase);
                                            window.location.href = `/simulation/${universeKey}`;
                                        }
                                    }
                                )
                            },
                            5000
                        );
                    }
                    $('#progress-bar').css('width', progress + '%');
                    let currentTime = (new Date()).getTime();
                    let millisecondsPassed = currentTime - originTime;
                    let millisecondsPerPctProgress = millisecondsPassed / progress;
                    let pctProgressRemaining = 100 - progress;
                    let millisecondsRemaining = millisecondsPerPctProgress * pctProgressRemaining;
                    let estSecondsRemaining = Math.round(millisecondsRemaining / 1000);
                    estSecondsRemaining = isFinite(estSecondsRemaining) ? estSecondsRemaining : '???';
                    if (!isFinite(estSecondsRemaining)) {
                        originTime = (new Date()).getTime(); // Reset origin time if bar not moving yet
                    }
                    $('#seconds-remaining').html(estSecondsRemaining);
                }
            )
        },
        250
    );
    $('#submit-email').click(function () {
        let submit = $(this);
        submit.find('#text').hide();
        submit.find('#spinner').show();
        let emailInput = $('#email-input').val();
        if (validateEmail(emailInput)) {
            $.post(
                '/simulation/store-email',
                {
                    universe_key: universeKey,
                    email_input: emailInput
                },
                function (response) {
                    $('#email-input').hide();
                    submit.css('width', '100%');
                    submit.find('#spinner').hide();
                    submit.find('#text').show();
                    submit.find('#text').html('Email address successfully submitted');
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