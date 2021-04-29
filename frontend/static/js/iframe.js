$(document).ready(function() {
    if (parent.iframeHistoryPointer === 0) {
        backButton.disable();
    }
    if (parent.iframeHistoryPointer === (parent.iframeHistory.length - 1)) {
        forwardButton.disable();
    }

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
    })
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