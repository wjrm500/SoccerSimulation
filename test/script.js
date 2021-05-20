const canvas = document.getElementById('football-pitch');
const ctx = canvas.getContext('2d');
const image = document.getElementById('football-pitch-image');
ctx.drawImage(image, 0, 0, 362, 500);

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

function plotCoords(coords) {
    for (let position of coords) {
        const centerX = canvas.width / 32 * position.x;
        const centerY = canvas.height / 32 * position.y;
        const radius = 8;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
        ctx.fillStyle = 'red';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#000000';
        ctx.stroke();
    }
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

let coords = calculateCoordsFromFormation('4-1-4-1', null, {2: [null, -3, -3, null]});
plotCoords(coords);
console.log(coords.map(i => getPositionFromCoords(i)))