$(document).ready(function() {
    if (parent.iframeHistoryPointer === 0) {
        backButton.disable();
    }
    if (parent.iframeHistoryPointer === (parent.iframeHistory.length - 1)) {
        forwardButton.disable();
    }

    $('#refresh').click(function() {
        window.frameElement.contentWindow.location.reload();
    });

    $('#history-back').click(function() {
        parent.iframeHistoryPointer -= 1;
        document.location.href = parent.iframeHistory[parent.iframeHistoryPointer];
    });

    $('#history-forward').click(function() {
        console.log(parent.iframeHistoryPointer);
        console.log(parent.iframeHistory);
        parent.iframeHistoryPointer += 1;
        document.location.href = parent.iframeHistory[parent.iframeHistoryPointer];
    });

    $('a').click(function(e) {
        e.preventDefault();
        let url = $(this).data('url');
        sendIFrameToUrl(url);
    });

    $('.fixture-summary-goal-player').click(function() {
        let url = '/simulation/player/' + this.dataset.playerId;
        sendIFrameToUrl(url);
    });

    $('#player-game-table .clickable-row').click(function() {
        let url = '/simulation/fixture/' + this.dataset.fixtureId;
        if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
            parent.iframeHistory.pop();
            parent.iframeHistory.push(url);
        } else {
            parent.iframeHistory.push(url);
        }
        parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
        document.location.href = url;
    });

    $('.rating-span').each(function() {
        let val = 100 - $(this).html();
        let hue = Math.floor((100 - val) * 120 / 100);
        let saturation = Math.abs(val - 50) / 50 * 100;
        $(this).css({
            'backgroundColor': `hsl(${hue}, ${saturation}%, 50%)`,
        });
    });

    $('#club-player-performance-table th:nth-child(n + 3)').hover(
        function() {
            $(this).addClass('hovered');
        },
        function() {
            $(this).removeClass('hovered');
        }
    )

    $('#club-player-performance-table th:nth-child(n + 3)').click(function() {
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
        $('#club-player-performance-table tr:not(:nth-child(1))').each(function() {
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
            let tr = $('#club-player-performance-table tr:eq(' + (i + 1) + ')');
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
})

const backButton = {
    element: $('#history-back'),
    disable: function() {
        this.element.attr('disabled', true);
        this.element.addClass('history-button-disabled');
    },
    enable: function() {
        this.element.attr('disabled', false);
        this.element.removeClass('history-button-disabled');
    }
}

const forwardButton = {
    element: $('#history-forward'),
    disable: function() {
        this.element.attr('disabled', true);
        this.element.addClass('history-button-disabled');
    },
    enable: function() {
        this.element.attr('disabled', false);
        this.element.removeClass('history-button-disabled');
    }
}

function sendIFrameToUrl(url) {
    if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
        parent.iframeHistory.pop();
        parent.iframeHistory.push(url);
    } else {
        parent.iframeHistory.push(url);
    }
    parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
    document.location.href = url;
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