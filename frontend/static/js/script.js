$(document).ready(function() {
    $('.clickable-row').click(function() {
        $('#sometimes-iframe').attr('src', '/simulation/player/' + $(this).data('playerId'));
    });
});