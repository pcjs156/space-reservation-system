const bookedCells = document.getElementsByClassName('booked');
const notBookedCells = document.getElementsByClassName('not-booked');

for (let cell of bookedCells) {
    cell.addEventListener('mouseover', (e) => {
        e.target.style.border = '2px solid #ff0000';
    });

    cell.addEventListener('mouseout', (e) => {
        e.target.style.border = null;
    })

    cell.addEventListener('click', (e) => {
        location.replace(e.target.getAttribute('detail-link'));
    })
}

for (let cell of notBookedCells) {
    cell.addEventListener('mouseover', (e) => {
        e.target.style.border = '2px solid #00ff00';
    });

    cell.addEventListener('mouseout', (e) => {
        e.target.style.border = null;
    })

    cell.addEventListener('click', (e) => {
        location.replace(e.target.getAttribute('detail-link'));
    })
}