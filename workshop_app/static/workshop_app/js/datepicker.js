//ToolTip popup function on-hover
$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        placement: 'top',
        trigger: 'hover'
    });

    $('[data-toggle="popinfo"]').popover({
        placement: 'top',
        trigger: 'hover'
    });
});

// Change date modal
function changeDate(date) {
    let previous_date = new Date(date);
    let dateToday = new Date();
    let upto = new Date();

    previous_date.setDate(previous_date.getDate() + 1);
    upto.setFullYear(dateToday.getFullYear() + 1);

    let counter = date.split(" ");
    const id = counter.slice(-1).pop();
    if (date[0] === 'P') {
        counter = '.pDate' + id
        $(counter).datepicker({
            changeMonth: true,
            changeYear: true,
            minDate: dateToday,
            maxDate: upto,
            dateFormat: "yy-mm-dd",
        });
        $(".ui-dialog-content").dialog("close");
        $('.myDialogP' + id).dialog();

    } else {
        counter = '.rDate' + id;
        $(counter).datepicker({
            changeMonth: true,
            changeYear: true,
            minDate: dateToday,
            maxDate: upto,
            dateFormat: "yy-mm-dd",
        });
        $(".ui-dialog-content").dialog("close");
        $('.myDialogR' + id).dialog();

    }
};