$(document).ready(function() {
    window.onresize = function(){ location.reload(); }

    $('#copy-simulation-key').click(function() {
        let textToCopy = $('#input-simulation-key').html();
        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                $('#simulation-key-value .my-tooltiptext').css('visibility', 'visible');
                setTimeout(function() {
                    $('#simulation-key-value .my-tooltiptext').css('visibility', 'hidden');
                }, 1000);
            });
    });

    styleLeagueTable();

    window.iframeHistoryPointer = 0;
    window.iframeHistory = [];

    let controlPressed = false;
    let clubsPressed = [];

    $(document).keydown(function(e){
        if (e.which == 17) {
            controlPressed = true;
        }
    });
    
    $(document).keyup(function(){
        controlPressed = false;
    });

    $('#league-table tr').click(function() {
        // Reset CSS
        $('#results tr').css('display', 'table-row');
        $('#results .gap-row').data('gap-row-remove', false);

        if (!controlPressed && !$(this).hasClass('controlClicked')) {
            $('#sometimes-iframe').hide();
            $('#sometimes-data-container #spinner').show();
            let iframe = document.getElementById('sometimes-iframe');
            let url = '/simulation/club/' + this.dataset.clubId;
            window.iframeHistory.push(url);
            window.iframeHistoryPointer = window.iframeHistory.length - 1;
            iframe.onload = function () {
                $('#sometimes-data-container #spinner').hide();
                $('#sometimes-iframe').show();
            }
            iframe.src = url;
        }

        if (controlPressed && !$(this).hasClass('controlClicked')) {
            $(this).addClass('controlClicked');

            // Add / remove clubs from clubsPressed array, keeping a maximum length of 2
            if (clubsPressed.length === 2) {
                let unpressedClub = clubsPressed.shift();
                unpressedClub.removeClass('controlClicked');
            }
            clubsPressed.push($(this));

            // Highlight relevant results
            let clubIdsPressed = clubsPressed.map(x => x.data('clubId'));
            let matchFoundInGameweek;
            $('#results .result').each(function() {
                if ($(this).prev('tr').hasClass('date-row')) {
                    matchFoundInGameweek = false;
                }
                if ($(this).css('display') === 'none') {
                    return true;
                }
                let homeClubId = $(this).find('.result-home-club-name').data('clubId');
                let awayClubId = $(this).find('.result-away-club-name').data('clubId');
                let checker = (arr, target) => target.every(v => arr.includes(v));
                if (!checker([homeClubId, awayClubId], clubIdsPressed)) {
                    $(this).closest('tr').css('display', 'none');
                } else {
                    matchFoundInGameweek = true;
                    return true;
                }
                if ($(this).nextAll('tr:visible:first').hasClass('gap-row') && !matchFoundInGameweek) {
                    $(this).nextAll('.gap-row:first').data('gap-row-remove', true);
                    $(this).prevAll('.date-row:first').css('display', 'none');
                }
            });
            if (clubsPressed.length < 2) {
                $('#results .gap-row').css('display', 'table-row');
            } else {
                $('#results').css('height', 'auto');
                $('#results .gap-row').each(function() {
                    if ($(this).data('gap-row-remove')) {
                        $(this).css('display', 'none');
                    }
                });
            }
        } else {
            $(this).removeClass('controlClicked');
            $(this).siblings().each(function() {
                $(this).removeClass('controlClicked');
            })
            clubsPressed = [];
        }
    });

    $('#main a').click(function(e) {
        e.preventDefault();
        $('#sometimes-iframe').hide();
        $('#sometimes-data-container #spinner').show();
        let iframe = document.getElementById('sometimes-iframe');
        let url = $(this).data('url');
        if (window.iframeHistoryPointer !== (window.iframeHistory.length - 1)) {
            window.iframeHistory.pop();
            window.iframeHistory.push(url);
        } else {
            window.iframeHistory.push(url);
        }
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.onload = function () {
            $('#sometimes-data-container #spinner').hide();
            $('#sometimes-iframe').show();
        }
        iframe.src = url;
    });

    $('.player-performance-table .clickable-row').click(function() {
        $('#sometimes-iframe').hide();
        $('#sometimes-data-container #spinner').show();
        let iframe = document.getElementById('sometimes-iframe');
        let url = '/simulation/player/' + this.dataset.playerId;
        window.iframeHistory.push(url);
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.onload = function () {
            $('#sometimes-data-container #spinner').hide();
            $('#sometimes-iframe').show();
        }
        iframe.src = url;
    });

    $('#results .clickable-row').click(function() {
        $('#sometimes-iframe').hide();
        $('#sometimes-data-container #spinner').show();
        let iframe = document.getElementById('sometimes-iframe');
        let url = '/simulation/fixture/' + this.dataset.fixtureId;
        window.iframeHistory.push(url);
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.onload = function () {
            $('#sometimes-data-container #spinner').hide();
            $('#sometimes-iframe').show();
        }
        iframe.src = url;
    });

    $('#player-performance-table th:nth-child(n + 3)').hover(
        function() {
            $(this).addClass('hovered');
        },
        function() {
            $(this).removeClass('hovered');
        }
    )

    $('#player-performance-table th:nth-child(n + 3)').click(function() {
        $(this).removeClass('clicked');
        if (this.dataset.sort === 'unsorted') {
            sortHow = 'sorted-descending';
            $(this).addClass('clicked');
        }
        if (this.dataset.sort === 'sorted-descending') {
            sortHow = 'sorted-ascending';
            $(this).addClass('clicked');
        }
        if (this.dataset.sort === 'sorted-ascending') {
            sortHow = 'unsorted';
        }
        let data = [];
        let metric = $(this).data('metric');
        $('#player-performance-table tr:not(:nth-child(1))').each(function() {
            let datum = {
                'playerId': this.dataset.playerId,
                'rank': $(this).find('td:eq(0)').text(),
                'name': $(this).find('td:eq(1)').html(),
                'games': $(this).find('td:eq(2)').text(),
                'goals': $(this).find('td:eq(3)').text(),
                'assists': $(this).find('td:eq(4)').text(),
                'performanceIndex': $(this).find('td:eq(5)').text(),
            };
            data.push(datum);
        });
        data.sort(function(a, b) {
            if (sortHow === 'sorted-descending') {
                return b[metric] - a[metric]; 
            }
            if (sortHow === 'sorted-ascending') {
                return a[metric] - b[metric];   
            }
            if (sortHow === 'unsorted') {
                return a['rank'] - b['rank'];
            }
        });
        for (let i = 0; i < data.length; i++) {
            let datum = data[i];
            let tr = $('#player-performance-table tr:eq(' + (i + 1) + ')');
            tr.get(0).dataset.playerId = datum['playerId'];
            tr.find('td:eq(0)').text(datum['rank']);
            tr.find('td:eq(1)').html(datum['name']);
            tr.find('td:eq(2)').text(datum['games']);
            tr.find('td:eq(3)').text(datum['goals']);
            tr.find('td:eq(4)').text(datum['assists']);
            tr.find('td:eq(5)').text(datum['performanceIndex']);
        }
        this.dataset.sort = sortHow;
        $(this).siblings().each(function() {
            $(this).get(0).dataset.sort = 'unsorted';
            $(this).removeClass('clicked');
        });
        recolorAttributes();
    });

    $('.rating-span').each(function() {
        let val = 100 - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'backgroundColor': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });
});

function styleLeagueTable() {
    let leagueTable = $('#league-table')
    let numClubs = leagueTable.find('tr').length - 1;
    let numProRel = Math.floor(numClubs / 5);

    // Colour promoted rows
    let proRows = leagueTable.find(`tr:not(:nth-child(1)):nth-child(-n + ${numProRel + 1})`);
    proRows.css('backgroundColor', 'lightgreen');
    proRows.hover(
        function () {
            $(this).css('backgroundColor', '#19a519');
        },
        function () {
            $(this).css('backgroundColor', 'lightgreen');
        }
    );
    
    // Colour relegated rows
    let relRows = leagueTable.find(`tr:nth-last-child(-n + ${numProRel})`);
    relRows.css('backgroundColor', 'lightpink');
    relRows.hover(
        function () {
            $(this).css('backgroundColor', '#ff5e76');
        },
        function () {
            $(this).css('backgroundColor', 'lightpink');
        }
    );

    // Add dashed lines to visually separate promoted and relegated rows from rest of table
    leagueTable.find(`tr:nth-child(${numProRel + 1})`).css(
        'borderBottom', '1px dashed black'
    );
    leagueTable.find(`tr:nth-last-child(${numProRel})`).css(
        'borderTop', '1px dashed black'
    );
}

function recolorAttributes() {
    $('.player-rating, .pp-attributes').each(function() {
        let subtractFrom = $(this).hasClass('pp-attributes') ? 125 : 100;
        let val = subtractFrom - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'color': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });
}