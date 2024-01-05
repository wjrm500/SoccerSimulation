$(document).ready(function() {
    let playerId = $('#player-radar-image').data('playerId');
    let originalSrc = basePath + `/simulation/player/${playerId}/radar`;
    let newSrc = getUrlWithParams(originalSrc);
    $('#player-radar-image').prop('src', newSrc);

    $('#load-development-graph').click(function() {
        $(this).find('#text').hide();
        $(this).find('#spinner').show();
        let playerId = $(this).data('playerId');
        let img = document.createElement('img');
        img.id = 'player-development-graph-image';
        let imgSrc = basePath + `/simulation/player/${playerId}/development-graph`;
        imgSrc = getUrlWithParams(imgSrc);
        img.src = imgSrc;
        $(img).on('load', function() {
            let container = document.getElementById('development-graph-container');
            container.innerHTML = '';
            container.appendChild(img);
        });
    });
});