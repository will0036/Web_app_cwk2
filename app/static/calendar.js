$(document).ready(function () {
    var bookedDates = JSON.parse(document.getElementById('bookedDates').innerText);
    console.log(bookedDates);
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next Today',
            center: 'title',
            right: 'Month,agendaWeek,agendaDay',
        },
        defaultView: 'month',
        editable: false, 
        events: bookedDates, 
        eventColor: '#FF0000', 
        eventTextColor: '#FFFFFF', 
        eventRender: function (event, element) {
            element.find('.fc-title').html('Booked'); 
        },
    });
});