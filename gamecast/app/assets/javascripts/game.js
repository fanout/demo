var connection = new FO.Connection(gc.FANOUT_HOST);
var detailChannel = connection.Channel(gc.CHANNELS.DETAIL);
var scoreChannel = connection.Channel(gc.CHANNELS.SCORE);

detailChannel.on('data', gc.handleDetailedData);
scoreChannel.on('data', gc.handleScoreData);
