const canvas = document.getElementById('football-pitch');
const ctx = canvas.getContext('2d');
const image = document.getElementById('football-pitch-image');
ctx.drawImage(image, 0, 0, 362, 500);

function calculateCoords(formation, customXCoords, customYCoords) {
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

let coords = calculateCoords(
    '3-5-3-3',
    // {
    //     0: [2, null, -2],
    //     1: [null, 2, null, -2, null]
    // },
    // {
    //     1: [5, -1, 2, -1, 5],
    //     2: [1]
    // }
);

for (let position of coords) {
    console.log(position);
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


const positions = {
    WF: {
        bgColor: {r: 200, g: 200, b: 150},
        size: {h: 10, w: 10},
        startPositions: [{x: 0, y: 0}, {x: 22, y:0}]
    }
}
// ctx.fillStyle = 'rgba(200, 200, 150, 0.5)';
// ctx.fillRect(canvas.width / 32 * 0, canvas.height / 32 * 0, canvas.width / 32 * 10, canvas.height / 32 * 10);
// ctx.fillRect(canvas.width / 32 * 22, canvas.height / 32 * 0, canvas.width / 32 * 10, canvas.height / 32 * 10);

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

createPositionRects(positions['WF']);