$(document).ready(function() {

    $('.pre-match-form').each(function() {
        let val = $(this).html();
        let prefix = val.charAt(0);
        if (prefix === '±') {
            return;
        } else if (prefix === '+') {
            val = val.substring(1);
        }
        val = parseFloat(val);
        $(this).css({
            'color': val === 0 ? 'black' : val > 0 ? 'limegreen' : 'red'
        });
    });

    $('.performance-index').each(function() {
        let val = 100 - ($(this).html() * 10);
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        let motm = $(this).closest('tr').data('manOfTheMatch');
        $(this).css({
            'backgroundColor': motm === 'True' ? 'black' : '',
            'color': `hsl(${hue}, ${saturation}%, 50%)`
        });
    });

    $('.fixture-players-club table td:first-child').click(function() {
        let url = '/simulation/player/' + this.dataset.playerId;
        url = getUrlWithParams(url);
        sendIFrameToUrl(url);
    });

    let numClubs = $('#form-tables-grid').data('num-clubs');
    let numProRel = Math.floor(numClubs / 5);
    let allPositions = [...Array(numClubs).keys()].map((x) => x + 1);
    let promPositions = allPositions.filter((x) => x <= numProRel);
    let relPositions = allPositions.filter((x) => x > numClubs - numProRel);

    $('.form-table tr:not(:first-child)').each(function() {
        debugger;
        let rank = parseInt($(this).find('td:first-child').html());
        if (promPositions.includes(rank)) {
            $(this).addClass('color-param-top4');
        } else if (relPositions.includes(rank)) {
            $(this).addClass('color-param-bottom4');
        }
        if (promPositions[promPositions.length - 1] === rank) {
            $(this).addClass('color-param-top4-border');
        } else if (relPositions[0] === rank) {
            $(this).addClass('color-param-bottom4-border');
        }
    })
    
    // The below is just a hacky fix for the fact that the "color-param-this" class for some reason doesn't get applied to the away team tables
    $('.form-table-container:nth-child(1) td:nth-child(2), .form-table-container:nth-child(3) td:nth-child(2)').each(function() {
        if ($(this).html().trim() === $('#fixture-summary-home-team-name').html().trim()) {
            $(this).closest('tr').addClass('color-param-this');
        }
    });
    $('.form-table-container:nth-child(2) td:nth-child(2), .form-table-container:nth-child(4) td:nth-child(2)').each(function() {
        if ($(this).html().trim() === $('#fixture-summary-away-team-name').html().trim()) {
            $(this).closest('tr').addClass('color-param-this');
        }
    });
})