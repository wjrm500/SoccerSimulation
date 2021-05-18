const canvas = document.getElementById('football-pitch');
const ctx = canvas.getContext('2d');
const image = document.getElementById('football-pitch-image');

ctx.drawImage(image, 0, 0, 362, 500);

// const formations = {
//     '3-4-1-2':  [
//         {x: 8, y: 25},
//         {x: 16, y: 25},
//         {x: 24, y: 25},
//         {x: 4, y: 19},
//         {x: 12, y: 19},
//         {x: 20, y: 19},
//         {x: 28, y: 19},
//         {x: 16, y: 13},
//         {x: 12, y: 7},
//         {x: 20, y: 7},
//     ],
//     '3-4-2-1': [
//         {x: 8, y: 25},
//         {x: 16, y: 25},
//         {x: 24, y: 25},
//         {x: 4, y: 19},
//         {x: 12, y: 19},
//         {x: 20, y: 19},
//         {x: 28, y: 19},
//         {x: 12, y: 13},
//         {x: 20, y: 13},
//         {x: 16, y: 7},
//     ],
//     '3-4-3': [
//         {x: 8, y: 25},
//         {x: 16, y: 25},
//         {x: 24, y: 25},
//         {x: 4, y: 16},
//         {x: 12, y: 16},
//         {x: 20, y: 16},
//         {x: 28, y: 16},
//         {x: 8, y: 7},
//         {x: 16, y: 7},
//         {x: 24, y: 7}
//     ],
//     '3-5-1-1': [
//         {x: 8, y: 25},
//         {x: 16, y: 25},
//         {x: 24, y: 25},
//         {x: 4, y: 19},
//         {x: 10, y: 19},
//         {x: 16, y: 19},
//         {x: 22, y: 19},
//         {x: 28, y: 19},
//         {x: 16, y: 13},
//         {x: 16, y: 7}
//     ],
//     '3-5-2': [
//         {x: 8, y: 25},
//         {x: 16, y: 25},
//         {x: 24, y: 25},
//         {x: 4, y: 16},
//         {x: 10, y: 16},
//         {x: 16, y: 16},
//         {x: 22, y: 16},
//         {x: 28, y: 16},
//         {x: 12, y: 7},
//         {x: 20, y: 7}
//     ],
//     '4-4-2': [
//         {x: 4, y: 25},
//         {x: 12, y: 25},
//         {x: 20, y: 25},
//         {x: 28, y: 25},
//         {x: 4, y: 16},
//         {x: 12, y: 16},
//         {x: 20, y: 16},
//         {x: 28, y: 16},
//         {x: 12, y: 7},
//         {x: 20, y: 7}
//     ]
// };

function calculateCoords(formation, customXCoords, customYCoords) {
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
        if (customYCoords && i in customYCoords && customYCoords[i].length === numInGroup) {
            var yArr = [];
            for (let j of customYCoords[i]) {
                yArr.push(j);
            }
        }
        if (i === 0) {
            y = maxY;
        } else if (i === (numGroups - 1)) {
            y = minY;
        } else {
            y = maxY - ((maxY - minY) / (numGroups - 1) * i)
        }
        if (customXCoords && i in customXCoords && customXCoords[i].length === numInGroup) {
            for (let j = 0; j < numInGroup; j++) {
                let customXCoord = customXCoords[i][j];
                if (customYCoords && i in customYCoords && customYCoords[i].length === numInGroup) {
                    y = yArr[j];
                }
                res.push({x: customXCoord, y: y});
            }
        } else {
            let idealGap = Math.min(8, (maxX - minX) / (numInGroup - 1));
            let midX = (minX +  maxX) / 2;
            let distFromCenter = (idealGap * (numInGroup - 1)) / 2
            let realMinX = midX - distFromCenter;
            let x = realMinX;
            for (let j = 0; j < numInGroup; j++) {
                if (customYCoords && i in customYCoords && customYCoords[i].length === numInGroup) {
                    y = yArr[j];
                }
                res.push({x: x, y: y});
                x += idealGap;
            }
        }   
    }
    return res;
}

let coords = calculateCoords(
    '3-5-2',
    null,
    {
        1: [14, 17, 18, 17, 14]
    }
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
