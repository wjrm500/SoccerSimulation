$(document).ready(function() {
    $('#player-performance-table .clickable-row').click(function() {
        $('#sometimes-iframe').attr('src', '/simulation/player/' + this.dataset.playerId);
        let iframe = document.getElementById('sometimes-iframe');
        let innerDoc = iframe.contentDocument || iframe.contentWindow.document;
        let playerGamesTable = innerDoc.getElementById('player-games-table');
        playerGamesTable.querySelectorAll('.clickable-row').forEach(item => {
            item.addEventListener('click', () => {
                $('#sometimes-iframe').attr('src', '/simulation/fixture/' + this.dataset.fixtureId);
            });
        });
    });

    $('#player-performance-table th').hover(
        function() {
            if (this.dataset.sort === 'unsorted') {
                let tableDownArrow = $(this).find('.table-down-arrow');
                tableDownArrow.css('display', 'inline');
                tableDownArrow.siblings('.table-arrow').css('display', 'none');
            }
            if (this.dataset.sort === 'sorted-descending') {
                let tableUpArrow = $(this).find('.table-up-arrow');
                tableUpArrow.css('display', 'inline');
                tableUpArrow.siblings('.table-arrow').css('display', 'none');
            }
            if (this.dataset.sort === 'sorted-ascending') {
                let tableUnsortedArrow = $(this).find('.table-unsorted-arrow');
                tableUnsortedArrow.css('display', 'inline');
                tableUnsortedArrow.siblings('.table-arrow').css('display', 'none');
            }
        },
        function() {
            $(this).find('.table-arrow').each(function() {
                $(this).css('display', 'none');
            });
            if (this.dataset.sort === 'unsorted') {
                let tableArrow = $(this).find('.table-down-arrow');
                tableArrow.css('display', 'none');
                $(this).find('.table-unsorted-arrow').css('display', 'inline');
            }
            if (this.dataset.sort === 'sorted-descending') {
                let tableArrow = $(this).find('.table-up-arrow');
                tableArrow.css('display', 'none');
                $(this).find('.table-down-arrow').css('display', 'inline');
            }
            if (this.dataset.sort === 'sorted-ascending') {
                let tableArrow = $(this).find('.table-unsorted-arrow');
                tableArrow.css('display', 'none');
                $(this).find('.table-up-arrow').css('display', 'inline');
            }
        }
    );

    $('#player-performance-table th:not(:nth-child(1))').click(function() {
        if (this.dataset.sort === 'unsorted') {
            sortHow = 'sorted-descending';
        }
        if (this.dataset.sort === 'sorted-descending') {
            sortHow = 'sorted-ascending';
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
                'rating': $(this).find('td:eq(5)').text(),
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
            tr.find('td:eq(0)').html(datum['rank']);
            tr.find('td:eq(1)').html(datum['name']);
            tr.find('td:eq(2)').text(datum['games']);
            tr.find('td:eq(3)').text(datum['goals']);
            tr.find('td:eq(4)').text(datum['assists']);
            tr.find('td:eq(5)').text(datum['rating']);
        }
        this.dataset.sort = sortHow;
        $(this).siblings().each(function() {
            this.dataset.sort = 'unsorted';
            $(this).find('.table-arrow').css('display', 'none');
            $(this).find('.table-unsorted-arrow').css('display', 'inline');
        });
    });
});