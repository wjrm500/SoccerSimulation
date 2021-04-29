$(document).ready(function() {
    // let iframe = document.getElementById('sometimes-iframe');
    // iframe.src = '/simulation/player/' + this.dataset.playerId;
    // iframe.onload = function() {
    //     let innerDoc = iframe.contentDocument || iframe.contentWindow.document;
    //     let playerGameTable = innerDoc.getElementById('player-game-table');
    //     playerGameTable.querySelectorAll('.clickable-row').forEach(item => {
    //         item.addEventListener('click', () => {
    //             iframe.src = '/simulation/fixture/' + item.dataset.fixtureId;
    //             iframe.onload = function() {
    //                 iframe.contentDocument.querySelector('#history-back').onclick = function() {
    //                     iframe.contentWindow.history.back(); 
    //                 }
    //                 iframe.contentDocument.querySelector('#history-forward').onclick = function() {
    //                     iframe.contentWindow.history.forward(); 
    //                 }
    //             }
    //         });
    //     });
    // }

    $('#history-back').click(function() {
        window.history.back(); 
    });

    $('#history-forward').click(function() {
        window.history.forward(); 
    });

    $('#player-game-table .clickable-row').click(function() {
        document.location.href = '/simulation/fixture/' + this.dataset.fixtureId;
    })
})