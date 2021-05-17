const canvas = document.getElementById('football-pitch');
const ctx = canvas.getContext('2d');
const image = document.getElementById('football-pitch-image');

ctx.drawImage(image, 0, 0, 362, 500);

const centerX = canvas.width / 32 * 12;
const centerY = canvas.height / 32 * 7;
const radius = 8;

ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
ctx.fillStyle = 'red';
ctx.fill();
ctx.lineWidth = 2;
ctx.strokeStyle = '#000000';
ctx.stroke();