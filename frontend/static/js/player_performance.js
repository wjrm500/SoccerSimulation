$(document).ready(function() {
    $('.view-button').click(function() {
        const views = ['attributes', 'performance'];
        let view = $(this).data('view');
        $(this).addClass('clicked');
        $('.view-button').not('#' + $(this).attr('id')).each((x, y) => $(y).removeClass('clicked'));
        $('.pp-' + view).show();
        let otherView = views[1 - views.indexOf(view)];
        $('.pp-' + otherView).hide();
    });

    $('.player-rating').each(function() {
        let val = 100 - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'color': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });

    $('.pp-attributes').each(function() {
        let val = 125 - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'color': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });

    $('#filter-by').change(function() {
        let filterBy = $(this).val();
        $('#filter-detail-container').show();
        $('.filter-detail#filter-' + filterBy.toLowerCase()).show();
        $('.filter-detail:not(#filter-' + filterBy.toLowerCase() + ')').hide();
    });

    let playerSearchTimeout;

    $('#filter-player input').keyup(function() {
        clearTimeout(playerSearchTimeout);
        let thisThing = $(this);
        playerSearchTimeout = setTimeout(function() {
            $('#player-performance-proper-table tr:not(:first-child)').show();
            console.log(thisThing);
            let searchVal = thisThing.val().toLowerCase();
            $('#player-performance-proper-table tr:not(:first-child)').each(function() {
                let playerName = $(this).find('td:nth-child(2)').html().toLowerCase();
                playerName = playerName.substring(0, playerName.indexOf('<'));
                if (!playerName.includes(searchVal)) {
                    $(this).hide();
                }
            });
            alternateRowColors();
        }, 200);
    });

    $('#filter-club select').change(function() {
        $('#player-performance-proper-table tr:not(:first-child)').show();
        let clubId = $(this).val();
        if (clubId !== 'all') {
            $('#player-performance-proper-table tr:not(:first-child)').each(function() {
                if (clubId != $(this).find('td:nth-child(2) span').data('clubId')) {
                    $(this).hide();
                }
            });
        }
        alternateRowColors();
    });

    $('#filter-position select').change(function() {
        $('#player-performance-proper-table tr:not(:first-child)').show();
        let position = $(this).val();
        if (position !== 'all') {
            $('#player-performance-proper-table tr:not(:first-child)').each(function() {
                if (position != $(this).find('td:nth-child(3)').html()) {
                    $(this).hide();
                }
            });
        }
        alternateRowColors();
    });

    $('#player-performance-proper-table .clickable-row').click(function() {
        let url = '/simulation/player/' + this.dataset.playerId;
        sendIFrameToUrl(url);
    });

    $('.stretched-grid-item').css('border-bottom', 'none');

    function alternateRowColors() {
        $('#player-performance-proper-table tr:not(:first-child):visible').each(function(index) {
            if (index % 2 !== 0) {
                $(this).css('backgroundColor', '#eeeeee');
            } else {
                $(this).css('backgroundColor', '#ffffff');
            }
        });
    }

    $('#player-performance-proper-table th:nth-child(n + 4)').hover(
        function() {
            $(this).addClass('hovered');
        },
        function() {
            $(this).removeClass('hovered');
        }
    )

    $('#player-performance-proper-table th:nth-child(n + 4)').click(function() {
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
        $('#player-performance-proper-table tr:not(:nth-child(1))').each(function() {
            let datum = {
                'playerId': this.dataset.playerId,
                'rank': $(this).find('td:eq(0)').text(),
                'name': $(this).find('td:eq(1)').html(),
                'position': $(this).find('td:eq(2)').text(),
                'age': $(this).find('td:eq(3)').text(),
                'rating': $(this).find('td:eq(4)').text(),
                'offence': $(this).find('td:eq(5)').text(),
                'spark': $(this).find('td:eq(6)').text(),
                'technique': $(this).find('td:eq(7)').text(),
                'defence': $(this).find('td:eq(8)').text(),
                'authority': $(this).find('td:eq(9)').text(),
                'fitness': $(this).find('td:eq(10)').text(),
                'games': $(this).find('td:eq(11)').text(),
                'goals': $(this).find('td:eq(12)').text(),
                'assists': $(this).find('td:eq(13)').text(),
                'mvps': $(this).find('td:eq(14)').text(),
                'performanceIndex': $(this).find('td:eq(15)').text(),
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
            let tr = $('#player-performance-proper-table tr:eq(' + (i + 1) + ')');
            tr.get(0).dataset.playerId = datum['playerId'];
            tr.find('td:eq(0)').text(datum['rank']);
            tr.find('td:eq(1)').html(datum['name']);
            tr.find('td:eq(2)').text(datum['position']);
            tr.find('td:eq(3)').text(datum['age']);
            tr.find('td:eq(4)').text(datum['rating']);
            tr.find('td:eq(5)').text(datum['offence']);
            tr.find('td:eq(6)').text(datum['spark']);
            tr.find('td:eq(7)').text(datum['technique']);
            tr.find('td:eq(8)').text(datum['defence']);
            tr.find('td:eq(9)').text(datum['authority']);
            tr.find('td:eq(10)').text(datum['fitness']);
            tr.find('td:eq(11)').text(datum['games']);
            tr.find('td:eq(12)').text(datum['goals']);
            tr.find('td:eq(13)').text(datum['assists']);
            tr.find('td:eq(14)').text(datum['mvps']);
            tr.find('td:eq(15)').text(datum['performanceIndex']);
        }
        this.dataset.sort = sortHow;
        $(this).siblings().each(function() {
            $(this).get(0).dataset.sort = 'unsorted';
            $(this).removeClass('clicked');
        });
    });

    $("#age-range-slider").slider({
        range: true,
        min: 15,
        max: 45,
        values: [25, 35],
        slide: function(event, ui) {
            let lowerBound = ui.values[0];
            let upperBound = ui.values[1];
            $('#age-range-slider-lower-bound').html(lowerBound);
            $('#age-range-slider-upper-bound').html(upperBound);
            $('#player-performance-proper-table tr:not(:first-child)').show();
            $('#player-performance-proper-table tr:not(:first-child)').each(function() {
                let age = $(this).find('td:nth-child(4)').html();
                if (age < lowerBound || age > upperBound) {
                    $(this).hide();
                }
            });
            alternateRowColors();
        }
    });
});