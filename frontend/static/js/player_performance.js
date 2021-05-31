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
});