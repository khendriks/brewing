var start = $('#start').text();
var duration = $('#duration').text();
var finish = $('#finish').text();
var progressbar = $('#progressbar');
var alarm = document.getElementById('alarm');
var intervalId;
var red = false;

if (start && duration) {
    if (!finish || /^\s*$/.test(finish)) {
        update_timer();
        intervalId = setInterval(update_timer, 500);
    }
}

function update_timer() {
    var now = new Date();
    var start_date = new Date(0);
    start_date.setUTCSeconds(start);

    var spend_seconds = Math.round((now - start_date)/1000);
    var percentage = Math.round((spend_seconds / duration)*10000)/100;

    if (percentage < 0){
        percentage = 0;
        progressbar.css('width', percentage + '%').attr('aria-valuenow', percentage).text(percentage + '%');
    } else if (percentage > 100){
        percentage = 100;
        progressbar.css('width', percentage + '%').attr('aria-valuenow', percentage).text(percentage + '%');
        progressbar.removeClass('progress-bar-animated').removeClass('progress-bar-striped');
        progressbar.removeClass('bg-success');
        alarm.play();
        if(!red){
            progressbar.addClass('bg-danger').removeClass('bg-warning');
            red = true;
        }else{
            progressbar.addClass('bg-warning').removeClass('bg-danger');
            red = false;
        }
    }
    progressbar.css('width', percentage + '%').attr('aria-valuenow', percentage).text(percentage + '%');
}


