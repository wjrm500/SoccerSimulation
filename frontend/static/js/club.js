function calculateCoordsFromFormation(formation, customXCoords, customYCoords) {
    // For custom co-ordinates, pass an object where the key represents the index of the formation group, and the value is an array representing the offset for each circle in that group
    const minY = 7;
    const maxY = 25;
    const minX = 4;
    const maxX = 28;
    let res = [];
    let formationArr = formation.split('-');
    let numGroups = formationArr.length;
    for (let i = 0; i < numGroups; i++) {
        let numInGroup = parseInt(formationArr[i]);
        let y;
        if (i === 0) {
            y = maxY;
        } else if (i === (numGroups - 1)) {
            y = minY;
        } else {
            y = maxY - ((maxY - minY) / (numGroups - 1) * i)
        }
        let idealGap = Math.min(8, (maxX - minX) / (numInGroup - 1));
        let midX = (minX +  maxX) / 2;
        let distFromCenter = (idealGap * (numInGroup - 1)) / 2
        let realMinX = midX - distFromCenter;
        let x = realMinX;
        let rollingX = x;
        let rollingY = y;
        for (let j = 0; j < numInGroup; j++) {
            x = rollingX;
            y = rollingY;
            if (customXCoords && i in customXCoords && customXCoords[i].length === numInGroup) {
                x += customXCoords[i][j] ?? 0;
            }
            if (customYCoords && i in customYCoords && customYCoords[i].length === numInGroup) {
                y -= customYCoords[i][j] ?? 0;
            }
            res.push({x: x, y: y});
            rollingX += idealGap;
        }
    }
    return res;
}

function drawPlayer(player, centerX, centerY, radius, hoverState) {
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
    let val = player.rating;
    let hue = Math.floor((100 - val) * 120 / 100);
    let saturation = Math.abs(val - 50) / 50 * 100;
    if (hoverState) {
        ctx.fillStyle = `hsl(${hue}, ${saturation}%, 20%)`;
    } else {
        ctx.fillStyle = `hsl(${hue}, ${saturation}%, 50%)`;
    }
    ctx.fill();
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#000000';
    ctx.stroke();
    ctx.fillStyle = 'white';
    ctx.font = hoverState ? 'normal 900 12px Arial, sans-serif' : '12px Arial, sans-serif';
    ctx.fillText(parseInt(player.rating), centerX, centerY);
    ctx.fillStyle = 'black';
    ctx.fillText(player.name, centerX, centerY + 30);
}

var playerIdHovered = 0;

function plotCoords(zip, playerIdHovered) {
    ctx.font = '11px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let hoverPlaces = [];
    for (let zipItem of zip) {
        const centerX = ctx.canvas.width / 32 * zipItem.coords.x;
        const centerY = ctx.canvas.height / 32 * zipItem.coords.y;
        const radius = ctx.canvas.width / 25 * (1 + (zipItem.player.adjustedRating * 2));
        hoverPlaces.push({
            playerId: zipItem.player.id,
            centerX,
            centerY,
            radius
        });
        hoverState = playerIdHovered === zipItem.player.id;
        drawPlayer(zipItem.player, centerX, centerY, radius, hoverState);
    }
    $(canvas).unbind();
    $(canvas).mousemove(function(evt) {
        const {x, y} = getMousePos(evt);
        canvas.style.cursor = 'auto';
        for (let hoverPlace of hoverPlaces) {
            let {playerId, centerX, centerY, radius} = hoverPlace;
            if (Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)) < radius) {
                canvas.style.cursor = 'pointer';
                if (playerId !== playerIdHovered) {
                    playerIdHovered = playerId;
                    drawPitch(playerIdHovered);
                    let playerRow = $('#club-player-performance-table tr[data-player-id=' + playerId + ']');
                    playerRow.addClass('hovered');
                    playerRow.find('.player-row-bottom').css('color', 'white');
                    return;
                }
            } else {
                if (playerIdHovered !== 0) {
                    playerIdHovered = 0;
                    $('#club-player-performance-table tr').each(function() {
                        $(this).removeClass('hovered');
                        $(this).find('.player-row-bottom').css('color', 'grey')
                    })
                    drawPitch();
                }
            }
        }
    });
    $(canvas).click(function(evt) {
        const {x, y} = getMousePos(evt);
        for (let hoverPlace of hoverPlaces) {
            let {playerId, centerX, centerY, radius} = hoverPlace;
            if (Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)) < radius) {
                let url = '/simulation/player/' + playerId;
                if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
                    parent.iframeHistory.pop();
                    parent.iframeHistory.push(url);
                } else {
                    parent.iframeHistory.push(url);
                }
                parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
                document.location.href = url;
            }
        }
    });
}

const positions = {
    WF: {
        bgColor: {r: 255, g: 100, b: 100},
        size: {h: 10, w: 10},
        startPositions: [{x: 0, y: 0}, {x: 22, y:0}]
    },
    CF: {
        bgColor: {r: 255, g: 50, b: 50},
        size: {h: 10, w: 12},
        startPositions: [{x: 10, y: 0}]
    },
    WM: {
        bgColor: {r: 189, g: 183, b: 107},
        size: {h: 8, w: 8},
        startPositions: [{x: 0, y: 10}, {x: 24, y: 10}]
    },
    COM: {
        bgColor: {r: 255, g: 255, b: 0},
        size: {h: 4, w: 16},
        startPositions: [{x: 8, y: 10}]
    },
    CM: {
        bgColor: {r: 240, g: 230, b: 140},
        size: {h: 4, w: 16},
        startPositions: [{x: 8, y: 14}]
    },
    CDM: {
        bgColor: {r: 255, g: 215, b: 0},
        size: {h: 4, w: 16},
        startPositions: [{x: 8, y: 18}]
    },
    WB: {
        bgColor: {r: 25, g: 25, b: 112},
        size: {h: 4, w: 8},
        startPositions: [{x: 0, y: 18}, {x: 24, y: 18}]
    },
    FB: {
        bgColor: {r: 30, g: 144, b: 255},
        size: {h: 10, w: 6},
        startPositions: [{x: 0, y: 22}, {x: 26, y: 22}]
    },
    CB: {
        bgColor: {r: 0, g: 0, b: 255},
        size: {h: 10, w: 20},
        startPositions: [{x: 6, y: 22}]
    },
}

function createPositionRects(position) {
    ctx.fillStyle = `rgba(${position.bgColor.r}, ${position.bgColor.g}, ${position.bgColor.b}, 0.5)`;
    for (let startPosition of position.startPositions) {
        ctx.fillRect(
            canvas.width / 32 * startPosition.x,
            canvas.height / 32 * startPosition.y,
            canvas.width / 32 * position.size.w,
            canvas.height / 32 * position.size.h
        );
    }
}

function getPositionFromCoords(coords) {
    let x = coords.x;
    let y = coords.y;
    let prospectives = [];
    for (let key in positions) {
        let value = positions[key];
        for (let startPosition of value.startPositions) {
            let startX = startPosition.x;
            let endX = startX + value.size.w;
            let startY = startPosition.y;
            let endY = startY + value.size.h;
            if (x >= startX && x <= endX && y >= startY && y <= endY) {
                prospectives.push(key);
            }
        }
    }
    const priority = ['WF', 'CF', 'CM', 'CDM', 'WM', 'COM', 'WB', 'FB', 'CB'];
    let selected = prospectives.map(x => [x, priority.indexOf(x)]).reduce((prev, cur) => (prev[1] < cur[1]) ? prev : cur)[0];
    return selected;
}

function getMousePos(evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
        y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
    };
}

function drawPitch(playerIdHovered) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, (rect.height - 10) / 500 * 362, (rect.height - 10));
    let coords = calculateCoordsFromFormation(canvas.dataset.formation);//, null, {0: [3, 0, 0, 3], 2: [0, -3, -3, 0]});
    let players = JSON.parse(canvas.dataset.players);
    let playerPositions = {};
    for (let player of players) {
        if (!(player.position in playerPositions)) {
            playerPositions[player.position] = [];
        }
        playerPositions[player.position].push(player);
    }
    let playerData = coords.map(crd => getPositionFromCoords(crd)).map(pos => playerPositions[pos].shift());
    let zip = [];
    for (let i = 0; i < players.length; i++) {
        zip.push({
            coords: coords[i],
            player: playerData[i]
        });
    }
    plotCoords(zip, playerIdHovered);
}

$(document).ready(function() {
    canvas = document.getElementById('football-pitch');
    rect = canvas.parentNode.getBoundingClientRect();
    canvas.width = (rect.height - 10) / 500 * 362;
    canvas.height = (rect.height - 10);
    ctx = canvas.getContext('2d');
    image = document.getElementById('football-pitch-image');
    drawPitch();
    $('#club-player-performance-table .clickable-row').click(function() {
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

    $('#club-player-performance-table th').hover(
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

    $('#club-player-performance-table th:not(:nth-child(1))').click(function() {
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
        $('#club-player-performance-table tr:not(:nth-child(1))').each(function() {
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
            let tr = $('#club-player-performance-table tr:eq(' + (i + 1) + ')');
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

    $('#club-player-performance-table tr:not(:first-child)').mouseenter(function() {
        let playerId = $(this).data('playerId');
        drawPitch(playerId);
    });

    $('.club-score-container').each(function() {
        let result = $(this).data('result');
        let resultColorMapping = {
            win: 'lightgreen',
            draw: 'lemonchiffon',
            loss: 'lightpink'
        }
        $(this).css('backgroundColor', resultColorMapping[result]);
    });

    $('#club-results .clickable-row').click(function() {
        let fixtureId = $(this).data('fixtureId');
        let url = '/simulation/fixture/' + fixtureId;
        if (parent.iframeHistoryPointer !== (parent.iframeHistory.length - 1)) {
            parent.iframeHistory.pop();
            parent.iframeHistory.push(url);
        } else {
            parent.iframeHistory.push(url);
        }
        parent.iframeHistoryPointer = parent.iframeHistory.length - 1;
        document.location.href = url;
    });

    $('.home-away-button').click(function() {
        let homeAway = $(this).data('homeAway');
        $('#club-results tr').each(function() {
            $(this).css('display', '');
        });
        $(this).addClass('clicked');
        $('.home-away-button').not('#' + $(this).attr('id')).each((x, y) => $(y).removeClass('clicked'));
        if (homeAway === 'home') {
            $('#club-results tr').each(function() {
                if ($(this).data('atHome') === 'False') {
                    $(this).css('display', 'none');
                }
            });
        } else if (homeAway === 'away') {
            $('#club-results tr').each(function() {
                if ($(this).data('atHome') === 'True') {
                    $(this).css('display', 'none');
                }
            });
        }
    });
});