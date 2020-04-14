$(document).ready(function() {
  var socket = io();

  socket.on('connect', function() {
    socket.emit('my_event', {data: 'I\'m connected!'});
  });

  socket.on('my_response', function(msg, cb) {
    $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
    if (cb)
      cb();
  });

  $(function(){
    $('#wort-pump-toggle').click(function() {
      togglePump($(this), 'wort');
    });
    $('#water-pump-toggle').click(function() {
      togglePump($(this), 'water');
    });

    $('#boil-toggle').click(function() {
      toggleElement($(this), 'boil');
    });
    $('#hlt-toggle').click(function() {
      toggleElement($(this), 'hlt');
    });

    $('#boil-target').on('input', function() {
      setTargetTemp($(this).val(), 'boil');
    });
    $('#hlt-target').on('input', function() {
      setTargetTemp($(this).val(), 'hlt');
    });

    $('#shutdown').click(function() {
      socket.emit('shutdown');
      return false;
    });
  });

  function setTargetTemp(temp, elementName) {
    socket.emit('set_target_temp', { 'elementName': elementName, 'temp': temp});
    return false;
  }

  function toggleElement(el, elementName) {
    toggleButton(el);
    socket.emit('toggle_element', elementName);
    return false;
  }

  function togglePump(el, pumpName) {
    toggleButton(el);
    socket.emit('toggle_pump', pumpName);
    return false;
  }

  function toggleButton(el) {
    el.toggleClass('btn-on');
    if (el.hasClass('btn-on')) {
      el.html('On');
    } else {
      el.html('Off');
    }
  }
});
