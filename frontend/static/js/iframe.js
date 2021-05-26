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
        if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
            parent.iframeHistory.pop();
            parent.iframeHistory.push(url);
        } else {
            parent.iframeHistory.push(url);
        }
        parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
        document.location.href = url;
    });

    // $('a').click(function() {
    //     url = $(this).attr('href');
    //     if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
    //         parent.iframeHistory.pop();
    //         parent.iframeHistory.push(url);
    //     } else {
    //         parent.iframeHistory.push(url);
    //     }
    //     parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
    // })

    $('.fixture-summary-goal-player').click(function() {
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