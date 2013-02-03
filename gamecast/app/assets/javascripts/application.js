// This is a manifest file that'll be compiled into application.js, which will include all the files
// listed below.
//
// Any JavaScript/Coffee file within this directory, lib/assets/javascripts, vendor/assets/javascripts,
// or vendor/assets/javascripts of plugins, if any, can be referenced here using a relative path.
//
// It's not advisable to add code directly here, but if you do, it'll appear at the bottom of the
// the compiled file.
//
// WARNING: THE FIRST BLANK LINE MARKS THE END OF WHAT'S TO BE PROCESSED, ANY BLANK LINE SHOULD
// GO AFTER THE REQUIRES BELOW.
//
//= require jquery
//= require jquery_ujs

var gc = {};

/**
 * Channel names.
 * @enum {string}
 */
gc.CHANNELS = {
    DETAIL: 'gamecast-detail',
    SCORE: 'gamecast-score'
};

/** @const {string} **/
gc.FANOUT_HOST = 'demo.fanout.io';

/**
 * Handle the score data response from fanout.io. Update the DOM to
 * show the score changing.
 * @param {Object} data The response data.
 */
gc.handleScoreData = function(data) {
    $('#' + data.team).find('.gc-score').html(data.score);
};

/**
 * Handle the detailed data response from fanout.io. Update the DOM to
 * show the detailed play-by-play.
 * @param {Object} data The response data.
 */
gc.handleDetailedData = function(data) {
    throw 'Not implemented';
};

/**
 * Increase the score for a specific team. Shows the score update in the DOM
 * and sends a request to the server.
 */
gc.increaseScore = function() {
    var scoreEl = $(this).siblings('.gc-score');
    var score = parseInt(scoreEl.html(), 10);
    score++;
    scoreEl.html(score);

    // Send the score increase.
    var team = scoreEl.parent().attr('id');
    jQuery.post('/admin/create.json', {
        team: team,
        score: score
    });
};
