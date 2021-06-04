$(document).ready(function() {
    $('#load-development-graph').click(function() {
        $(this).find('#text').hide();
        $(this).find('#spinner').show();
        let playerId = $(this).data('playerId');
        let img = document.createElement('img');
        img.id = 'player-development-graph-image';
        img.src = `/simulation/player/${playerId}/development-graph`;
        $(img).on('load', function() {
            let container = document.getElementById('development-graph-container');
            container.innerHTML = '';
            container.appendChild(img);
        });
    });
});