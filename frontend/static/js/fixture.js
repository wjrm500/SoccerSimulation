$(document).ready(function() {
    $('.fixture-players-club table td:last-child').each(function() {
        let val = 100 - ($(this).html() * 10);
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        let motm = $(this).closest('tr').data('manOfTheMatch');
        $(this).css({
            'backgroundColor': motm === 'True' ? 'black' : '',
            'color': `hsl(${hue}, ${saturation}%, 50%)`
        })
    });

$('.fixture-players-club table td:first-child').click(function() {
        let url = '/simulation/player/' + this.dataset.playerId;
        if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
            parent.iframeHistory.pop();
            parent.iframeHistory.push(url);
        } else {
            parent.iframeHistory.push(url);
        }
        parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
        document.location.href = url;
    });
})