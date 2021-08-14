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