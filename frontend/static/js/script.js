$(document).ready(function() {
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
        $('#league-table tr').each(function() {
            $(this).find('td:nth-child(2)').css({'color': 'black', 'font-style': 'normal'});
        })
        $('#results tr').css('display', 'table-row');
        $('#results .gap-row').data('gap-row-remove', false);

        if (!controlPressed && !$(this).data('controlClicked')) {
            let iframe = document.getElementById('sometimes-iframe');
            let url = '/simulation/club/' + this.dataset.clubId;
            window.iframeHistory.push(url);
            window.iframeHistoryPointer = window.iframeHistory.length - 1;
            iframe.src = url;
        }

        if (controlPressed && !$(this).data('controlClicked')) {
            $(this).data('controlClicked', true);

            // Add / remove clubs from clubsPressed array, keeping a maximum length of 2
            if (clubsPressed.length === 2) {
                let unpressedClub = clubsPressed.shift();
                unpressedClub.data('controlClicked', false);
            }
            clubsPressed.push($(this));
            
            // Style league table
            for (let club of clubsPressed) {
                club.find('td:nth-child(2)').css({'color': 'blue', 'font-style': 'italic'});
            }

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
            $(this).data('controlClicked', false);
            $(this).siblings().each(function() {
                $(this).data('controlClicked', false);
            })
            clubsPressed = [];
        }
    });

    $('#main a').click(function(e) {
        e.preventDefault();
        let iframe = document.getElementById('sometimes-iframe');
        let url = $(this).data('url');
        if (window.iframeHistoryPointer !== (window.iframeHistory.length - 1)) {
            window.iframeHistory.pop();
            window.iframeHistory.push(url);
        } else {
            window.iframeHistory.push(url);
        }
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.src = url;
    });

    $('.player-performance-table .clickable-row').click(function() {
        let iframe = document.getElementById('sometimes-iframe');
        let url = '/simulation/player/' + this.dataset.playerId;
        window.iframeHistory.push(url);
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.src = url;
    });

    $('#results .clickable-row').click(function() {
        let iframe = document.getElementById('sometimes-iframe');
        let url = '/simulation/fixture/' + this.dataset.fixtureId;
        window.iframeHistory.push(url);
        window.iframeHistoryPointer = window.iframeHistory.length - 1;
        iframe.src = url;
    });

    $('.player-performance-table th').hover(
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

    $('.player-performance-table th:not(:nth-child(1))').click(function() {
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
        $('.player-performance-table tr:not(:nth-child(1))').each(function() {
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
            let tr = $('.player-performance-table tr:eq(' + (i + 1) + ')');
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

    $('.rating-span').each(function() {
        let val = 100 - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'backgroundColor': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });
});