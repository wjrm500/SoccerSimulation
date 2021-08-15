$(document).ready(function() {
    styleLeagueTable();
    $('#grid-item-standings').css('flex', 1);
    $('.grid-item').click(function() {
        $('.grid-item').css('flex', '');
        $(this).css('flex', 1);
    })

    $('#no-mobile-access-notice .close-icon').click(function() {
        $('#no-mobile-access-notice').slideUp();
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
        $(this).removeClass('clicked')
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